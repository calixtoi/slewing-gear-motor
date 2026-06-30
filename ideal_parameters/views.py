from django.views.generic import TemplateView
from cover.models import DesignParameters


class IdealParametersView(TemplateView):
    """Display the full motor specification requirement table."""
    template_name = 'ideal_parameters/parameters.html'

    def get_context_data(self, **kwargs):
        """Build the complete parameters specification table."""
        context = super().get_context_data(**kwargs)
        design = DesignParameters.get_or_create_default()

        # Computed values
        gearmotor_output_speed_min = (
            design.crane_min_slewing_speed_rpm
            * design.slewing_ring_ratio_pm401
        )
        gearmotor_output_speed_max = (
            design.crane_max_slewing_speed_rpm
            * design.slewing_ring_ratio_pm401
        )
        required_gearmotor_output_torque = (
            design.motor_torque_share_fraction
            * design.crane_peak_torque_substation_kNm
            * 1000
            / design.slewing_ring_ratio_pm401
        )
        gearbox_ratio_min = (
            1390 / (design.crane_max_slewing_speed_rpm * design.slewing_ring_ratio_pm401)
        )
        gearbox_ratio_max = (
            1465 / (design.crane_min_slewing_speed_rpm * design.slewing_ring_ratio_pm401)
        )
        required_gearmotor_structural_torque = (
            design.crane_peak_torque_substation_kNm
            * 1000
            / design.slewing_ring_ratio_pm401
        )
        motor_rated_torque_min = required_gearmotor_output_torque / gearbox_ratio_max
        motor_rated_torque_max = required_gearmotor_output_torque / gearbox_ratio_min

        parameters = [
            # GEAR DATA
            {
                'group': 'Gear data',
                'parameter': 'Gear series',
                'ideal_range': 'Helical bevel geared motors',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Gear data',
                'parameter': 'Gearmotor output speed',
                'ideal_range': f'{gearmotor_output_speed_min:.0f} – {gearmotor_output_speed_max:.0f}',
                'unit': 'revolutions per minute',
                'specification_requirement': f'{design.crane_min_slewing_speed_rpm} to {design.crane_max_slewing_speed_rpm} crane revolutions per minute × slewing ring ratio {design.slewing_ring_ratio_pm401}',
                'calc_min': gearmotor_output_speed_min,
                'calc_max': gearmotor_output_speed_max,
            },
            {
                'group': 'Gear data',
                'parameter': 'Required gearmotor output torque',
                'ideal_range': f'{required_gearmotor_output_torque:.1f} minimum; preferred ≈ 180',
                'unit': 'Newton-metres',
                'specification_requirement': f'30% × {design.crane_peak_torque_substation_kNm} kNm × 1000 ÷ {design.slewing_ring_ratio_pm401}',
                'calc_min': required_gearmotor_output_torque,
                'calc_max': None,
            },
            {
                'group': 'Gear data',
                'parameter': 'Gearbox internal ratio range',
                'ideal_range': f'{gearbox_ratio_min:.2f} – {gearbox_ratio_max:.2f}',
                'unit': 'dimensionless',
                'specification_requirement': f'1390 ÷ ({design.crane_max_slewing_speed_rpm} × {design.slewing_ring_ratio_pm401}) to 1465 ÷ ({design.crane_min_slewing_speed_rpm} × {design.slewing_ring_ratio_pm401})',
                'calc_min': gearbox_ratio_min,
                'calc_max': gearbox_ratio_max,
            },
            {
                'group': 'Gear data',
                'parameter': 'Maximum permissible motor input speed',
                'ideal_range': '1390 – 1465',
                'unit': 'revolutions per minute',
                'specification_requirement': 'Accepted 4-pole motor rated-speed band',
                'calc_min': 1390,
                'calc_max': 1465,
            },
            {
                'group': 'Gear data',
                'parameter': 'Output flange',
                'ideal_range': 'Square flange IEC 200; bolt circle diameter 165 mm; 4 holes diameter 11 mm',
                'unit': 'millimetres',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Gear data',
                'parameter': 'Output shaft (special)',
                'ideal_range': 'Diameter 32 k6 × 50 mm length',
                'unit': 'millimetres',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Gear data',
                'parameter': 'Keyway',
                'ideal_range': 'DIN 6885 part 1',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Gear data',
                'parameter': 'Painting system',
                'ideal_range': 'C5H according to EN 12944-5 (except output flange); output flange: 1 × primer only',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Gear data',
                'parameter': 'Colour',
                'ideal_range': 'RAL 7035 Light Grey',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            # INPUT SIDE
            {
                'group': 'Input side',
                'parameter': 'Gear type',
                'ideal_range': 'Helical bevel gearmotor — input side',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Input side',
                'parameter': 'Motor mounting',
                'ideal_range': 'Direct motor mounting',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Input side',
                'parameter': 'Input flange',
                'ideal_range': 'Left input flange: square IEC 150; bolt circle diameter 165 mm; 4 through-holes diameter 12 mm; corner radius 15 mm; bore diameter 32 F8; keyway 10 H9',
                'unit': 'millimetres',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            # MOTOR DATA
            {
                'group': 'Motor data',
                'parameter': 'Housing material',
                'ideal_range': 'Cast iron',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Motor data',
                'parameter': 'Duty cycle',
                'ideal_range': 'S3-25%',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Motor data',
                'parameter': 'Efficiency class',
                'ideal_range': 'IE2 or IE3 (evaluated under continuous S1 duty for classification purposes)',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Motor data',
                'parameter': 'Motor rated power',
                'ideal_range': '0.75 – 1.50',
                'unit': 'kilowatts',
                'specification_requirement': f'Motor power sizing: required_power = gearmotor_output_torque × gearmotor_output_speed ÷ 9550 ÷ gearbox_efficiency. PM401 common: {required_gearmotor_output_torque:.1f} × {gearmotor_output_speed_max:.0f} ÷ 9550 ÷ 0.90 = 0.866 kW. Rounded up to nearest 0.25 kW = 1.00 kW. Adopted range: 1.00 – 1.50 kW.',
                'calc_min': 1.0,
                'calc_max': 1.5,
            },
            {
                'group': 'Motor data',
                'parameter': 'Motor rated speed',
                'ideal_range': '1390 – 1465',
                'unit': 'revolutions per minute',
                'specification_requirement': 'Accepted 4-pole motor rated-speed band',
                'calc_min': 1390,
                'calc_max': 1465,
            },
            {
                'group': 'Motor data',
                'parameter': 'Motor rated torque',
                'ideal_range': f'{motor_rated_torque_min:.2f} – {motor_rated_torque_max:.2f}',
                'unit': 'Newton-metres',
                'specification_requirement': f'Rated torque = required gearmotor output torque ÷ gearbox ratio band = {required_gearmotor_output_torque:.1f} ÷ {gearbox_ratio_max:.2f} to {required_gearmotor_output_torque:.1f} ÷ {gearbox_ratio_min:.2f}',
                'calc_min': motor_rated_torque_min,
                'calc_max': motor_rated_torque_max,
            },
            {
                'group': 'Motor data',
                'parameter': 'Supply voltage',
                'ideal_range': '400 / 480 / 690',
                'unit': 'Volts',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Motor data',
                'parameter': 'Supply frequency',
                'ideal_range': '50 / 60',
                'unit': 'Hertz',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Motor data',
                'parameter': 'Winding connection',
                'ideal_range': 'Delta / Star (400 V Delta / 690 V Star)',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Motor data',
                'parameter': 'Degree of protection',
                'ideal_range': 'IP66',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Motor data',
                'parameter': 'Terminal box mounting position',
                'ideal_range': 'Mounted vertically downwards on non-drive end side; cable entry pointing downward',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Motor data',
                'parameter': 'Cable entries',
                'ideal_range': 'M25×1.5 and M16×1.5; blind-plugged for shipping',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            # FURTHER MOTOR EXECUTIONS
            {
                'group': 'Further motor executions',
                'parameter': 'Cooling method',
                'ideal_range': 'Unventilated without shaft fan — IC 410 TENV (Totally Enclosed Non-Ventilated)',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'Further motor executions',
                'parameter': 'Anti-condensation heater',
                'ideal_range': 'Approximately 25 Watts; 24 Volts DC',
                'unit': 'Watts / Volts DC',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            # GENERAL
            {
                'group': 'General',
                'parameter': 'Motor certification',
                'ideal_range': 'CE marking mandatory; EN 10204 Type 3.1 material certificate required; UKCA and UL/CSA optional',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'General',
                'parameter': 'Corrosivity and paint system',
                'ideal_range': 'C5H per DIN EN ISO 12944-5 — coast or offshore, very aggressive atmosphere, including underwater exposure',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'General',
                'parameter': 'Ambient temperature range',
                'ideal_range': '−20 °C to +50 °C',
                'unit': 'degrees Celsius',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'General',
                'parameter': 'Direction of rotation',
                'ideal_range': 'Clockwise and counter-clockwise',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'General',
                'parameter': 'Starting method',
                'ideal_range': 'Direct-on-line start',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'General',
                'parameter': 'Heater terminal blocks',
                'ideal_range': 'Two dedicated terminals for the anti-condensation heater wiring inside the motor terminal box',
                'unit': '—',
                'specification_requirement': 'Specification requirement',
                'calc_min': None,
                'calc_max': None,
            },
            {
                'group': 'General',
                'parameter': 'Required gearbox structural torque capacity',
                'ideal_range': f'{required_gearmotor_structural_torque:.1f} minimum',
                'unit': 'Newton-metres',
                'specification_requirement': f'crane_peak_torque × 1000 ÷ slewing_ring_ratio = {design.crane_peak_torque_substation_kNm * 1000} ÷ {design.slewing_ring_ratio_pm401}',
                'calc_min': required_gearmotor_structural_torque,
                'calc_max': None,
            },
            {
                'group': 'General',
                'parameter': 'Required gearbox output torque',
                'ideal_range': f'{required_gearmotor_output_torque:.1f} minimum',
                'unit': 'Newton-metres',
                'specification_requirement': f'motor_torque_share × crane_peak_torque × 1000 ÷ slewing_ring_ratio = {design.motor_torque_share_fraction * design.crane_peak_torque_substation_kNm * 1000} ÷ {design.slewing_ring_ratio_pm401}',
                'calc_min': required_gearmotor_output_torque,
                'calc_max': None,
            },
            {
                'group': 'General',
                'parameter': 'Crane slewing speed window',
                'ideal_range': f'{design.crane_min_slewing_speed_rpm} – {design.crane_max_slewing_speed_rpm}',
                'unit': 'revolutions per minute',
                'specification_requirement': 'Design practical speed window',
                'calc_min': design.crane_min_slewing_speed_rpm,
                'calc_max': design.crane_max_slewing_speed_rpm,
            },
        ]

        # Group parameters
        grouped_parameters = {}
        for param in parameters:
            group = param['group']
            if group not in grouped_parameters:
                grouped_parameters[group] = []
            grouped_parameters[group].append(param)

        context['grouped_parameters'] = grouped_parameters
        context['parameters'] = parameters

        return context
