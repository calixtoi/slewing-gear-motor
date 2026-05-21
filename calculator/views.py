import json
import os
import tempfile
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from .forms import DrivetrainForm, SaveCalculationForm, DatasheetUploadForm, MotorSpecsForm, TextDatasheetForm
from .engine import drivetrain_sizing, SAFETY_FACTOR
from .models import MotorCalculation
from .pdf_parser import (
    parse_datasheet, parse_text, check_compliance, specs_to_form_initial,
    extract_motor_params, extract_motor_params_from_pdf, MOTOR_PARAM_LABELS,
)

# Raw strings so backslashes reach KaTeX unchanged.
FORMULAS = {
    'f1':  r'M_{2,\max} = \dfrac{M_{\max}}{i_{\text{worm}} \cdot \eta}',
    'f2':  r'M_{2,\text{nom}} = \dfrac{M_{\text{nom}}}{i_{\text{worm}} \cdot \eta}',
    'f3':  r'M_{\text{gear,req}} = M_{2,\text{nom}} \times S_f \qquad S_f = 1.34',
    'f4':     r'i_{\text{bevel}} = \dfrac{n_{\text{motor}}}{n_{\text{gear,out}}}',
    'f4_inv': r'n_{\text{gear,out}} = \dfrac{n_{\text{motor}}}{i_{\text{bevel}}}',
    'f5':  r'n_{\text{slew}} = \dfrac{n_{\text{gear,out}}}{i_{\text{worm}}}',
    'f2_inv': r'M_{2,\text{nom}} = M_n \cdot i_{\text{worm}} \cdot \eta_{\text{worm}} \quad \text{(back-calc from motor)}',
    'f6':  r'M_{\text{motor,req}} = \dfrac{M_{2,\max}}{i_{\text{bevel}} \cdot \eta_{\text{bevel}}}',
    'f7':  r'M_{\text{start}} = M_n \cdot k_{\text{start}}, \qquad k_{\text{start}} = \dfrac{M_a}{M_n}',
    'f8':  r'\text{margin} = \dfrac{M_{\text{start}}}{M_{\text{motor,req}}}',
    'f8c': (
        r'\begin{cases}'
        r'\text{margin} \geq 1.5 & \Rightarrow \textbf{OK} \\'
        r'1.0 \leq \text{margin} < 1.5 & \Rightarrow \textbf{Low\;Margin} \\'
        r'\text{margin} < 1.0 & \Rightarrow \textbf{CRITICAL\;FAIL\;—\;Motor\;Will\;Stall}'
        r'\end{cases}'
    ),
    'f9':     r'P_{\text{rated}}\,[\text{kW}] = \dfrac{M_n\,[\text{Nm}] \cdot n_{\text{motor}}\,[\text{rpm}]}{9550}',
    'f9_inv': r'M_n\,[\text{Nm}] = \dfrac{9550 \times P_{\text{rated}}\,[\text{kW}]}{n_{\text{motor}}\,[\text{rpm}]}',
    'f9b':    r'9550 = \dfrac{60 \times 10^3}{2\pi} \approx 9549.3',
    'fg1': r'M_{2,\text{nom}} = \dfrac{M_{\text{nom}}}{i_{\text{worm}} \cdot \eta}',
    'fg2': r'M_{2,\max} = \dfrac{M_{\max}}{i_{\text{worm}} \cdot \eta}',
    'fg3': r'\lambda = \dfrac{M_{2,\text{nom}}}{M_{2,\max}}',
    'fg4': r'M_{\text{gear,soll}} = M_{2,\text{nom}} + \left(M_{2,\max} - M_{2,\text{nom}}\right) \cdot \lambda',
    'fg4_exp': (
        r'M_{\text{gear,soll}} = M_{2,\text{nom}} + '
        r'\left(M_{2,\max} - M_{2,\text{nom}}\right) \cdot '
        r'\dfrac{M_{2,\text{nom}}}{M_{2,\max}}'
    ),
    'fs_margin': r'\text{margin} = \dfrac{\text{value}_{\text{supplier}}}{\text{value}_{\text{required}}} \geq 1.10',
    'fs_ratio':  r'\text{deviation} = \dfrac{|\,r_{\text{supplier}} - r_{\text{calc}}\,|}{r_{\text{calc}}} \leq 2\%',
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
    return d['motor_speed'] / d['gear_ratio']


def index(request):
    results = None
    form = DrivetrainForm()
    specs_form = MotorSpecsForm()
    datasheet = None
    datasheet_json = ''
    compliance = None

    _load_fields = [
        'crane_torque_max', 'crane_torque_nom', 'worm_ratio', 'worm_efficiency',
        'motor_speed', 'gearbox_output_speed', 'gear_ratio', 'motor_rated_torque', 'starting_factor',
        'supplier_motor_power_kw', 'supplier_motor_rated_torque',
        'supplier_motor_starting_torque', 'supplier_gearbox_rated_torque',
        'supplier_bevel_ratio', 'supplier_worm_ratio',
    ]
    if request.method == 'GET' and any(k in request.GET for k in _load_fields):
        form = DrivetrainForm(initial={k: request.GET[k] for k in _load_fields if k in request.GET})

    if request.method == 'POST':
        form = DrivetrainForm(request.POST)
        specs_form = MotorSpecsForm(request.POST)
        datasheet, datasheet_json = _load_datasheet(request.POST)
        if form.is_valid():
            d = form.cleaned_data
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

        if specs_form.is_valid():
            compliance = check_compliance(specs_form.cleaned_data)

    save_initial = {}
    if datasheet:
        save_initial = {
            'supplier_name':   datasheet.get('supplier', ''),
            'crane_type':      datasheet.get('crane_type', ''),
            'price_prototype': datasheet.get('price_prototype'),
            'price_series':    datasheet.get('price_series'),
        }
    save_form = SaveCalculationForm(initial=save_initial)

    return render(request, 'calculator/index.html', {
        'form': form,
        'specs_form': specs_form,
        'save_form': save_form,
        'results': results,
        'datasheet': datasheet,
        'datasheet_json': datasheet_json,
        'compliance': compliance,
        'active_page': 'calculator',
        **FORMULAS,
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
