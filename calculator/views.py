import json
from django.shortcuts import render, redirect, get_object_or_404
from .models import Motor, RingSystem
from .services import evaluate, verdict
from .formula_builder import SymbolicFormula
from .formula_display import FormulaDisplay

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
        'description': 'Total reduction ratio combining gearbox and slewing ring',
        'vars': {
            'i_gb': 'Gearbox reduction ratio (:1)',
            'i_slew': 'Slewing-ring reduction ratio (:1)',
            'i_tot': 'Total reduction ratio (:1)',
        }
    },
    'f2': {
        'latex': r'n_{\text{gm}} = \frac{n_{\text{mot}}}{i_{\text{gb}}}',
        'description': 'GM output speed from motor speed and gearbox ratio',
        'vars': {
            'n_mot': 'Motor rated speed (rpm)',
            'i_gb': 'Gearbox reduction ratio (:1)',
            'n_gm': 'GM output speed (rpm)',
        }
    },
    'f3': {
        'latex': r'n_{\text{slew}} = \frac{n_{\text{gm}}}{i_{\text{slew}}} = \frac{n_{\text{mot}}}{i_{\text{tot}}}',
        'description': 'Crane slewing speed (two equivalent forms)',
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
        'latex': r'\Delta P = 100 \times \frac{\left| P - \frac{T_{\text{nom}} \times n_{\text{gm}}}{k} \right|}{P}',
        'description': 'Power consistency deviation (acceptance: ≤ 5%)',
        'vars': {
            'P': 'Motor rated power (kW)',
            'T_nom': 'GM nominal torque (Nm)',
            'n_gm': 'GM output speed (rpm)',
            'k': 'Torque constant = 60000/(2π) = 9549.3 (–)',
            'ΔP': 'Power consistency deviation (%)',
        }
    },

    'section_4': 'Ring Torques (GM Output × CF)',
    'f5': {
        'latex': r'M_{S2} = T_{\text{nom}} \times CF',
        'description': 'Ring nominal/running torque',
        'vars': {
            'T_nom': 'GM nominal torque (Nm)',
            'CF': 'Combined factor (–)',
            'M_S2': 'Ring nominal torque (Nm)',
        }
    },
    'f6': {
        'latex': r'M_{\text{PU}} = T_{\text{pu}} \times CF',
        'description': 'Ring pull-up torque (constraint: ≥ 0.9 × M_rated)',
        'vars': {
            'T_pu': 'GM pull-up torque (Nm)',
            'CF': 'Combined factor (–)',
            'M_PU': 'Ring pull-up torque (Nm)',
        }
    },
    'f7': {
        'latex': r'M_{\text{start}} = T_{\text{start}} \times CF',
        'description': 'Ring starting torque (constraint: M_rated ≤ M_start ≤ M_max)',
        'vars': {
            'T_start': 'GM starting torque (Nm)',
            'CF': 'Combined factor (–)',
            'M_start': 'Ring starting torque (Nm)',
        }
    },
    'f8': {
        'latex': r'M_{\text{peak}} = T_{\text{peak}} \times CF',
        'description': 'Ring peak torque (constraint: M_peak ≤ M_max)',
        'vars': {
            'T_peak': 'GM peak torque (Nm)',
            'CF': 'Combined factor (–)',
            'M_peak': 'Ring peak torque (Nm)',
        }
    },

    'section_5': 'Derived Limits (Reverse Calculations)',
    'f9': {
        'latex': r'T_{\text{gm,nom,req}} = \frac{M_{\text{rated}}}{CF}',
        'description': 'Required GM nominal torque to meet ring rated capacity',
        'vars': {
            'M_rated': 'Ring rated torque (Nm)',
            'CF': 'Combined factor (–)',
            'T_gm_nom_req': 'Required GM nominal torque (Nm)',
        }
    },
    'f10': {
        'latex': r'T_{\text{gm,start,max}} = \frac{M_{\text{max}}}{CF}',
        'description': 'Maximum permissible GM starting torque before ring failure',
        'vars': {
            'M_max': 'Ring maximum torque (Nm)',
            'CF': 'Combined factor (–)',
            'T_gm_start_max': 'Max GM starting torque (Nm)',
        }
    },
}


def index(request):
    """Landing page with navigation to all apps."""
    ring_systems = RingSystem.objects.all().order_by('system_type')
    motor_counts = {}
    for rs in ring_systems:
        motor_counts[rs.system_type] = rs.motors.count()

    return render(request, 'calculator/index.html', {
        'ring_systems': ring_systems,
        'motor_counts': motor_counts,
        'active_page': 'home',
    })


def formulas(request):
    ring_systems = RingSystem.objects.all().order_by('system_type')
    return render(request, 'calculator/formulas.html', {
        'ring_systems': ring_systems,
        'active_page': 'formulas',
        **FORMULAS,
    })


def formula_reference(request):
    """Dedicated formulas page with beautiful LaTeX rendering and detailed explanations."""
    ring_systems = RingSystem.objects.all().order_by('system_type')

    formulas_data = {
        'combined_factor': {
            'title': 'Combined Factor',
            'latex': r'CF = i_{\text{slew}} \times \eta_{\text{slew}}',
            'description': 'The combined factor represents the total torque multiplication from the GM output shaft to the ring.',
            'variables': [
                ('i_{\\text{slew}}', 'Slewing-ring reduction ratio (:1)', 'Fixed system parameter'),
                ('\\eta_{\\text{slew}}', 'Slewing-ring efficiency (–)', 'Fixed at 0.40 for both variants'),
                ('CF', 'Combined factor (–)', 'Calculated: PF Std = 48.4, PF-XXL = 44.0'),
            ],
            'note': 'This factor is fundamental to all subsequent torque calculations.',
        },
        'total_reduction': {
            'title': 'Total Reduction Ratio',
            'latex': r'i_{\text{tot}} = i_{\text{gb}} \times i_{\text{slew}}',
            'description': 'The total reduction combines the gearbox ratio with the slewing ring ratio.',
            'variables': [
                ('i_{\\text{gb}}', 'Gearbox reduction ratio (:1)', 'From motor datasheet'),
                ('i_{\\text{slew}}', 'Slewing-ring reduction ratio (:1)', 'System constant'),
                ('i_{\\text{tot}}', 'Total reduction ratio (:1)', 'Calculated'),
            ],
            'note': 'Used to calculate final crane slewing speed from motor speed.',
        },
        'gm_output_speed': {
            'title': 'GM Output Speed',
            'latex': r'n_{\text{gm}} = \frac{n_{\text{mot}}}{i_{\text{gb}}}',
            'description': 'The speed at the gearbox output shaft, obtained by dividing motor speed by the gearbox ratio.',
            'variables': [
                ('n_{\\text{mot}}', 'Motor rated speed (rpm)', 'From motor datasheet'),
                ('i_{\\text{gb}}', 'Gearbox reduction ratio (:1)', 'From motor datasheet'),
                ('n_{\\text{gm}}', 'GM output speed (rpm)', 'Calculated'),
            ],
            'constraints': [
                'PF Standard: 30–60 rpm',
                'PF-XXL: 22–55 rpm',
            ],
            'note': 'This speed must fall within the acceptable window for the chosen crane type.',
        },
        'slewing_speed': {
            'title': 'Crane Slewing Speed',
            'latex': r'n_{\text{slew}} = \frac{n_{\text{gm}}}{i_{\text{slew}}} = \frac{n_{\text{mot}}}{i_{\text{tot}}}',
            'description': 'The final crane slewing speed obtained by dividing GM output speed by the slewing ring ratio.',
            'variables': [
                ('n_{\\text{gm}}', 'GM output speed (rpm)', 'Calculated from previous formula'),
                ('i_{\\text{slew}}', 'Slewing-ring reduction ratio (:1)', 'System constant'),
                ('n_{\\text{slew}}', 'Crane slewing speed (rpm)', 'Final result'),
            ],
            'constraints': [
                'PF Standard: 0.2–1.0 rpm (target: 0.40 ±10%)',
                'PF-XXL: 0.2–0.5 rpm (target: 0.35 ±10%)',
            ],
            'note': 'Critical specification—must be within the acceptable window and near the target speed.',
        },
        'power_consistency': {
            'title': 'Power Consistency Check',
            'latex': r'\Delta P = \frac{\left| P - \frac{T_{\text{nom}} \times n_{\text{gm}}}{k} \right|}{P} \times 100\%',
            'description': 'Validates that the declared motor power matches the calculated power from torque and speed.',
            'variables': [
                ('P', 'Motor rated power (kW)', 'From motor datasheet'),
                ('T_{\\text{nom}}', 'GM nominal output torque (Nm)', 'From motor datasheet'),
                ('n_{\\text{gm}}', 'GM output speed (rpm)', 'Calculated'),
                ('k', 'Torque constant', 'Fixed at 9549.3 (= 60000/2π)'),
                ('\\Delta P', 'Power consistency deviation (%)', 'Calculated'),
            ],
            'constraints': [
                'Required: ΔP ≤ 5%',
            ],
            'note': 'The formula P = T × n / 9549.3 (in kW) must hold. Large deviations indicate datasheet errors.',
        },
        'ring_nominal': {
            'title': 'Ring Nominal Torque',
            'latex': r'M_{S2} = T_{\text{nom}} \times CF',
            'description': 'Operating torque transmitted to the ring during normal running conditions.',
            'variables': [
                ('T_{\\text{nom}}', 'GM nominal output torque (Nm)', 'From motor datasheet'),
                ('CF', 'Combined factor (–)', 'Calculated from CF formula'),
                ('M_{S2}', 'Ring nominal torque (Nm)', 'Calculated'),
            ],
            'note': 'This is the torque the ring must sustain during normal operation.',
        },
        'ring_pullup': {
            'title': 'Ring Pull-Up Torque',
            'latex': r'M_{\text{PU}} = T_{\text{pu}} \times CF',
            'description': 'Pull-up torque transmitted to the ring during acceleration phase.',
            'variables': [
                ('T_{\\text{pu}}', 'GM pull-up/acceleration torque (Nm)', 'From motor datasheet (optional)'),
                ('CF', 'Combined factor (–)', 'Calculated from CF formula'),
                ('M_{\\text{PU}}', 'Ring pull-up torque (Nm)', 'Calculated'),
            ],
            'constraints': [
                'Required: M_PU ≥ 0.9 × M_rated',
            ],
            'note': 'If T_pu is missing from datasheet, this check is marked as REVIEW.',
        },
        'ring_start': {
            'title': 'Ring Start/Breakaway Torque',
            'latex': r'M_{\text{start}} = T_{\text{start}} \times CF',
            'description': 'Peak torque transmitted when starting the crane (critical structural check).',
            'variables': [
                ('T_{\\text{start}}', 'GM starting torque (Nm)', 'From motor datasheet'),
                ('CF', 'Combined factor (–)', 'Calculated from CF formula'),
                ('M_{\\text{start}}', 'Ring start torque (Nm)', 'Calculated'),
            ],
            'constraints': [
                'Required: M_rated ≤ M_start ≤ M_max',
                'PF Standard: 15360 ≤ M_start ≤ 41190 Nm',
                'PF-XXL: 65000 ≤ M_start ≤ 70000 Nm',
            ],
            'note': 'Most critical check—starting torque must be bounded within the ring\'s operating envelope.',
        },
        'ring_peak': {
            'title': 'Ring Peak Torque',
            'latex': r'M_{\text{peak}} = T_{\text{peak}} \times CF',
            'description': 'Maximum transient torque the ring may experience.',
            'variables': [
                ('T_{\\text{peak}}', 'GM peak/maximum torque (Nm)', 'From motor datasheet'),
                ('CF', 'Combined factor (–)', 'Calculated from CF formula'),
                ('M_{\\text{peak}}', 'Ring peak torque (Nm)', 'Calculated'),
            ],
            'constraints': [
                'Required: M_peak ≤ M_max',
            ],
            'note': 'Peak torque must not exceed the structural limit of the ring.',
        },
        'gm_nom_required': {
            'title': 'Required GM Nominal Torque (Reverse Calculation)',
            'latex': r'T_{\text{gm,nom,req}} = \frac{M_{\text{rated}}}{CF}',
            'description': 'Minimum GM output torque required to operate the ring at its rated capacity.',
            'variables': [
                ('M_{\\text{rated}}', 'Ring nominal torque (Nm)', 'System constant'),
                ('CF', 'Combined factor (–)', 'System constant'),
                ('T_{\\text{gm,nom,req}}', 'Required GM nominal torque (Nm)', 'Calculated'),
            ],
            'values': [
                'PF Standard: 15360 / 48.4 = <strong>317.4 Nm</strong>',
                'PF-XXL: 65000 / 44.0 = <strong>1477.3 Nm</strong>',
            ],
            'note': 'Motor must provide at least this torque to operate the ring properly.',
        },
        'gm_start_max': {
            'title': 'Maximum Permissible GM Starting Torque (Reverse Calculation)',
            'latex': r'T_{\text{gm,start,max}} = \frac{M_{\text{max}}}{CF}',
            'description': 'Maximum GM output starting torque the ring can withstand.',
            'variables': [
                ('M_{\\text{max}}', 'Ring maximum structural torque (Nm)', 'System constant'),
                ('CF', 'Combined factor (–)', 'System constant'),
                ('T_{\\text{gm,start,max}}', 'Max GM starting torque (Nm)', 'Calculated'),
            ],
            'values': [
                'PF Standard: 41190 / 48.4 = <strong>851.0 Nm</strong>',
                'PF-XXL: 70000 / 44.0 = <strong>1590.9 Nm</strong>',
            ],
            'note': 'Motor starting torque must not exceed this limit to protect the ring.',
        },
    }

    return render(request, 'calculator/formula_reference.html', {
        'ring_systems': ring_systems,
        'formulas_data': formulas_data,
        'active_page': 'formulas',
    })


def formula_verifier(request):
    """Manual formula verification tool with step-by-step calculation breakdown."""
    ring_systems = RingSystem.objects.all().order_by('system_type')
    result = None
    ring_system = None
    calculation_steps = None

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

            # Build step-by-step calculation breakdown
            calculation_steps = build_calculation_steps(motor_input, ring_system, result)

            # Build clean formula displays (no raw LaTeX)
            n_gm = motor_input['n_mot'] / motor_input['i_gb']
            i_tot = motor_input['i_gb'] * ring_system.i_slew
            n_slew = motor_input['n_mot'] / i_tot

            formula_displays = {
                'total_reduction': FormulaDisplay.total_reduction_breakdown(
                    motor_input['i_gb'], ring_system.i_slew
                ),
                'gm_output_speed': FormulaDisplay.gm_output_speed_breakdown(
                    motor_input['n_mot'], motor_input['i_gb']
                ),
                'slewing_speed': FormulaDisplay.slewing_speed_breakdown(
                    motor_input['n_mot'], i_tot, ring_system.n_slew_tgt
                ),
                'power_consistency': FormulaDisplay.power_consistency_breakdown(
                    motor_input['P'], motor_input['T_nom'], n_gm, ring_system.k
                ),
            }
        except (ValueError, TypeError) as e:
            result = {'error': f'Invalid input: {str(e)}'}
            formula_displays = {}

    return render(request, 'calculator/formula_verifier.html', {
        'ring_systems': ring_systems,
        'result': result,
        'calculation_steps': calculation_steps,
        'formula_displays': formula_displays,
        'ring_system': ring_system,
        'active_page': 'formulas',
        **FORMULAS,
    })


def build_calculation_steps(motor_input, ring_system, result):
    """Build detailed step-by-step calculation breakdown."""
    steps = []

    # Step 0: System Constants
    steps.append({
        'number': '0',
        'title': 'System Constants',
        'description': 'Fixed parameters for the selected crane type',
        'inputs': [
            {'label': 'i_{slew}', 'value': ring_system.i_slew, 'unit': ':1'},
            {'label': '\\eta_{slew}', 'value': ring_system.eta_slew, 'unit': '–'},
            {'label': 'CF', 'value': ring_system.CF, 'unit': '–'},
            {'label': 'M_{rated}', 'value': ring_system.M_rated, 'unit': 'Nm'},
            {'label': 'M_{max}', 'value': ring_system.M_max, 'unit': 'Nm'},
        ],
        'formula': r'CF = i_{\text{slew}} \times \eta_{\text{slew}} = ' + f'{ring_system.i_slew} \\times {ring_system.eta_slew} = {ring_system.CF}',
        'output': {'label': 'CF (Combined Factor)', 'value': ring_system.CF, 'unit': '–'},
    })

    # Step 1: Total Reduction
    i_tot = motor_input['i_gb'] * ring_system.i_slew
    formula_latex, substitution_latex, _ = SymbolicFormula.total_reduction_formula(
        motor_input['i_gb'], ring_system.i_slew
    )
    steps.append({
        'number': '1',
        'title': 'Total Reduction Ratio',
        'description': 'Combine gearbox and slewing ring ratios',
        'inputs': [
            {'label': 'i_{gb}', 'value': motor_input['i_gb'], 'unit': ':1', 'source': 'Motor datasheet'},
            {'label': 'i_{slew}', 'value': ring_system.i_slew, 'unit': ':1', 'source': 'System constant'},
        ],
        'formula': formula_latex,
        'substitution': substitution_latex,
        'output': {'label': 'i_{tot}', 'value': i_tot, 'unit': ':1'},
    })

    # Step 2: GM Output Speed
    n_gm = motor_input['n_mot'] / motor_input['i_gb']
    formula_latex, substitution_latex, _ = SymbolicFormula.gm_output_speed_formula(
        motor_input['n_mot'], motor_input['i_gb']
    )
    steps.append({
        'number': '2',
        'title': 'GM Output Speed',
        'description': 'Speed at the gearbox output shaft',
        'inputs': [
            {'label': 'n_{mot}', 'value': motor_input['n_mot'], 'unit': 'rpm', 'source': 'Motor datasheet'},
            {'label': 'i_{gb}', 'value': motor_input['i_gb'], 'unit': ':1', 'source': 'Motor datasheet'},
        ],
        'formula': formula_latex,
        'substitution': substitution_latex,
        'output': {'label': 'n_{gm}', 'value': n_gm, 'unit': 'rpm'},
        'constraints': [
            f'Acceptable window: {ring_system.n_gm_min}–{ring_system.n_gm_max} rpm',
            f'Check: {ring_system.n_gm_min} ≤ {n_gm:.2f} ≤ {ring_system.n_gm_max} → ' + ('✓ PASS' if ring_system.n_gm_min <= n_gm <= ring_system.n_gm_max else '✗ FAIL'),
        ],
    })

    # Step 3: Crane Slewing Speed
    n_slew = motor_input['n_mot'] / i_tot
    formula_latex, substitution_latex, _ = SymbolicFormula.slewing_speed_formula(
        motor_input['n_mot'], i_tot
    )
    steps.append({
        'number': '3',
        'title': 'Crane Slewing Speed',
        'description': 'Final crane speed at the ring',
        'inputs': [
            {'label': 'n_{mot}', 'value': motor_input['n_mot'], 'unit': 'rpm', 'source': 'Motor datasheet'},
            {'label': 'i_{tot}', 'value': i_tot, 'unit': ':1', 'source': 'From Step 1'},
        ],
        'formula': formula_latex,
        'substitution': substitution_latex,
        'output': {'label': 'n_{slew}', 'value': n_slew, 'unit': 'rpm'},
        'constraints': [
            f'Acceptable window: {ring_system.n_slew_min}–{ring_system.n_slew_max} rpm',
            f'Target: {ring_system.n_slew_tgt} ±10% = {ring_system.n_slew_tgt * 0.9:.3f}–{ring_system.n_slew_tgt * 1.1:.3f} rpm',
            f'Check: {ring_system.n_slew_min} ≤ {n_slew:.4f} ≤ {ring_system.n_slew_max} → ' + ('✓ PASS' if ring_system.n_slew_min <= n_slew <= ring_system.n_slew_max else '✗ FAIL'),
        ],
    })

    # Step 4: Power Consistency
    dP_fraction = result.get('dP')
    dP_percent = dP_fraction * 100 if dP_fraction else None
    formula_latex, substitution_latex, _ = SymbolicFormula.power_consistency_formula(
        motor_input['P'], motor_input['T_nom'], n_gm, ring_system.k
    )
    steps.append({
        'number': '4',
        'title': 'Power Consistency Check',
        'description': 'Verify declared power matches T×n calculation',
        'inputs': [
            {'label': 'P', 'value': motor_input['P'], 'unit': 'kW', 'source': 'Motor datasheet'},
            {'label': 'T_{nom}', 'value': motor_input['T_nom'], 'unit': 'Nm', 'source': 'Motor datasheet'},
            {'label': 'n_{gm}', 'value': n_gm, 'unit': 'rpm', 'source': 'From Step 2'},
            {'label': 'k', 'value': ring_system.k, 'unit': '–', 'source': 'Constant (60000/2π)'},
        ],
        'formula': formula_latex,
        'substitution': substitution_latex,
        'output': {'label': '\\Delta P', 'value': dP_percent, 'unit': '%'},
        'constraints': [
            f'Required: ΔP ≤ 5%',
            f'Check: {dP_percent:.2f if dP_percent else "N/A"}% ≤ 5% → ' + ('✓ PASS' if dP_percent and dP_percent <= 5 else '✗ FAIL' if dP_percent else '? N/A'),
        ],
    })

    # Step 5: Ring Torques
    sub_steps_list = []
    for torque_type, T_value in [
        ('nom', motor_input['T_nom']),
        ('pu', motor_input['T_pu']),
        ('start', motor_input['T_start']),
        ('peak', motor_input['T_peak']),
    ]:
        formula_latex, substitution_latex, M_value = SymbolicFormula.ring_torque_formula(
            torque_type, T_value, ring_system.CF
        )
        sub_steps_list.append({
            'formula': formula_latex,
            'substitution': substitution_latex,
            'output': f'{M_value:.0f}' if M_value else 'N/A',
        })

    steps.append({
        'number': '5',
        'title': 'Ring Torques (GM Output × CF)',
        'description': 'Scale GM torques to ring level',
        'inputs': [
            {'label': 'T_{nom}', 'value': motor_input['T_nom'], 'unit': 'Nm', 'source': 'Motor datasheet'},
            {'label': 'T_{pu}', 'value': motor_input['T_pu'], 'unit': 'Nm', 'source': 'Motor datasheet' if motor_input['T_pu'] else 'Not provided'},
            {'label': 'T_{start}', 'value': motor_input['T_start'], 'unit': 'Nm', 'source': 'Motor datasheet'},
            {'label': 'T_{peak}', 'value': motor_input['T_peak'], 'unit': 'Nm', 'source': 'Motor datasheet'},
            {'label': 'CF', 'value': ring_system.CF, 'unit': '–', 'source': 'System constant'},
        ],
        'sub_steps': sub_steps_list,
    })

    # Step 6: Derived Limits
    T_gm_nom_req = ring_system.M_rated / ring_system.CF
    T_gm_start_max = ring_system.M_max / ring_system.CF

    formula_nom, substitution_nom, _ = SymbolicFormula.required_gm_torque_formula(
        ring_system.M_rated, ring_system.CF
    )
    formula_max, substitution_max, _ = SymbolicFormula.max_gm_torque_formula(
        ring_system.M_max, ring_system.CF
    )

    steps.append({
        'number': '6',
        'title': 'Derived Limits (Reverse Calculations)',
        'description': 'Calculate acceptable ranges for motor torques',
        'inputs': [
            {'label': 'M_{rated}', 'value': ring_system.M_rated, 'unit': 'Nm', 'source': 'System constant'},
            {'label': 'M_{max}', 'value': ring_system.M_max, 'unit': 'Nm', 'source': 'System constant'},
            {'label': 'CF', 'value': ring_system.CF, 'unit': '–', 'source': 'System constant'},
        ],
        'sub_steps': [
            {
                'formula': formula_nom,
                'substitution': substitution_nom,
                'output': f'{T_gm_nom_req:.1f}',
            },
            {
                'formula': formula_max,
                'substitution': substitution_max,
                'output': f'{T_gm_start_max:.1f}',
            },
        ],
    })

    return steps


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
