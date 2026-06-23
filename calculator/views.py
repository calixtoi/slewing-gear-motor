import json
from django.shortcuts import render, redirect, get_object_or_404
from .models import Motor, RingSystem
from .services import evaluate, verdict

FORMULAS = {
    'f_CF':    r'CF = i_{\text{slew}} \times \eta_{\text{slew}}',
    'f1':      r'i_{\text{tot}} = i_{\text{gb}} \times i_{\text{slew}}',
    'f2':      r'n_{\text{gm}} = \dfrac{n_{\text{mot}}}{i_{\text{gb}}}',
    'f3':      r'n_{\text{slew}} = \dfrac{n_{\text{gm}}}{i_{\text{slew}}}',
    'f4':      r'M_{S2} = T_{\text{nom}} \times CF',
    'f5':      r'M_{\text{start}} = T_{\text{start}} \times CF',
    'f6':      r'M_{\text{peak}} = T_{\text{peak}} \times CF',
}


def index(request):
    return redirect('motor_list', system_type='standard_pf')


def formulas(request):
    return render(request, 'calculator/formulas.html', {
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
