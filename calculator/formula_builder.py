"""
Professional formula builder using SymPy for canonical LaTeX output.
Generates human-readable, scientifically-formatted mathematical expressions.
"""

import sympy as sp
from sympy import symbols, Rational, latex, Abs, simplify, pi
from decimal import Decimal


class FormulaStep:
    """Represents a single calculation step with inputs, formula, and output."""

    def __init__(self, title: str, description: str = ""):
        self.title = title
        self.description = description
        self.inputs = {}
        self.formula_latex = ""
        self.substitution_latex = ""
        self.output_latex = ""
        self.output_value = None
        self.output_unit = ""
        self.constraints = []

    def set_formula(self, latex_str: str):
        """Set the formula in LaTeX format."""
        self.formula_latex = latex_str
        return self

    def add_input(self, label: str, value, unit: str, source: str):
        """Add an input parameter."""
        self.inputs[label] = {
            'value': value,
            'unit': unit,
            'source': source,
        }
        return self

    def set_substitution(self, latex_str: str):
        """Set the formula with values substituted."""
        self.substitution_latex = latex_str
        return self

    def set_output(self, label: str, value, unit: str):
        """Set the output value."""
        self.output_latex = label
        self.output_value = value
        self.output_unit = unit
        return self

    def add_constraint(self, description: str, passes: bool = None):
        """Add a constraint check."""
        self.constraints.append({
            'description': description,
            'passes': passes,
        })
        return self

    def to_dict(self):
        """Convert to dictionary for template rendering."""
        return {
            'title': self.title,
            'description': self.description,
            'inputs': list(self.inputs.items()),
            'formula': self.formula_latex,
            'substitution': self.substitution_latex,
            'output': {
                'label': self.output_latex,
                'value': self.output_value,
                'unit': self.output_unit,
            },
            'constraints': self.constraints,
        }


class SymbolicFormula:
    """Generate canonical LaTeX from symbolic expressions."""

    # Torque constant: P = T × n / 9549.3
    k = Decimal('9549.2959')

    @staticmethod
    def format_number(value, decimals=2, use_siunit=False):
        """Format a number for display."""
        if value is None:
            return "N/A"
        if isinstance(value, (int, float)):
            return f"{value:.{decimals}f}"
        return str(value)

    @staticmethod
    def cf_formula(i_slew, eta_slew):
        """
        Combined Factor: CF = i_slew × η_slew
        Returns: (formula_latex, substitution_latex, value)
        """
        # Symbol formula
        i_s = symbols('i_{slew}', positive=True, real=True)
        eta_s = symbols('eta_{slew}', positive=True, real=True)
        formula = i_s * eta_s

        formula_latex = latex(formula, mode='equation*')
        # Better formatting
        formula_latex = r'CF = i_{\text{slew}} \times \eta_{\text{slew}}'

        # Substitution
        cf_value = i_slew * eta_slew
        substitution = (
            r'CF = ' + f'{i_slew}' + r' \times ' + f'{eta_slew}' +
            r' = ' + f'{cf_value:.1f}'
        )

        return formula_latex, substitution, cf_value

    @staticmethod
    def total_reduction_formula(i_gb, i_slew):
        """
        Total Reduction: i_tot = i_gb × i_slew
        """
        formula_latex = r'i_{\text{tot}} = i_{\text{gb}} \times i_{\text{slew}}'

        i_tot_value = i_gb * i_slew
        substitution = (
            r'i_{\text{tot}} = ' + f'{i_gb}' + r' \times ' + f'{i_slew}' +
            r' = ' + f'{i_tot_value:.2f}'
        )

        return formula_latex, substitution, i_tot_value

    @staticmethod
    def gm_output_speed_formula(n_mot, i_gb):
        """
        GM Output Speed: n_gm = n_mot / i_gb
        """
        formula_latex = r'n_{\text{gm}} = \frac{n_{\text{mot}}}{i_{\text{gb}}}'

        n_gm_value = n_mot / i_gb
        substitution = (
            r'n_{\text{gm}} = \frac{' + f'{n_mot}' + r'}{' + f'{i_gb}' +
            r'} = ' + f'{n_gm_value:.2f}'
        )

        return formula_latex, substitution, n_gm_value

    @staticmethod
    def slewing_speed_formula(n_mot, i_tot):
        """
        Crane Slewing Speed: n_slew = n_mot / i_tot
        """
        formula_latex = r'n_{\text{slew}} = \frac{n_{\text{mot}}}{i_{\text{tot}}}'

        n_slew_value = n_mot / i_tot
        substitution = (
            r'n_{\text{slew}} = \frac{' + f'{n_mot}' + r'}{' + f'{i_tot:.2f}' +
            r'} = ' + f'{n_slew_value:.4f}'
        )

        return formula_latex, substitution, n_slew_value

    @staticmethod
    def power_consistency_formula(P, T_nom, n_gm, k=9549.3):
        """
        Power Consistency: ΔP = |P - (T_nom × n_gm / k)| / P × 100%
        """
        formula_latex = (
            r'\Delta P = 100 \times \frac{\left| P - \frac{T_{\text{nom}} \times n_{\text{gm}}}{k} \right|}{P}'
        )

        P_calc = (T_nom * n_gm) / k
        dP_percent = abs(P - P_calc) / P * 100

        substitution = (
            r'\Delta P = 100 \times \frac{\left| ' + f'{P}' +
            r' - \frac{' + f'{T_nom} \times {n_gm:.2f}' + r'}{' + f'{k:.1f}' +
            r'} \right|}{' + f'{P}' + r'} = ' + f'{dP_percent:.2f}'
        )

        return formula_latex, substitution, dP_percent

    @staticmethod
    def ring_torque_formula(torque_type, T_value, CF):
        """
        Ring Torques: M = T × CF
        torque_type: 'nom', 'pu', 'start', 'peak'
        """
        type_map = {
            'nom': (r'M_{S2}', 'Ring nominal torque'),
            'pu': (r'M_{\text{PU}}', 'Ring pull-up torque'),
            'start': (r'M_{\text{start}}', 'Ring start torque'),
            'peak': (r'M_{\text{peak}}', 'Ring peak torque'),
        }

        type_label, _ = type_map.get(torque_type, (r'M', 'Ring torque'))
        T_label = {
            'nom': r'T_{\text{nom}}',
            'pu': r'T_{\text{pu}}',
            'start': r'T_{\text{start}}',
            'peak': r'T_{\text{peak}}',
        }.get(torque_type)

        formula_latex = f'{type_label} = {T_label} \\times CF'

        M_value = T_value * CF if T_value else None
        substitution = (
            f'{type_label} = ' + (
                f'{T_value} \\times {CF} = {M_value:.0f}' if T_value
                else 'Not provided'
            )
        )

        return formula_latex, substitution, M_value

    @staticmethod
    def required_gm_torque_formula(M_rated, CF):
        """
        Required GM Torque: T_gm_nom_req = M_rated / CF
        """
        formula_latex = r'T_{\text{gm,nom,req}} = \frac{M_{\text{rated}}}{CF}'

        T_req = M_rated / CF
        substitution = (
            r'T_{\text{gm,nom,req}} = \frac{' + f'{M_rated}' + r'}{' +
            f'{CF}' + r'} = ' + f'{T_req:.1f}'
        )

        return formula_latex, substitution, T_req

    @staticmethod
    def max_gm_torque_formula(M_max, CF):
        """
        Maximum GM Torque: T_gm_start_max = M_max / CF
        """
        formula_latex = r'T_{\text{gm,start,max}} = \frac{M_{\text{max}}}{CF}'

        T_max = M_max / CF
        substitution = (
            r'T_{\text{gm,start,max}} = \frac{' + f'{M_max}' + r'}{' +
            f'{CF}' + r'} = ' + f'{T_max:.1f}'
        )

        return formula_latex, substitution, T_max


def render_formula_card(title: str, formula: str, description: str = ""):
    """Render a formula card HTML snippet."""
    return f"""
    <div class="formula-card">
      <div class="formula-header">
        <strong>{title}</strong>
        {f'<small class="text-muted">{description}</small>' if description else ''}
      </div>
      <div class="formula-display">
        $${ formula }$$
      </div>
    </div>
    """
