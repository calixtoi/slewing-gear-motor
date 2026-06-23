"""
Formula display builder for clean, readable calculation breakdown.
Converts formulas into step-by-step visual format without raw LaTeX.
"""


class FormulaDisplay:
    """Build human-readable formula displays instead of raw LaTeX."""

    @staticmethod
    def power_consistency_breakdown(P_val, T_nom_val, n_gm_val, k=9549.3):
        """
        Display ΔP calculation step-by-step.

        Returns dict with formatted display components.
        """
        # Step 1: Calculate power from torque and speed
        P_calc = (T_nom_val * n_gm_val) / k

        # Step 2: Calculate absolute difference
        P_diff = abs(P_val - P_calc)

        # Step 3: Calculate percentage
        dP_percent = (P_diff / P_val) * 100

        return {
            'formula_name': 'Power Consistency Check',
            'formula_text': 'ΔP = |P - (T_nom × n_gm / k)| / P × 100%',

            'variables': [
                {'symbol': 'P', 'description': 'Motor rated power (kW)', 'value': P_val},
                {'symbol': 'T_nom', 'description': 'GM nominal torque (Nm)', 'value': T_nom_val},
                {'symbol': 'n_gm', 'description': 'GM output speed (rpm)', 'value': n_gm_val},
                {'symbol': 'k', 'description': 'Torque constant (60000/2π)', 'value': k},
            ],

            'breakdown': [
                {
                    'step': 1,
                    'description': 'Calculate power from torque and speed',
                    'expression': f'P_calc = T_nom × n_gm / k',
                    'values': f'{T_nom_val} × {n_gm_val} / {k:.1f}',
                    'result': f'{P_calc:.4f} kW',
                },
                {
                    'step': 2,
                    'description': 'Calculate absolute difference from declared power',
                    'expression': f'P_diff = |P - P_calc|',
                    'values': f'|{P_val} - {P_calc:.4f}|',
                    'result': f'{P_diff:.4f} kW',
                },
                {
                    'step': 3,
                    'description': 'Calculate deviation percentage',
                    'expression': f'ΔP = P_diff / P × 100%',
                    'values': f'{P_diff:.4f} / {P_val} × 100%',
                    'result': f'{dP_percent:.2f}%',
                }
            ],

            'final_result': {
                'symbol': 'ΔP',
                'value': dP_percent,
                'unit': '%',
                'interpretation': 'Power consistency deviation',
                'acceptance': 'ΔP ≤ 5%',
                'status': 'PASS' if dP_percent <= 5 else 'FAIL',
            }
        }

    @staticmethod
    def gm_output_speed_breakdown(n_mot, i_gb):
        """Display n_gm calculation."""
        n_gm = n_mot / i_gb

        return {
            'formula_name': 'GM Output Speed',
            'formula_text': 'n_gm = n_mot / i_gb',

            'variables': [
                {'symbol': 'n_mot', 'description': 'Motor rated speed (rpm)', 'value': n_mot},
                {'symbol': 'i_gb', 'description': 'Gearbox reduction ratio (:1)', 'value': i_gb},
            ],

            'calculation': {
                'expression': 'n_gm = n_mot / i_gb',
                'substitution': f'n_gm = {n_mot} / {i_gb}',
                'result': f'{n_gm:.2f}',
            },

            'final_result': {
                'symbol': 'n_gm',
                'value': n_gm,
                'unit': 'rpm',
                'interpretation': 'Speed at gearbox output',
            }
        }

    @staticmethod
    def total_reduction_breakdown(i_gb, i_slew):
        """Display i_tot calculation."""
        i_tot = i_gb * i_slew

        return {
            'formula_name': 'Total Reduction Ratio',
            'formula_text': 'i_tot = i_gb × i_slew',

            'variables': [
                {'symbol': 'i_gb', 'description': 'Gearbox reduction ratio (:1)', 'value': i_gb},
                {'symbol': 'i_slew', 'description': 'Slewing ring reduction ratio (:1)', 'value': i_slew},
            ],

            'calculation': {
                'expression': 'i_tot = i_gb × i_slew',
                'substitution': f'i_tot = {i_gb} × {i_slew}',
                'result': f'{i_tot:.2f}',
            },

            'final_result': {
                'symbol': 'i_tot',
                'value': i_tot,
                'unit': ':1',
                'interpretation': 'Total reduction from motor to ring',
            }
        }

    @staticmethod
    def slewing_speed_breakdown(n_mot, i_tot, n_slew_tgt=None):
        """Display n_slew calculation."""
        n_slew = n_mot / i_tot

        breakdown = {
            'formula_name': 'Crane Slewing Speed',
            'formula_text': 'n_slew = n_mot / i_tot',

            'variables': [
                {'symbol': 'n_mot', 'description': 'Motor rated speed (rpm)', 'value': n_mot},
                {'symbol': 'i_tot', 'description': 'Total reduction ratio (:1)', 'value': i_tot},
            ],

            'calculation': {
                'expression': 'n_slew = n_mot / i_tot',
                'substitution': f'n_slew = {n_mot} / {i_tot:.2f}',
                'result': f'{n_slew:.4f}',
            },

            'final_result': {
                'symbol': 'n_slew',
                'value': n_slew,
                'unit': 'rpm',
                'interpretation': 'Final crane slewing speed at the ring',
            }
        }

        if n_slew_tgt:
            deviation = abs(n_slew - n_slew_tgt) / n_slew_tgt * 100
            breakdown['final_result']['target'] = n_slew_tgt
            breakdown['final_result']['deviation_percent'] = deviation

        return breakdown

    @staticmethod
    def ring_torque_breakdown(torque_type, T_value, CF):
        """Display ring torque calculation M = T × CF."""
        M_value = T_value * CF

        type_map = {
            'nom': ('M_S2', 'Ring nominal torque'),
            'pu': ('M_PU', 'Ring pull-up torque'),
            'start': ('M_start', 'Ring starting torque'),
            'peak': ('M_peak', 'Ring peak torque'),
        }

        symbol, description = type_map.get(torque_type, ('M', 'Ring torque'))

        T_label = {
            'nom': 'T_nom',
            'pu': 'T_pu',
            'start': 'T_start',
            'peak': 'T_peak',
        }.get(torque_type)

        return {
            'formula_name': description,
            'formula_text': f'{symbol} = {T_label} × CF',

            'variables': [
                {'symbol': T_label, 'description': 'GM torque (Nm)', 'value': T_value},
                {'symbol': 'CF', 'description': 'Combined factor (:1)', 'value': CF},
            ],

            'calculation': {
                'expression': f'{symbol} = {T_label} × CF',
                'substitution': f'{symbol} = {T_value} × {CF}',
                'result': f'{M_value:.0f}',
            },

            'final_result': {
                'symbol': symbol,
                'value': M_value,
                'unit': 'Nm',
                'interpretation': description,
            }
        }
