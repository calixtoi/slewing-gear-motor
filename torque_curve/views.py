"""
torque_curve/views.py
=====================
Torque-speed curve chart view.
Shows the induction motor torque curve from 0 RPM to rated speed,
with the four key points annotated and the structural limit line drawn.
Works for any motor — either from KNOWN_MOTORS or from user input.
"""

import json as json_lib
from django.shortcuts import render
from django.http import JsonResponse
from calculator.engine import (
    KNOWN_MOTORS, CRANE_PARAMS, CRANE_STANDARD_PF, CRANE_PF_XXL,
    drivetrain_sizing, size_known_motor,
)


def build_curve_data(result):
    """
    Build the full torque-speed curve dataset for Chart.js.

    The standard induction motor torque-speed curve has this shape:
      - At 0% speed (locked rotor): starting torque (Anlaufdrehmoment)
      - At ~40% speed: pull-up torque (minimum during acceleration)
      - At ~80% speed: breakdown torque (peak / Mk)
      - At 100% speed: nominal torque (rated operating point)

    We generate a smooth curve by interpolating between these four anchor points.
    All torque values are at the GEARBOX OUTPUT SHAFT (Nm).
    Speed values are as a percentage of rated motor speed.
    """
    r = result

    # Four anchor points on the torque-speed curve
    anchors = [
        (0,   r.gm_out_locked_rotor_nm),   # startup — the structural check point
        (40,  r.gm_out_pullup_nm),          # pull-up minimum
        (80,  r.gm_out_breakdown_nm),        # breakdown peak
        (100, r.gm_out_nom_nm),             # rated operating point
    ]

    # Generate smooth curve points using piecewise linear interpolation
    # between the four anchors at every 5% speed step
    curve_points = []
    for i in range(len(anchors) - 1):
        x0, y0 = anchors[i]
        x1, y1 = anchors[i + 1]
        steps = range(x0, x1, 5)
        for x in steps:
            t = (x - x0) / (x1 - x0)
            y = y0 + t * (y1 - y0)
            curve_points.append({'x': x, 'y': round(y, 1)})
    # Add final rated point
    curve_points.append({'x': 100, 'y': round(r.gm_out_nom_nm, 1)})

    # Named annotation points
    named_points = [
        {
            'speed_pct':  0,
            'torque_nm':  round(r.gm_out_locked_rotor_nm, 1),
            'label':      'Locked rotor (startup)',
            'sublabel':   'Anlaufdrehmoment',
            'exceeds_limit': r.gm_out_locked_rotor_nm > r.T_gm_start_MAX,
            'color':      'red' if r.gm_out_locked_rotor_nm > r.T_gm_start_MAX else 'green',
        },
        {
            'speed_pct':  40,
            'torque_nm':  round(r.gm_out_pullup_nm, 1),
            'label':      'Pull-up torque',
            'sublabel':   'Minimum during acceleration',
            'exceeds_limit': False,
            'color':      'blue',
        },
        {
            'speed_pct':  80,
            'torque_nm':  round(r.gm_out_breakdown_nm, 1),
            'label':      'Breakdown torque (Mk)',
            'sublabel':   'Peak before stall',
            'exceeds_limit': False,
            'color':      'orange',
        },
        {
            'speed_pct':  100,
            'torque_nm':  round(r.gm_out_nom_nm, 1),
            'label':      'Rated torque (nominal)',
            'sublabel':   'Normal crane slewing',
            'exceeds_limit': False,
            'color':      'green',
        },
    ]

    return {
        'curve_points':      curve_points,
        'named_points':      named_points,
        'limit_line':        round(r.T_gm_start_MAX, 1),
        'limit_label':       f'Structural limit at GM output: {r.T_gm_start_MAX:,.0f} Nm',
        'rated_speed_rpm':   round(r.motor_speed_rpm, 0),
        'gm_out_speed_rpm':  round(r.gm_out_speed_rpm, 1),
        'crane_label':       r.crane_label,
        'overall_status':    r.overall_status,
        'motor_power_kw':    r.motor_power_kw,
        'i_gb':              round(r.i_gb, 2),
        'i_slew':            r.i_slew,
        'CF':                round(r.CF, 1),
        'T_crane_lim':       r.T_crane_lim,
    }


def torque_curve_index(request):
    """
    Main torque curve page.
    Shows Chart.js torque-speed curves for all known motors,
    plus an input form to plot any motor.
    """
    # Build data for all known motors
    known_results = {}
    for key, motor in KNOWN_MOTORS.items():
        result = size_known_motor(key)
        known_results[key] = {
            'motor':      motor,
            'result':     result,
            'curve_data': build_curve_data(result),
        }

    context = {
        'known_results':    known_results,
        'known_motors':     KNOWN_MOTORS,
        'known_results_json': json_lib.dumps({
            k: v['curve_data'] for k, v in known_results.items()
        }),
        'crane_standard_pf': CRANE_STANDARD_PF,
        'crane_pf_xxl':      CRANE_PF_XXL,
    }
    return render(request, 'torque_curve/index.html', context)


def torque_curve_ajax(request):
    """
    POST JSON with motor parameters → return curve data as JSON for Chart.js.
    Called by the live input form on the torque curve page.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json_lib.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    try:
        result = drivetrain_sizing(
            crane_type        = data.get('crane_type', CRANE_STANDARD_PF),
            motor_power_kw    = float(data['motor_power_kw']),
            motor_speed_rpm   = float(data['motor_speed_rpm']),
            gm_out_speed_rpm  = float(data['gm_out_speed_rpm']),
            gm_out_nom_nm     = float(data['gm_out_nom_nm']),
            gm_out_start_nm   = float(data['gm_out_start_nm']),
            Mk_Mn             = float(data.get('Mk_Mn', 3.40)),
            i_gb              = float(data['i_gb']) if data.get('i_gb') else None,
            gm_out_pullup_nm  = float(data['gm_out_pullup_nm']) if data.get('gm_out_pullup_nm') else None,
        )
        return JsonResponse(build_curve_data(result))
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
