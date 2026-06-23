"""
Pure calculation and validation functions for motor sizing.
No Django dependencies — easy to unit-test.
"""


def evaluate(motor_input: dict, ring_system) -> dict:
    """
    Evaluate a motor candidate against a ring system.

    Args:
        motor_input: dict with keys i_gb, n_mot, P, T_nom, T_pu, T_start, T_peak, T_in_max, T_bd, fB, duty, flange
        ring_system: RingSystem instance (PF Standard or PF-XXL)

    Returns:
        dict with calculated values and 11-point checks
    """

    # Extract inputs
    i_gb = motor_input.get('i_gb', 0)
    n_mot = motor_input.get('n_mot', 0)
    P = motor_input.get('P', 0)
    T_nom = motor_input.get('T_nom', 0)
    T_pu = motor_input.get('T_pu')  # Optional
    T_start = motor_input.get('T_start', 0)
    T_peak = motor_input.get('T_peak', 0)
    T_in_max = motor_input.get('T_in_max')  # Optional
    T_bd = motor_input.get('T_bd')  # Optional
    fB = motor_input.get('fB')  # Optional
    duty = motor_input.get('duty', '')
    flange = motor_input.get('flange', '')

    # Ring system parameters
    i_slew = ring_system.i_slew
    eta_slew = ring_system.eta_slew
    CF = ring_system.CF
    M_max = ring_system.M_max
    M_rated = ring_system.M_rated
    n_slew_min = ring_system.n_slew_min
    n_slew_max = ring_system.n_slew_max
    n_slew_tgt = ring_system.n_slew_tgt
    n_gm_min = ring_system.n_gm_min
    n_gm_max = ring_system.n_gm_max
    k = ring_system.k

    # Calculations
    i_tot = i_gb * i_slew if i_gb and i_slew else 0
    n_gm = n_mot / i_gb if i_gb and n_mot else 0
    n_slew = n_mot / i_tot if i_tot and n_mot else 0
    dP = abs(P - T_nom * n_gm / k) / P if P and T_nom and n_gm else None

    # Ring-level torques
    M_S2 = T_nom * CF if T_nom and CF else 0
    M_PU = T_pu * CF if T_pu and CF else None
    M_start = T_start * CF if T_start and CF else 0
    M_peak = T_peak * CF if T_peak and CF else 0

    # Derived limits
    T_gm_nom_req = M_rated / CF if CF else 0
    T_gm_start_max = M_max / CF if CF else 0

    # Run the 11-point checks
    checks = {}

    # 1. Crane speed in range
    checks['1_crane_speed'] = {
        'label': '1. Crane speed in range (n_slew_min ≤ n_slew ≤ n_slew_max)',
        'expected': f'{n_slew_min}–{n_slew_max} rpm',
        'actual': f'{n_slew:.3f} rpm' if n_slew else 'N/A',
        'status': 'PASS' if (n_slew and n_slew_min <= n_slew <= n_slew_max) else 'FAIL',
    }

    # 2. GM output speed in range
    checks['2_gm_speed'] = {
        'label': '2. GM output speed in range (n_gm_min ≤ n_gm ≤ n_gm_max)',
        'expected': f'{n_gm_min}–{n_gm_max} rpm',
        'actual': f'{n_gm:.1f} rpm' if n_gm else 'N/A',
        'status': 'PASS' if (n_gm and n_gm_min <= n_gm <= n_gm_max) else 'FAIL',
    }

    # 3. Speed near target (±10%)
    speed_err = abs(n_slew - n_slew_tgt) / n_slew_tgt if (n_slew and n_slew_tgt) else None
    checks['3_speed_target'] = {
        'label': '3. Speed near target (±10%): |n_slew - n_slew_tgt| / n_slew_tgt ≤ 0.10',
        'expected': f'±{n_slew_tgt * 0.1:.3f} rpm (target {n_slew_tgt})',
        'actual': f'{speed_err * 100:.1f}%' if speed_err is not None else 'N/A',
        'status': 'PASS' if (speed_err is not None and speed_err <= 0.10) else 'FAIL',
    }

    # 4. Power consistency (ΔP ≤ 5%)
    checks['4_power'] = {
        'label': '4. Power consistency: ΔP ≤ 5%',
        'expected': '≤ 5%',
        'actual': f'{dP * 100:.1f}%' if dP is not None else 'N/A',
        'status': 'PASS' if (dP is not None and dP <= 0.05) else 'FAIL',
    }

    # 5. Ring pull-up ≥ 90% rated (REVIEW if T_pu missing)
    if M_PU is not None:
        pu_check = M_PU >= 0.9 * M_rated
        checks['5_ring_pullup'] = {
            'label': '5. Ring pull-up ≥ 90% rated: M_PU ≥ 0.9 × M_rated',
            'expected': f'≥ {0.9 * M_rated:,.0f} Nm',
            'actual': f'{M_PU:,.0f} Nm',
            'status': 'PASS' if pu_check else 'FAIL',
        }
    else:
        checks['5_ring_pullup'] = {
            'label': '5. Ring pull-up ≥ 90% rated: M_PU ≥ 0.9 × M_rated',
            'expected': f'≥ {0.9 * M_rated:,.0f} Nm',
            'actual': 'T_pu not provided',
            'status': 'REVIEW',
        }

    # 6. Ring start in band (M_rated ≤ M_start ≤ M_max)
    if M_start:
        start_in_band = M_rated <= M_start <= M_max
        checks['6_ring_start'] = {
            'label': '6. Ring start in band: M_rated ≤ M_start ≤ M_max',
            'expected': f'{M_rated:,.0f}–{M_max:,.0f} Nm',
            'actual': f'{M_start:,.0f} Nm',
            'status': 'PASS' if start_in_band else 'FAIL',
        }
    else:
        checks['6_ring_start'] = {
            'label': '6. Ring start in band: M_rated ≤ M_start ≤ M_max',
            'expected': f'{M_rated:,.0f}–{M_max:,.0f} Nm',
            'actual': 'N/A',
            'status': 'FAIL',
        }

    # 7. Ring peak ≤ ring max (M_peak ≤ M_max)
    if M_peak:
        peak_ok = M_peak <= M_max
        checks['7_ring_peak'] = {
            'label': '7. Ring peak ≤ ring max: M_peak ≤ M_max',
            'expected': f'≤ {M_max:,.0f} Nm',
            'actual': f'{M_peak:,.0f} Nm',
            'status': 'PASS' if peak_ok else 'FAIL',
        }
    else:
        checks['7_ring_peak'] = {
            'label': '7. Ring peak ≤ ring max: M_peak ≤ M_max',
            'expected': f'≤ {M_max:,.0f} Nm',
            'actual': 'N/A',
            'status': 'FAIL',
        }

    # 8. GM start ≤ limit (T_start ≤ T_gm_start_max)
    if T_start:
        gm_start_ok = T_start <= T_gm_start_max
        checks['8_gm_start'] = {
            'label': '8. GM start ≤ limit: T_start ≤ T_gm_start_max',
            'expected': f'≤ {T_gm_start_max:,.0f} Nm',
            'actual': f'{T_start:,.0f} Nm',
            'status': 'PASS' if gm_start_ok else 'FAIL',
        }
    else:
        checks['8_gm_start'] = {
            'label': '8. GM start ≤ limit: T_start ≤ T_gm_start_max',
            'expected': f'≤ {T_gm_start_max:,.0f} Nm',
            'actual': 'N/A',
            'status': 'FAIL',
        }

    # 9. Gearbox input torque OK (T_bd ≤ T_in_max) — REVIEW if T_in_max missing
    if T_bd is not None and T_in_max is not None:
        gb_input_ok = T_bd <= T_in_max
        checks['9_gb_input'] = {
            'label': '9. Gearbox input torque OK: T_bd ≤ T_in_max',
            'expected': f'≤ {T_in_max:,.1f} Nm',
            'actual': f'{T_bd:,.1f} Nm',
            'status': 'PASS' if gb_input_ok else 'FAIL',
        }
    else:
        checks['9_gb_input'] = {
            'label': '9. Gearbox input torque OK: T_bd ≤ T_in_max',
            'expected': f'≤ {T_in_max:,.1f} Nm' if T_in_max else 'N/A',
            'actual': f'{T_bd:,.1f} Nm' if T_bd is not None else 'T_in_max or T_bd not provided',
            'status': 'REVIEW',
        }

    # 10. Duty acceptable (contains "S2-12" or "S3-15" or "S3-25")
    duty_ok = any(x in duty.upper() for x in ['S2-12', 'S3-15', 'S3-25']) if duty else False
    checks['10_duty'] = {
        'label': '10. Duty acceptable: duty in {S2-12, S3-15, S3-25}',
        'expected': 'S2-12, S3-15, or S3-25',
        'actual': duty if duty else 'Not provided',
        'status': 'PASS' if duty_ok else 'FAIL' if duty else 'REVIEW',
    }

    # 11. Flange interface (contains "150")
    flange_ok = '150' in flange if flange else False
    checks['11_flange'] = {
        'label': '11. Flange interface: flange contains "150"',
        'expected': 'Ø150 or □150',
        'actual': flange if flange else 'Not provided',
        'status': 'PASS' if flange_ok else 'FAIL' if flange else 'REVIEW',
    }

    return {
        'i_tot': i_tot,
        'n_gm': n_gm,
        'n_slew': n_slew,
        'dP': dP,
        'M_S2': M_S2,
        'M_PU': M_PU,
        'M_start': M_start,
        'M_peak': M_peak,
        'T_gm_nom_req': T_gm_nom_req,
        'T_gm_start_max': T_gm_start_max,
        'checks': checks,
    }


def verdict(checks: dict) -> str:
    """
    Determine verdict from checks dict.

    Rules:
    - If any check is FAIL → DOES_NOT_FIT
    - Else if any check is REVIEW → FITS_REVIEW
    - Else → FITS
    """
    statuses = [c['status'] for c in checks.values()]

    if 'FAIL' in statuses:
        return 'DOES_NOT_FIT'
    elif 'REVIEW' in statuses:
        return 'FITS_REVIEW'
    else:
        return 'FITS'
