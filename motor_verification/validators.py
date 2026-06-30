"""Validation logic for motor supplier specifications."""

from cover.models import DesignParameters


def validate_supplier(supplier, design_params=None):
    """
    Validate a MotorSupplier against design requirements.

    Returns a dict mapping field_name → {"status": "PASS"|"FAIL"|"CHECK", "message": "..."}
    """
    if design_params is None:
        design_params = DesignParameters.get_or_create_default()

    # Compute required values
    gearmotor_output_speed_min = (
        design_params.crane_min_slewing_speed_rpm
        * design_params.slewing_ring_ratio_pm401
    )
    gearmotor_output_speed_max = (
        design_params.crane_max_slewing_speed_rpm
        * design_params.slewing_ring_ratio_pm401
    )
    required_gearmotor_output_torque = (
        design_params.motor_torque_share_fraction
        * design_params.crane_peak_torque_substation_kNm
        * 1000
        / design_params.slewing_ring_ratio_pm401
    )
    gearbox_ratio_min = (
        1390
        / (design_params.crane_max_slewing_speed_rpm * design_params.slewing_ring_ratio_pm401)
    )
    gearbox_ratio_max = (
        1465
        / (design_params.crane_min_slewing_speed_rpm * design_params.slewing_ring_ratio_pm401)
    )
    required_gearmotor_structural_torque = (
        design_params.crane_peak_torque_substation_kNm
        * 1000
        / design_params.slewing_ring_ratio_pm401
    )

    results = {}

    # Gearmotor output speed
    if supplier.gearmotor_output_speed_rpm is None:
        results['gearmotor_output_speed_rpm'] = {
            'status': 'CHECK',
            'message': 'Value not provided',
        }
    elif gearmotor_output_speed_min <= supplier.gearmotor_output_speed_rpm <= gearmotor_output_speed_max:
        results['gearmotor_output_speed_rpm'] = {
            'status': 'PASS',
            'message': f'{supplier.gearmotor_output_speed_rpm:.1f} rpm within range {gearmotor_output_speed_min:.1f}–{gearmotor_output_speed_max:.1f} rpm',
        }
    else:
        results['gearmotor_output_speed_rpm'] = {
            'status': 'FAIL',
            'message': f'{supplier.gearmotor_output_speed_rpm:.1f} rpm is outside the required range of {gearmotor_output_speed_min:.1f}–{gearmotor_output_speed_max:.1f} rpm',
        }

    # Gearmotor output torque
    if supplier.gearmotor_output_torque_nm is None:
        results['gearmotor_output_torque_nm'] = {
            'status': 'CHECK',
            'message': 'Value not provided',
        }
    elif supplier.gearmotor_output_torque_nm >= required_gearmotor_output_torque:
        results['gearmotor_output_torque_nm'] = {
            'status': 'PASS',
            'message': f'{supplier.gearmotor_output_torque_nm:.1f} N·m meets minimum {required_gearmotor_output_torque:.1f} N·m',
        }
    else:
        results['gearmotor_output_torque_nm'] = {
            'status': 'FAIL',
            'message': f'{supplier.gearmotor_output_torque_nm:.1f} Newton-metres is below the minimum {required_gearmotor_output_torque:.1f} Newton-metres',
        }

    # Gearbox internal ratio
    if supplier.gearbox_internal_ratio is None:
        results['gearbox_internal_ratio'] = {
            'status': 'CHECK',
            'message': 'Value not provided',
        }
    elif gearbox_ratio_min <= supplier.gearbox_internal_ratio <= gearbox_ratio_max:
        results['gearbox_internal_ratio'] = {
            'status': 'PASS',
            'message': f'{supplier.gearbox_internal_ratio:.2f} within range {gearbox_ratio_min:.2f}–{gearbox_ratio_max:.2f}',
        }
    else:
        results['gearbox_internal_ratio'] = {
            'status': 'FAIL',
            'message': f'Ratio {supplier.gearbox_internal_ratio:.2f} is outside required range {gearbox_ratio_min:.2f}–{gearbox_ratio_max:.2f}',
        }

    # Max permissible input speed
    if supplier.max_permissible_input_speed_rpm is None:
        results['max_permissible_input_speed_rpm'] = {
            'status': 'CHECK',
            'message': 'Value not provided',
        }
    elif 1390 <= supplier.max_permissible_input_speed_rpm <= 1465:
        results['max_permissible_input_speed_rpm'] = {
            'status': 'PASS',
            'message': f'{supplier.max_permissible_input_speed_rpm:.0f} rpm within 4-pole band',
        }
    else:
        results['max_permissible_input_speed_rpm'] = {
            'status': 'FAIL',
            'message': f'{supplier.max_permissible_input_speed_rpm:.0f} rpm outside 1390–1465 rpm band',
        }

    # Motor rated power
    if supplier.motor_rated_power_kw is None:
        results['motor_rated_power_kw'] = {
            'status': 'CHECK',
            'message': 'Value not provided',
        }
    elif 0.75 <= supplier.motor_rated_power_kw <= 1.50:
        results['motor_rated_power_kw'] = {
            'status': 'PASS',
            'message': f'{supplier.motor_rated_power_kw:.2f} kW within range 0.75–1.50 kW',
        }
    else:
        results['motor_rated_power_kw'] = {
            'status': 'FAIL',
            'message': f'{supplier.motor_rated_power_kw:.2f} kW outside range 0.75–1.50 kW',
        }

    # Motor rated speed
    if supplier.motor_rated_speed_rpm is None:
        results['motor_rated_speed_rpm'] = {
            'status': 'CHECK',
            'message': 'Value not provided',
        }
    elif 1390 <= supplier.motor_rated_speed_rpm <= 1465:
        results['motor_rated_speed_rpm'] = {
            'status': 'PASS',
            'message': f'{supplier.motor_rated_speed_rpm:.0f} rpm within 4-pole band',
        }
    else:
        results['motor_rated_speed_rpm'] = {
            'status': 'FAIL',
            'message': f'{supplier.motor_rated_speed_rpm:.0f} rpm outside 1390–1465 rpm band',
        }

    # Motor rated torque (computed from power and speed)
    if supplier.motor_rated_power_kw is not None and supplier.motor_rated_speed_rpm is not None:
        computed_torque = 9550 * supplier.motor_rated_power_kw / supplier.motor_rated_speed_rpm
        min_torque = required_gearmotor_output_torque / gearbox_ratio_max
        max_torque = required_gearmotor_output_torque / gearbox_ratio_min
        if min_torque <= computed_torque <= max_torque:
            results['motor_rated_torque'] = {
                'status': 'PASS',
                'message': f'Computed {computed_torque:.2f} N·m within {min_torque:.2f}–{max_torque:.2f} N·m',
            }
        else:
            results['motor_rated_torque'] = {
                'status': 'FAIL',
                'message': f'Computed {computed_torque:.2f} N·m outside {min_torque:.2f}–{max_torque:.2f} N·m',
            }
    else:
        results['motor_rated_torque'] = {
            'status': 'CHECK',
            'message': 'Cannot compute (power or speed missing)',
        }

    # Protection class (IP66)
    if supplier.protection_class is None or supplier.protection_class == '':
        results['protection_class'] = {
            'status': 'CHECK',
            'message': 'Not provided',
        }
    elif 'IP66' in supplier.protection_class.upper() or 'IP 66' in supplier.protection_class.upper():
        results['protection_class'] = {
            'status': 'PASS',
            'message': f'IP66 requirement met: {supplier.protection_class}',
        }
    else:
        results['protection_class'] = {
            'status': 'FAIL',
            'message': f'{supplier.protection_class} does not meet IP66 requirement',
        }

    # Gearbox structural capacity
    if supplier.gearbox_structural_capacity_nm is None:
        results['gearbox_structural_capacity_nm'] = {
            'status': 'CHECK',
            'message': 'Value not provided',
        }
    elif supplier.gearbox_structural_capacity_nm >= required_gearmotor_structural_torque:
        results['gearbox_structural_capacity_nm'] = {
            'status': 'PASS',
            'message': f'{supplier.gearbox_structural_capacity_nm:.1f} N·m meets minimum {required_gearmotor_structural_torque:.1f} N·m',
        }
    else:
        results['gearbox_structural_capacity_nm'] = {
            'status': 'FAIL',
            'message': f'{supplier.gearbox_structural_capacity_nm:.1f} N·m below minimum {required_gearmotor_structural_torque:.1f} N·m',
        }

    # Computed crane slewing speed
    if supplier.gearmotor_output_speed_rpm is not None:
        computed_crane_speed = (
            supplier.gearmotor_output_speed_rpm
            / design_params.slewing_ring_ratio_pm401
        )
        if design_params.crane_min_slewing_speed_rpm <= computed_crane_speed <= design_params.crane_max_slewing_speed_rpm:
            results['crane_slewing_speed'] = {
                'status': 'PASS',
                'message': f'Computed {computed_crane_speed:.2f} rpm within window {design_params.crane_min_slewing_speed_rpm}–{design_params.crane_max_slewing_speed_rpm} rpm',
            }
        else:
            results['crane_slewing_speed'] = {
                'status': 'FAIL',
                'message': f'Computed {computed_crane_speed:.2f} rpm outside {design_params.crane_min_slewing_speed_rpm}–{design_params.crane_max_slewing_speed_rpm} rpm window',
            }
    else:
        results['crane_slewing_speed'] = {
            'status': 'CHECK',
            'message': 'Cannot compute (output speed not provided)',
        }

    # Categorical fields
    categorical_fields = [
        ('gear_series', 'Helical bevel'),
        ('housing_material', 'Cast iron'),
        ('duty_cycle', 'S3-25%'),
        ('efficiency_class', ['IE2', 'IE3']),
        ('painting_system', ['C5H', 'C5M']),
        ('colour_ral', ['7035', 'RAL']),
        ('cooling_method', ['IC410', 'TENV']),
        ('certifications', ['CE', 'EN 10204']),
        ('corrosivity_category', 'C5'),
        ('temperature_range', '-20'),
        ('rotation', 'Clockwise'),
        ('starting_method', 'Direct'),
    ]

    for field_name, requirement in categorical_fields:
        value = getattr(supplier, field_name, '')
        if not value or value == '':
            results[field_name] = {
                'status': 'CHECK',
                'message': 'Not provided — needs review',
            }
        else:
            if isinstance(requirement, list):
                if any(req.lower() in value.lower() for req in requirement):
                    results[field_name] = {
                        'status': 'PASS',
                        'message': value,
                    }
                else:
                    results[field_name] = {
                        'status': 'CHECK',
                        'message': f'{value} — needs manual review',
                    }
            else:
                if requirement.lower() in value.lower():
                    results[field_name] = {
                        'status': 'PASS',
                        'message': value,
                    }
                else:
                    results[field_name] = {
                        'status': 'CHECK',
                        'message': f'{value} — check if acceptable',
                    }

    return results


def get_supplier_summary(supplier, design_params=None):
    """Get a summary of pass/fail/check counts for a supplier."""
    validation_results = validate_supplier(supplier, design_params)

    pass_count = sum(1 for v in validation_results.values() if v['status'] == 'PASS')
    fail_count = sum(1 for v in validation_results.values() if v['status'] == 'FAIL')
    check_count = sum(1 for v in validation_results.values() if v['status'] == 'CHECK')

    if fail_count > 0:
        overall = 'NOT FIT'
    elif check_count >= 5:
        overall = 'REVIEW'
    else:
        overall = 'SUITABLE'

    return {
        'pass_count': pass_count,
        'fail_count': fail_count,
        'check_count': check_count,
        'overall': overall,
    }
