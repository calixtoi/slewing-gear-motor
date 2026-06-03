import json
import os
import tempfile
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import DrivetrainForm, SaveCalculationForm, DatasheetUploadForm, MotorSpecsForm, TextDatasheetForm
from .engine import (
    drivetrain_sizing,
    check_physical_compliance,
    size_known_motor,
    CRANE_PARAMS,
    CRANE_STANDARD_PF,
    CRANE_PF_XXL,
    KNOWN_MOTORS,
    PHYSICAL_REQUIREMENTS,
    TORQUE_CONSTANT,
    ETA_GB_ASSUMED,
    SAFETY_FACTOR,
)
from .models import MotorCalculation
from .pdf_parser import (
    parse_datasheet, parse_text, check_compliance, specs_to_form_initial,
    extract_motor_params, extract_motor_params_from_pdf, MOTOR_PARAM_LABELS,
)

FORMULAS = {
    'f_CF':    r'CF = i_{\text{slew}} \times \eta_{\text{slew}}',
    'f1':      r'T_{GM,start,MAX} = \dfrac{T_{crane,lim}}{CF}',
    'f2':      r'T_{GM,nom,req} = \dfrac{T_{crane,nom}}{CF}',
    'f8':      r'M_{n,motor} = \dfrac{P_{kW} \times 9550}{n_{motor}}',
    'f8_note': r'9550 \approx \dfrac{60{,}000}{2\pi} \text{ — converts kW\cdotRPM to Nm}',
    'f4':      r'i_{gb} = \dfrac{n_{motor}}{n_{GM,out}}',
    'f4_inv':  r'n_{GM,out} = \dfrac{n_{motor}}{i_{gb}}',
    'f5':      r'n_{crane} = \dfrac{n_{GM,out}}{i_{slew}}',
    'f_MNenn': r'M_{Nenn} = T_{GM,out,nom} \times CF',
    'f_MaMax': r'M_{a,Max} = T_{GM,out,start} \times CF',
    'f_MkMax': r'M_{k,Max} = M_{Nenn} \times \left(\dfrac{M_k}{M_n}\right)',
    'f_MaMn':  r'\left(\dfrac{M_a}{M_n}\right)_{MAX} = \dfrac{T_{GM,start,MAX}}{T_{GM,out,nom}}',
    'fg3':     r'M_{gear,req} = M_{2,nom} \times 1.34',
    'fs_margin': r'\text{margin} = \dfrac{T_{crane,lim} - M_{a,Max}}{T_{crane,lim}} \times 100\%',
}


def _load_datasheet(post_data) -> tuple:
    """Parse optional datasheet_data JSON from POST. Returns (dict|None, str)."""
    raw = post_data.get('datasheet_data', '').strip()
    if raw:
        try:
            return json.loads(raw), raw
        except (json.JSONDecodeError, ValueError):
            pass
    return None, ''


def _spec_fields_from_form(sd: dict) -> dict:
    """Extract all spec_ fields from cleaned form data, returning safe defaults."""
    return {
        'spec_frame_material':    sd.get('spec_frame_material', '') or '',
        'spec_output_flange':     sd.get('spec_output_flange', '') or '',
        'spec_shaft':             sd.get('spec_shaft', '') or '',
        'spec_cooling_method':    sd.get('spec_cooling_method', '') or '',
        'spec_ip_rating':         sd.get('spec_ip_rating', '') or '',
        'spec_ambient_temp':      sd.get('spec_ambient_temp', '') or '',
        'spec_coating':           sd.get('spec_coating', '') or '',
        'spec_top_color':         sd.get('spec_top_color', '') or '',
        'spec_heater':            sd.get('spec_heater', '') or '',
        'spec_insulation_class':  sd.get('spec_insulation_class', '') or '',
        'spec_duty_cycle':        sd.get('spec_duty_cycle', '') or '',
        'spec_painting':          sd.get('spec_painting', '') or '',
        'spec_motor_certificate': sd.get('spec_motor_certificate', '') or '',
        'spec_weight_kg':         sd.get('spec_weight_kg'),
        'spec_efficiency_class':  sd.get('spec_efficiency_class', '') or '',
        'spec_voltage':           sd.get('spec_voltage', '') or '',
    }


def _effective_gearbox_speed(d):
    """Return gearbox output speed: direct input wins; otherwise compute from gear ratio."""
    if d.get('gearbox_output_speed'):
        return d['gearbox_output_speed']
    if d.get('gear_ratio') and d.get('motor_speed'):
        return d['motor_speed'] / d['gear_ratio']
    return None


def _crane_context():
    ctx = {}
    for ctype, params in CRANE_PARAMS.items():
        ctx[f'params_{ctype}'] = params
    ctx['crane_standard_pf'] = CRANE_STANDARD_PF
    ctx['crane_pf_xxl']      = CRANE_PF_XXL
    return ctx


def calculator(request):
    result = None
    phys_checks = None
    datasheet_json = ''
    form = DrivetrainForm()
    specs_form = MotorSpecsForm()
    save_form = SaveCalculationForm()
    error = None

    if request.method == 'POST':
        form = DrivetrainForm(request.POST)
        specs_form = MotorSpecsForm(request.POST)
        datasheet_json = request.POST.get('datasheet_data', '')

        if form.is_valid():
            d = form.cleaned_data

            try:
                # Determine which interface is being used (old or new)
                using_new_interface = any([d.get('motor_power'), d.get('supplier_output_torque'), d.get('supplier_starting_torque')])

                if using_new_interface:
                    # New interface
                    crane_type      = d.get('crane_type', CRANE_STANDARD_PF)
                    motor_power_kw  = float(d.get('motor_power') or 0)
                    motor_speed_rpm = float(d.get('motor_speed_new') or 0)
                    gm_out_nom_nm   = float(d.get('supplier_output_torque') or 0)
                    gm_out_start_nm = float(d.get('supplier_starting_torque') or 0)
                    Mk_Mn           = float(d.get('mk_mn_ratio') or 3.40)

                    gm_out_speed_rpm = None
                    if d.get('gearbox_output_speed'):
                        gm_out_speed_rpm = float(d['gearbox_output_speed'])
                    elif d.get('gear_ratio') and motor_speed_rpm:
                        gm_out_speed_rpm = motor_speed_rpm / float(d['gear_ratio'])

                    if not gm_out_speed_rpm or not gm_out_nom_nm or not gm_out_start_nm or not motor_power_kw:
                        error = 'Please provide all required fields: Motor Power, Motor Speed, Geared Motor Output Torque, Starting Torque, and either Output Speed or Gear Ratio.'
                    else:
                        i_gb = float(d['gear_ratio']) if d.get('gear_ratio') else None
                        result = drivetrain_sizing(
                            crane_type=crane_type,
                            motor_power_kw=motor_power_kw,
                            motor_speed_rpm=motor_speed_rpm,
                            gm_out_speed_rpm=gm_out_speed_rpm,
                            gm_out_nom_nm=gm_out_nom_nm,
                            gm_out_start_nm=gm_out_start_nm,
                            Mk_Mn=Mk_Mn,
                            i_gb=i_gb,
                        )
                        if specs_form.is_valid():
                            phys_checks = check_physical_compliance(specs_form.cleaned_data)
                else:
                    # Old interface - for backward compatibility with existing templates
                    # TODO: Map old fields to new engine when template is updated
                    error = 'Please use the new form interface with Motor Power, Motor Speed, Output Torque, and Starting Torque fields.'

            except (ValueError, TypeError) as e:
                error = f'Invalid input: {str(e)}'

    elif request.GET:
        initial = {}
        for key in ['crane_type','motor_power','motor_speed_new','gear_ratio',
                    'gearbox_output_speed','supplier_output_torque','supplier_starting_torque','mk_mn_ratio']:
            if key in request.GET:
                initial[key] = request.GET[key]
        if initial:
            form = DrivetrainForm(initial=initial)

    context = {
        'form': form, 'specs_form': specs_form, 'save_form': save_form,
        'result': result, 'phys_checks': phys_checks,
        'phys_requirements': PHYSICAL_REQUIREMENTS,
        'datasheet_data': datasheet_json, 'error': error,
        'known_motors': KNOWN_MOTORS,
        **FORMULAS, **_crane_context(),
    }
    return render(request, 'calculator/index.html', context)


def index(request):
    return calculator(request)


def requirements(request):
    reference = {k: size_known_motor(k) for k in KNOWN_MOTORS}
    req_tables = {}
    for ctype, params in CRANE_PARAMS.items():
        CF             = params['i_slew'] * params['eta_slew']
        req_tables[ctype] = {
            'params':          params,
            'CF':              CF,
            'T_gm_start_MAX':  params['T_crane_lim'] / CF,
            'T_gm_nom_req':    params['T_crane_nom']  / CF,
            'n_gm_min':        params['n_crane_min'] * params['i_slew'],
            'n_gm_max':        params['n_crane_max'] * params['i_slew'],
            'Ma_Mn_MAX':       (params['T_crane_lim'] / CF) / (params['T_crane_nom'] / CF),
        }
    context = {
        'req_tables': req_tables, 'reference': reference,
        'known_motors': KNOWN_MOTORS, 'phys_requirements': PHYSICAL_REQUIREMENTS,
        **FORMULAS, **_crane_context(),
    }
    return render(request, 'calculator/requirements.html', context)


@csrf_exempt
def calculate_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    crane_type        = data.get('crane_type', CRANE_STANDARD_PF)
    motor_power_kw    = float(data.get('motor_power_kw', 0))
    motor_speed_rpm   = float(data.get('motor_speed_rpm', 1415))
    gm_out_speed_rpm  = float(data.get('gm_out_speed_rpm', 0))
    gm_out_nom_nm     = float(data.get('gm_out_nom_nm', 0))
    gm_out_start_nm   = float(data.get('gm_out_start_nm', 0))
    Mk_Mn             = float(data.get('Mk_Mn', 3.40))
    gm_out_pullup_nm  = float(data['gm_out_pullup_nm']) if data.get('gm_out_pullup_nm') else None
    i_gb              = float(data['i_gb']) if data.get('i_gb') else None

    if not all([gm_out_speed_rpm, gm_out_nom_nm, gm_out_start_nm]):
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    if crane_type not in CRANE_PARAMS:
        return JsonResponse({'error': f'Unknown crane_type: {crane_type}'}, status=400)

    r = drivetrain_sizing(
        crane_type=crane_type, motor_power_kw=motor_power_kw,
        motor_speed_rpm=motor_speed_rpm, gm_out_speed_rpm=gm_out_speed_rpm,
        gm_out_nom_nm=gm_out_nom_nm, gm_out_start_nm=gm_out_start_nm,
        Mk_Mn=Mk_Mn, i_gb=i_gb, gm_out_pullup_nm=gm_out_pullup_nm,
    )
    return JsonResponse({
        'crane_label': r.crane_label, 'CF': round(r.CF, 2),
        'i_slew': r.i_slew, 'eta_slew': r.eta_slew,
        'T_crane_lim': r.T_crane_lim, 'T_gm_start_MAX': round(r.T_gm_start_MAX, 1),
        'T_gm_nom_required': round(r.T_gm_nom_required, 1),
        'Ma_Mn_MAX': round(r.Ma_Mn_MAX, 2), 'n_gm_min': r.n_gm_min, 'n_gm_max': r.n_gm_max,
        'Mn_motor': round(r.Mn_motor, 2), 'i_gb': round(r.i_gb, 2),
        'n_crane': round(r.n_crane, 4), 'M_Nenn': round(r.M_Nenn, 0),
        'Ma_Max': round(r.Ma_Max, 0), 'Mk_Max': round(r.Mk_Max, 0),
        'Ma_Mn_actual': round(r.Ma_Mn_actual, 2),
        'nom_utilisation_pct': round(r.nom_utilisation_pct, 1),
        'start_utilisation_pct': round(r.start_utilisation_pct, 1),
        'overall_status': r.overall_status, 'checks': r.checks,
        'torque_curve': {
            'points': [
                {'speed_pct': 0,   'label': 'Locked rotor (startup)',  'torque_nm': round(r.gm_out_locked_rotor_nm, 1),  'is_limit': r.gm_out_locked_rotor_nm > r.T_gm_start_MAX},
                {'speed_pct': 40,  'label': 'Pull-up torque',          'torque_nm': round(r.gm_out_pullup_nm, 1),        'is_limit': False},
                {'speed_pct': 80,  'label': 'Breakdown torque (Mk)',   'torque_nm': round(r.gm_out_breakdown_nm, 1),     'is_limit': False},
                {'speed_pct': 100, 'label': 'Rated torque (nominal)',  'torque_nm': round(r.gm_out_nom_nm, 1),           'is_limit': False},
            ],
            'limit_line': round(r.T_gm_start_MAX, 1),
            'limit_label': f'Max permissible starting torque ({r.T_gm_start_MAX:,.0f} Nm)',
            'rated_speed_rpm': round(r.motor_speed_rpm, 0),
            'gm_out_speed_rpm': round(r.gm_out_speed_rpm, 1),
        },
    })


def _datasheet_result(request, datasheet, specs, crane_type, motor_params):
    """Shared render for the datasheet result page (PDF and text paths)."""
    form_initial = specs_to_form_initial(specs)
    compliance = check_compliance(form_initial)
    found = {k: v for k, v in motor_params.items() if v is not None}
    has_supplier_params = any(k.startswith('supplier_') for k in found)
    param_display = [
        {'label': MOTOR_PARAM_LABELS[k][0], 'value': v, 'unit': MOTOR_PARAM_LABELS[k][1]}
        for k, v in found.items() if k in MOTOR_PARAM_LABELS
    ]
    datasheet_json = json.dumps(datasheet)
    return render(request, 'calculator/datasheet_result.html', {
        'datasheet':          datasheet,
        'datasheet_json':     datasheet_json,
        'compliance':         compliance,
        'form':               DrivetrainForm(initial=found),
        'specs_form':         MotorSpecsForm(initial=form_initial),
        'save_form':          SaveCalculationForm(initial={'crane_type': crane_type}),
        'motor_params':       found,
        'param_display':      param_display,
        'has_supplier_params': has_supplier_params,
        'active_page':        'calculator',
        **FORMULAS,
    })


def upload_datasheet(request):
    if request.method == 'GET':
        return render(request, 'calculator/datasheet_upload.html', {
            'pdf_form':  DatasheetUploadForm(),
            'text_form': TextDatasheetForm(),
            'active_tab': 'pdf',
            'active_page': 'upload',
        })

    source = request.POST.get('source', 'pdf')

    # ── Text path ────────────────────────────────────────────────────────────
    if source == 'text':
        form = TextDatasheetForm(request.POST)
        if not form.is_valid():
            return render(request, 'calculator/datasheet_upload.html', {
                'pdf_form':   DatasheetUploadForm(),
                'text_form':  form,
                'active_tab': 'text',
                'active_page': 'upload',
            })
        text       = form.cleaned_data['text_content']
        supplier   = form.cleaned_data['supplier_name']
        crane_type = form.cleaned_data['crane_type']
        raw_proto  = form.cleaned_data.get('price_prototype')
        raw_series = form.cleaned_data.get('price_series')
        specs        = parse_text(text)
        motor_params = extract_motor_params(text)
        datasheet = {
            'supplier':        supplier,
            'crane_type':      crane_type,
            'price_prototype': float(raw_proto)  if raw_proto  else None,
            'price_series':    float(raw_series) if raw_series else None,
            'specs':           specs,
        }
        return _datasheet_result(request, datasheet, specs, crane_type, motor_params)

    # ── PDF path ─────────────────────────────────────────────────────────────
    form = DatasheetUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, 'calculator/datasheet_upload.html', {
            'pdf_form':   form,
            'text_form':  TextDatasheetForm(),
            'active_tab': 'pdf',
            'active_page': 'upload',
        })

    pdf_file   = request.FILES['pdf_file']
    supplier   = form.cleaned_data['supplier_name']
    crane_type = form.cleaned_data['crane_type']
    raw_proto  = form.cleaned_data.get('price_prototype')
    raw_series = form.cleaned_data.get('price_series')

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
            for chunk in pdf_file.chunks():
                tmp.write(chunk)
        specs        = parse_datasheet(tmp_path)
        motor_params = extract_motor_params_from_pdf(tmp_path)
    except Exception as exc:
        form.add_error('pdf_file', f'Could not read PDF: {exc}')
        return render(request, 'calculator/datasheet_upload.html', {
            'pdf_form':   form,
            'text_form':  TextDatasheetForm(),
            'active_tab': 'pdf',
            'active_page': 'upload',
        })
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    datasheet = {
        'supplier':        supplier,
        'crane_type':      crane_type,
        'price_prototype': float(raw_proto)  if raw_proto  else None,
        'price_series':    float(raw_series) if raw_series else None,
        'specs':           specs,
    }
    return _datasheet_result(request, datasheet, specs, crane_type, motor_params)


def save_calculation(request):
    if request.method != 'POST':
        return redirect('index')

    calc_form  = DrivetrainForm(request.POST)
    save_form  = SaveCalculationForm(request.POST)
    specs_form = MotorSpecsForm(request.POST)

    if calc_form.is_valid() and save_form.is_valid():
        d  = calc_form.cleaned_data
        sd = specs_form.cleaned_data if specs_form.is_valid() else {}
        n_gear_out_eff = _effective_gearbox_speed(d)
        results = drivetrain_sizing(
            crane_torque_max=d['crane_torque_max'],
            crane_torque_nom=d.get('crane_torque_nom'),
            worm_ratio=d['worm_ratio'],
            worm_efficiency=d['worm_efficiency'],
            motor_speed=d['motor_speed'],
            gearbox_output_speed=n_gear_out_eff,
            motor_rated_torque=d['motor_rated_torque'],
            starting_factor=d['starting_factor'],
            bevel_efficiency=d['bevel_efficiency'],
            supplier_motor_power_kw=d.get('supplier_motor_power_kw'),
            supplier_motor_rated_torque=d.get('supplier_motor_rated_torque'),
            supplier_motor_starting_torque=d.get('supplier_motor_starting_torque'),
            supplier_gearbox_rated_torque=d.get('supplier_gearbox_rated_torque'),
            supplier_bevel_ratio=d.get('supplier_bevel_ratio'),
            supplier_worm_ratio=d.get('supplier_worm_ratio'),
        )
        # Prices: prefer save_form fields, fall back to datasheet JSON
        raw_proto  = save_form.cleaned_data.get('price_prototype')
        raw_series = save_form.cleaned_data.get('price_series')
        if not raw_proto or not raw_series:
            ds, _ = _load_datasheet(request.POST)
            if not raw_proto and ds and ds.get('price_prototype'):
                raw_proto  = Decimal(str(ds['price_prototype']))
            if not raw_series and ds and ds.get('price_series'):
                raw_series = Decimal(str(ds['price_series']))
        price_proto  = raw_proto  if raw_proto  else None
        price_series = raw_series if raw_series else None

        spec_data = _spec_fields_from_form(sd)

        MotorCalculation.objects.create(
            supplier_name=save_form.cleaned_data['supplier_name'],
            crane_type=save_form.cleaned_data['crane_type'],
            crane_torque_max=d['crane_torque_max'],
            crane_torque_nom=d.get('crane_torque_nom'),
            worm_ratio=d['worm_ratio'],
            worm_efficiency=d['worm_efficiency'],
            motor_speed=d['motor_speed'],
            motor_rated_torque=d['motor_rated_torque'],
            starting_factor=d['starting_factor'],
            bevel_efficiency=d['bevel_efficiency'],
            gearbox_output_speed=n_gear_out_eff,
            supplier_motor_power_kw=d.get('supplier_motor_power_kw'),
            supplier_motor_rated_torque=d.get('supplier_motor_rated_torque'),
            supplier_motor_starting_torque=d.get('supplier_motor_starting_torque'),
            supplier_gearbox_rated_torque=d.get('supplier_gearbox_rated_torque'),
            supplier_bevel_ratio=d.get('supplier_bevel_ratio'),
            supplier_worm_ratio=d.get('supplier_worm_ratio'),
            price_prototype=price_proto,
            price_series=price_series,
            torque_check=results['torque_check'],
            torque_margin=results['torque_margin'],
            motor_power_kw=results['motor_power_kw'],
            **spec_data,
        )
        return redirect('suppliers')

    results = None
    if calc_form.is_valid():
        d = calc_form.cleaned_data
        results = drivetrain_sizing(
            crane_torque_max=d['crane_torque_max'],
            crane_torque_nom=d.get('crane_torque_nom'),
            worm_ratio=d['worm_ratio'],
            worm_efficiency=d['worm_efficiency'],
            motor_speed=d['motor_speed'],
            gearbox_output_speed=_effective_gearbox_speed(d),
            motor_rated_torque=d['motor_rated_torque'],
            starting_factor=d['starting_factor'],
            bevel_efficiency=d['bevel_efficiency'],
        )

    compliance = None
    if specs_form.is_valid():
        compliance = check_compliance(specs_form.cleaned_data)

    datasheet, datasheet_json = _load_datasheet(request.POST)
    return render(request, 'calculator/index.html', {
        'form':           calc_form,
        'specs_form':     specs_form,
        'save_form':      save_form,  # already bound with POST data
        'results':        results,
        'datasheet':      datasheet,
        'datasheet_json': datasheet_json,
        'compliance':     compliance,
        'active_page':    'calculator',
        **FORMULAS,
    })


def suppliers(request, crane_filter=None):
    qs = MotorCalculation.objects.all()
    if crane_filter == 'standard_pf':
        qs = qs.filter(crane_type=MotorCalculation.STANDARD_PF)
    elif crane_filter == 'pf_xxl':
        qs = qs.filter(crane_type=MotorCalculation.PF_XXL)
    return render(request, 'calculator/suppliers.html', {
        'calculations': qs,
        'active_page': 'suppliers',
        'crane_filter': crane_filter,
    })


def supplier_detail(request, pk):
    calc = get_object_or_404(MotorCalculation, pk=pk)
    results = calc.recalculate()
    return render(request, 'calculator/supplier_detail.html', {
        'calc': calc,
        'results': results,
        'active_page': 'suppliers',
        **FORMULAS,
    })


def delete_calculation(request, pk):
    calc = get_object_or_404(MotorCalculation, pk=pk)
    if request.method == 'POST':
        calc.delete()
    return redirect('suppliers')


def formulas(request):
    return render(request, 'calculator/formulas.html', {
        'active_page': 'formulas',
        **FORMULAS,
    })


def requirements(request):
    M_MAX = 62_000   # Nm — max crane slewing torque (fixed design basis)
    I_WORM = 150     # worm gear ratio (fixed)
    N_MOTOR = 1450   # rpm — 4-pole 50 Hz (standard selection)
    N_MOTOR_6P = 960 # rpm — 6-pole 50 Hz (alternative)

    IEC_POWERS = [0.37, 0.55, 0.75, 1.1, 1.5, 2.2, 3.0, 4.0, 5.5, 7.5]

    def next_iec(p):
        return next((x for x in IEC_POWERS if x >= p), None)

    ETA_BEVEL = 0.95  # bevel gearbox efficiency applied in Step 6

    def _row(eta, n_slew, ma_mn):
        ng = round(n_slew * I_WORM, 2)
        M2 = M_MAX / (I_WORM * eta)
        ib = N_MOTOR / ng
        Mr = M2 / (ib * ETA_BEVEL)   # Step 6: includes bevel efficiency
        Mn = Mr / ma_mn
        P  = Mn * N_MOTOR / 9550
        M_start = Mn * ma_mn
        return {
            'eta': eta, 'n_slew': n_slew, 'ma_mn': ma_mn,
            'M2_max':      round(M2, 1),
            'n_gear_out':  round(ng, 1),
            'i_bevel':     round(ib, 2),
            'M_motor_req': round(Mr, 1),
            'M_n':         round(Mn, 1),
            'M_start':     round(M_start, 1),
            'P_req':       round(P, 3),
            'P_iec':       next_iec(P),
            'ok':          round(M_start, 1) >= round(Mr, 1),
        }

    # Summary boundary cases (basis: η=0.35–0.45, n_slew=0.25–0.35 rpm)
    worst = _row(0.35, 0.35, 3.0)   # worst: low η, high slew speed, low Ma/Mn
    best  = _row(0.45, 0.25, 3.5)   # best:  high η, low slew speed, high Ma/Mn
    typ   = _row(0.40, 0.30, 3.4)   # typical PF crane operating point

    # Full sizing matrix (η × n_slew, Ma/Mn fixed at 3.4)
    matrix = [
        _row(eta, n_slew, 3.4)
        for eta in [0.30, 0.35, 0.40, 0.45, 0.50]
        for n_slew in [0.25, 0.30, 0.35]
    ]

    # Gearbox sizing torque for typical case (load spectrum method, M_nom≈40% of M_max)
    M2_typ_nom = typ['M2_max'] * 0.40
    gb_soll_typ = round(M2_typ_nom * SAFETY_FACTOR, 1)

    context = {
        'M_MAX': M_MAX, 'I_WORM': I_WORM, 'N_MOTOR': N_MOTOR, 'N_MOTOR_6P': N_MOTOR_6P,
        'SF': SAFETY_FACTOR, 'ETA_BEVEL': ETA_BEVEL,
        'worst': worst, 'best': best, 'typ': typ,
        'matrix': matrix,
        'gb_soll_typ': gb_soll_typ,
        'active_page': 'requirements',
        **FORMULAS,
    }
    return render(request, 'calculator/requirements.html', context)


def comparison(request):
    crane_filter = request.GET.get('crane', None)
    qs = MotorCalculation.objects.all()
    if crane_filter == 'standard_pf':
        qs = qs.filter(crane_type=MotorCalculation.STANDARD_PF)
    elif crane_filter == 'pf_xxl':
        qs = qs.filter(crane_type=MotorCalculation.PF_XXL)
    return render(request, 'calculator/comparison.html', {
        'calculations': qs,
        'crane_filter': crane_filter,
        'active_page': 'comparison',
    })
