import json
from django.shortcuts import render, redirect, get_object_or_404
from .models import Motor, RingSystem
from .services import evaluate, verdict

FORMULAS = {
    'title': 'Motor Validation Formulas',

    'section_1': 'Combined Factor',
    'f_CF': {
        'latex': r'CF = i_{\text{slew}} \times \eta_{\text{slew}}',
        'description': 'Combined factor — total torque multiplication from GM output to ring',
        'vars': {
            'i_slew': 'Slewing-ring reduction ratio (:1)',
            'η_slew': 'Slewing-ring efficiency (–)',
            'CF': 'Combined factor (–)',
        }
    },

    'section_2': 'Speed Calculations',
    'f1': {
        'latex': r'i_{\text{tot}} = i_{\text{gb}} \times i_{\text{slew}}',
        'description': 'Total reduction ratio',
        'vars': {
            'i_gb': 'Gearbox reduction ratio (:1)',
            'i_slew': 'Slewing-ring reduction ratio (:1)',
            'i_tot': 'Total reduction ratio (:1)',
        }
    },
    'f2': {
        'latex': r'n_{\text{gm}} = \dfrac{n_{\text{mot}}}{i_{\text{gb}}}',
        'description': 'GM output speed',
        'vars': {
            'n_mot': 'Motor rated speed (rpm)',
            'i_gb': 'Gearbox reduction ratio (:1)',
            'n_gm': 'GM output speed (rpm)',
        }
    },
    'f3': {
        'latex': r'n_{\text{slew}} = \dfrac{n_{\text{gm}}}{i_{\text{slew}}} = \dfrac{n_{\text{mot}}}{i_{\text{tot}}}',
        'description': 'Crane slewing speed',
        'vars': {
            'n_gm': 'GM output speed (rpm)',
            'n_mot': 'Motor rated speed (rpm)',
            'i_slew': 'Slewing-ring reduction ratio (:1)',
            'i_tot': 'Total reduction ratio (:1)',
            'n_slew': 'Crane slewing speed (rpm)',
        }
    },

    'section_3': 'Power Consistency',
    'f4': {
        'latex': r'\Delta P = \dfrac{\left| P - \dfrac{T_{\text{nom}} \times n_{\text{gm}}}{k} \right|}{P} \times 100\%',
        'description': 'Power consistency check (limit: ≤ 5%)',
        'vars': {
            'P': 'Motor rated power (kW)',
            'T_nom': 'GM nominal torque (Nm)',
            'n_gm': 'GM output speed (rpm)',
            'k': 'Torque constant = 60000/(2π) = 9549.3 (–)',
            'ΔP': 'Power consistency deviation (%)',
        }
    },

    'section_4': 'Ring Torques (GM Output → Ring)',
    'f5': {
        'latex': r'M_{S2} = T_{\text{nom}} \times CF',
        'description': 'Ring running/nominal torque',
        'vars': {
            'T_nom': 'GM nominal torque (Nm)',
            'CF': 'Combined factor (–)',
            'M_S2': 'Ring nominal torque (Nm)',
        }
    },
    'f6': {
        'latex': r'M_{\text{PU}} = T_{\text{pu}} \times CF',
        'description': 'Ring pull-up torque (required: ≥ 0.9 × M_rated)',
        'vars': {
            'T_pu': 'GM pull-up torque (Nm)',
            'CF': 'Combined factor (–)',
            'M_PU': 'Ring pull-up torque (Nm)',
        }
    },
    'f7': {
        'latex': r'M_{\text{start}} = T_{\text{start}} \times CF',
        'description': 'Ring start/breakaway torque (required: M_rated ≤ M_start ≤ M_max)',
        'vars': {
            'T_start': 'GM start torque (Nm)',
            'CF': 'Combined factor (–)',
            'M_start': 'Ring start torque (Nm)',
        }
    },
    'f8': {
        'latex': r'M_{\text{peak}} = T_{\text{peak}} \times CF',
        'description': 'Ring peak torque (required: M_peak ≤ M_max)',
        'vars': {
            'T_peak': 'GM peak torque (Nm)',
            'CF': 'Combined factor (–)',
            'M_peak': 'Ring peak torque (Nm)',
        }
    },

    'section_5': 'Derived Limits',
    'f9': {
        'latex': r'T_{\text{gm,nom,req}} = \dfrac{M_{\text{rated}}}{CF}',
        'description': 'Required GM nominal torque',
        'vars': {
            'M_rated': 'Ring nominal torque (Nm)',
            'CF': 'Combined factor (–)',
            'T_gm_nom_req': 'Required GM nominal torque (Nm)',
        }
    },
    'f10': {
        'latex': r'T_{\text{gm,start,max}} = \dfrac{M_{\text{max}}}{CF}',
        'description': 'Maximum permissible GM starting torque',
        'vars': {
            'M_max': 'Ring maximum torque (Nm)',
            'CF': 'Combined factor (–)',
            'T_gm_start_max': 'Max GM starting torque (Nm)',
        }
    },
}


def index(request):
    return redirect('motor_list', system_type='standard_pf')


def formulas(request):
    ring_systems = RingSystem.objects.all().order_by('system_type')
    return render(request, 'calculator/formulas.html', {
        'ring_systems': ring_systems,
        'active_page': 'formulas',
        **FORMULAS,
    })


def formula_verifier(request):
    """Manual formula verification tool — input values and see them flow through all calculations."""
    ring_systems = RingSystem.objects.all().order_by('system_type')
    result = None
    ring_system = None

    if request.method == 'POST':
        system_type = request.POST.get('system_type', 'standard_pf')
        ring_system = get_object_or_404(RingSystem, system_type=system_type)

        try:
            motor_input = {
                'i_gb': float(request.POST.get('i_gb', 0)),
                'n_mot': float(request.POST.get('n_mot', 0)),
                'P': float(request.POST.get('P', 0)),
                'T_nom': float(request.POST.get('T_nom', 0)),
                'T_pu': float(request.POST.get('T_pu')) if request.POST.get('T_pu') else None,
                'T_start': float(request.POST.get('T_start', 0)),
                'T_peak': float(request.POST.get('T_peak', 0)),
                'T_in_max': float(request.POST.get('T_in_max')) if request.POST.get('T_in_max') else None,
                'T_bd': float(request.POST.get('T_bd')) if request.POST.get('T_bd') else None,
                'fB': float(request.POST.get('fB')) if request.POST.get('fB') else None,
                'duty': request.POST.get('duty', ''),
                'flange': request.POST.get('flange', ''),
            }

            result = evaluate(motor_input, ring_system)
            result['system_type_display'] = ring_system.get_system_type_display()
        except (ValueError, TypeError) as e:
            result = {'error': f'Invalid input: {str(e)}'}

    return render(request, 'calculator/formula_verifier.html', {
        'ring_systems': ring_systems,
        'result': result,
        'ring_system': ring_system,
        'active_page': 'formulas',
        **FORMULAS,
    })


def acceptance_ranges(request):
    """Show acceptable input ranges and limits for each crane type."""
    ring_systems = RingSystem.objects.all().order_by('system_type')

    acceptance_data = {}
    for rs in ring_systems:
        T_gm_nom_req = rs.M_rated / rs.CF
        T_gm_start_max = rs.M_max / rs.CF

        acceptance_data[rs.system_type] = {
            'system': rs,
            'T_gm_nom_req': T_gm_nom_req,
            'T_gm_start_max': T_gm_start_max,
            'T_gm_start_min': T_gm_nom_req,
            'T_gm_nom_min': T_gm_nom_req,
            'T_gm_peak_max': T_gm_start_max,
            'T_gm_pu_min': 0.9 * T_gm_nom_req,

            # Typical motor specs for this crane (4-pole induction motors)
            'typical_n_mot': [1365, 1415],
            'typical_i_gb_min': rs.n_gm_min if rs.n_gm_min > 0 else 20,
            'typical_i_gb_max': (1415 / rs.n_gm_min) if rs.n_gm_min > 0 else 70,

            'n_gm_min': rs.n_gm_min,
            'n_gm_max': rs.n_gm_max,
            'n_slew_min': rs.n_slew_min,
            'n_slew_max': rs.n_slew_max,
            'n_slew_tgt': rs.n_slew_tgt,

            'M_rated': rs.M_rated,
            'M_max': rs.M_max,
            'CF': rs.CF,
        }

    return render(request, 'calculator/acceptance_ranges.html', {
        'ring_systems': ring_systems,
        'acceptance_data': acceptance_data,
        'active_page': 'formulas',
        **FORMULAS,
    })


def requirements(request):
    ring_systems = RingSystem.objects.all().order_by('system_type')
    context = {
        'ring_systems': ring_systems,
        'active_page': 'requirements',
        **FORMULAS,
    }
    return render(request, 'calculator/requirements.html', context)


def comparison(request):
    crane_filter = request.GET.get('crane', None)
    qs = Motor.objects.select_related('ring_system').all()
    if crane_filter == 'standard_pf':
        qs = qs.filter(ring_system__system_type=RingSystem.STANDARD_PF)
    elif crane_filter == 'pf_xxl':
        qs = qs.filter(ring_system__system_type=RingSystem.PF_XXL)
    return render(request, 'calculator/comparison.html', {
        'motors': qs,
        'crane_filter': crane_filter,
        'active_page': 'comparison',
    })


def motor_list(request, system_type='standard_pf'):
    ring_system = get_object_or_404(RingSystem, system_type=system_type)
    motors = Motor.objects.filter(ring_system=ring_system).order_by('-created_at')

    return render(request, 'calculator/motor_list.html', {
        'ring_system': ring_system,
        'motors': motors,
        'active_page': 'motors',
    })


def motor_create(request, system_type='standard_pf'):
    from .forms_motor import MotorForm

    ring_system = get_object_or_404(RingSystem, system_type=system_type)
    result = None
    checks = {}
    passed_count = 0

    if request.method == 'POST':
        form = MotorForm(request.POST, ring_system=ring_system)
        if form.is_valid():
            motor = form.save(commit=False)
            motor.ring_system = ring_system

            motor_input = {
                'i_gb': motor.i_gb,
                'n_mot': motor.n_mot,
                'P': motor.P,
                'T_nom': motor.T_nom,
                'T_pu': motor.T_pu,
                'T_start': motor.T_start,
                'T_peak': motor.T_peak,
                'T_in_max': motor.T_in_max,
                'T_bd': motor.T_bd,
                'fB': motor.fB,
                'duty': motor.duty,
                'flange': motor.flange,
            }

            result = evaluate(motor_input, ring_system)
            checks = result.get('checks', {})
            passed_count = sum(1 for c in checks.values() if c['status'] == 'PASS')

            motor.i_tot = result.get('i_tot')
            motor.n_gm = result.get('n_gm')
            motor.n_slew = result.get('n_slew')
            motor.dP = result.get('dP')
            motor.M_S2 = result.get('M_S2')
            motor.M_PU = result.get('M_PU')
            motor.M_start = result.get('M_start')
            motor.M_peak = result.get('M_peak')

            motor.checks_json = json.dumps(checks)
            motor.verdict = verdict(checks)
            motor.passed_count = passed_count

            motor.save()
            return redirect('motor_detail', pk=motor.pk)
    else:
        form = MotorForm(ring_system=ring_system)

    return render(request, 'calculator/motor_form.html', {
        'ring_system': ring_system,
        'form': form,
        'active_page': 'motors',
    })


def motor_detail(request, pk):
    motor = get_object_or_404(Motor, pk=pk)
    ring_system = motor.ring_system
    checks = motor.checks

    result = {
        'i_tot': motor.i_tot,
        'n_gm': motor.n_gm,
        'n_slew': motor.n_slew,
        'dP': motor.dP * 100 if motor.dP is not None else None,
        'M_S2': motor.M_S2,
        'M_PU': motor.M_PU,
        'M_start': motor.M_start,
        'M_peak': motor.M_peak,
        'verdict': motor.verdict,
        'passed_count': motor.passed_count,
    }

    return render(request, 'calculator/motor_results.html', {
        'motor': motor,
        'ring_system': ring_system,
        'result': result,
        'checks': checks,
        'active_page': 'motors',
    })
