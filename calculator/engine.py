"""Core drivetrain sizing calculations (motor → bevel gearbox → worm gear → slewing ring)."""


SAFETY_FACTOR = 1.34  # Z-Systems sizing sheet constant
DEFAULT_BEVEL_EFFICIENCY = 0.95


def _check(value, required, label):
    if value is None:
        return None
    margin = value / required
    if margin >= 1.10:
        status = 'OK'
    elif margin >= 1.00:
        status = 'Marginal'
    else:
        status = 'Too small'
    return {
        'label': label,
        'supplied': round(value, 3),
        'required': round(required, 3),
        'margin': round(margin, 3),
        'status': status,
    }


def _ratio_check(value, calculated, label):
    if value is None:
        return None
    deviation = abs(value - calculated) / calculated
    status = 'OK' if deviation <= 0.02 else 'Mismatch'
    return {
        'label': label,
        'supplied': round(value, 3),
        'calculated': round(calculated, 3),
        'deviation_pct': round(deviation * 100, 2),
        'status': status,
    }


def drivetrain_sizing(
    crane_torque_max,
    worm_ratio,
    worm_efficiency,
    motor_speed,
    gearbox_output_speed,
    motor_rated_torque,
    starting_factor,
    bevel_efficiency=DEFAULT_BEVEL_EFFICIENCY,
    crane_torque_nom=None,
    supplier_motor_power_kw=None,
    supplier_motor_rated_torque=None,
    supplier_motor_starting_torque=None,
    supplier_gearbox_rated_torque=None,
    supplier_bevel_ratio=None,
    supplier_worm_ratio=None,
):
    r = {}

    # ── Step 1 — Worm shaft torque (maximum) ─────────────────────────────────
    # M2_Max = M_Max / (i_worm × η_worm)
    r['worm_input_torque_max'] = crane_torque_max / (worm_ratio * worm_efficiency)

    # ── Step 2 — Worm shaft torque (nominal) ─────────────────────────────────
    # Path A (preferred): top-down from nominal crane torque
    # Path B (fallback):  back-calculate from motor rated torque
    #   M2_nom = M_n × i_worm × η_worm  →  nominal torque the motor continuously delivers
    if crane_torque_nom is not None:
        r['worm_input_torque_nom'] = crane_torque_nom / (worm_ratio * worm_efficiency)
        r['step2_source'] = 'crane_torque_nom'
    else:
        r['worm_input_torque_nom'] = motor_rated_torque * worm_ratio * worm_efficiency
        r['step2_source'] = 'motor_rated_torque'

    # ── Step 3 — Required gearbox output torque ───────────────────────────────
    r['gearbox_required_torque'] = r['worm_input_torque_nom'] * SAFETY_FACTOR

    # ── Step 4 — Bevel gearbox ratio ─────────────────────────────────────────
    r['n_gear_out'] = gearbox_output_speed
    r['bevel_ratio'] = motor_speed / gearbox_output_speed

    # ── Step 5 — Slewing speed ────────────────────────────────────────────────
    r['slewing_speed_rpm'] = gearbox_output_speed / worm_ratio

    # ── Step 6 — Motor torque required (includes bevel gearbox efficiency) ────
    # M_motor_req = M2_Max / (i_bevel × η_bevel)
    r['bevel_efficiency'] = bevel_efficiency
    r['motor_torque_required'] = r['worm_input_torque_max'] / (r['bevel_ratio'] * bevel_efficiency)

    # ── Step 7 — Motor starting torque available ──────────────────────────────
    r['motor_start_torque'] = motor_rated_torque * starting_factor

    # ── Step 8 — Torque feasibility check ────────────────────────────────────
    margin = r['motor_start_torque'] / r['motor_torque_required']
    r['torque_margin'] = margin
    if margin < 1.0:
        r['torque_check'] = 'CRITICAL FAIL'
    elif margin < 1.5:
        r['torque_check'] = 'Low Margin'
    else:
        r['torque_check'] = 'OK'

    # ── Step 9 — Motor rated power (nameplate) ────────────────────────────────
    r['motor_power_kw'] = (motor_rated_torque * motor_speed) / 9550

    # ── Optional gearbox sizing (load spectrum method) ────────────────────────
    M2n = r['worm_input_torque_nom']
    M2a = r['worm_input_torque_max']
    lam = M2n / M2a
    M_soll = M2n + (M2a - M2n) * lam
    r['gb_load_spectrum_ratio'] = round(lam, 4)
    r['gb_sizing_torque'] = round(M_soll, 3)

    # ── Supplier data checks ──────────────────────────────────────────────────
    supplier_checks = []

    sc = _check(supplier_motor_starting_torque, r['motor_torque_required'],
                'Motor starting torque Ma vs required')
    if sc:
        supplier_checks.append(sc)

    sc = _check(supplier_motor_rated_torque, motor_rated_torque,
                'Motor rated torque M_n vs input')
    if sc:
        supplier_checks.append(sc)

    sc = _check(supplier_motor_power_kw, r['motor_power_kw'],
                'Motor power vs required')
    if sc:
        supplier_checks.append(sc)

    sc = _check(supplier_gearbox_rated_torque, r['gearbox_required_torque'],
                'Gearbox rated torque vs required')
    if sc:
        supplier_checks.append(sc)

    sc = _ratio_check(supplier_bevel_ratio, r['bevel_ratio'],
                      'Bevel ratio vs calculated')
    if sc:
        supplier_checks.append(sc)

    sc = _ratio_check(supplier_worm_ratio, worm_ratio,
                      'Worm ratio vs input')
    if sc:
        supplier_checks.append(sc)

    r['supplier_checks'] = supplier_checks
    checks_passed = None
    if supplier_checks:
        all_statuses = [c['status'] for c in supplier_checks]
        if all(s == 'OK' for s in all_statuses):
            checks_passed = 'ALL OK'
        elif any(s == 'Too small' or s == 'Mismatch' for s in all_statuses):
            checks_passed = 'FAIL'
        else:
            checks_passed = 'MARGINAL'
    r['supplier_overall'] = checks_passed

    # Round numeric results
    for key in ('worm_input_torque_max', 'worm_input_torque_nom',
                'gearbox_required_torque', 'n_gear_out', 'bevel_ratio',
                'slewing_speed_rpm', 'motor_torque_required',
                'motor_start_torque', 'torque_margin', 'motor_power_kw'):
        if r[key] is not None:
            r[key] = round(r[key], 3)

    return r
