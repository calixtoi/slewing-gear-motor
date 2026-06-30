import math
from django.views.generic import TemplateView
from cover.models import DesignParameters


class MotorCycleCalcView(TemplateView):
    """Perform full motor sizing calculation from design parameters."""
    template_name = 'motor_cycle_calc/calc.html'

    def get_context_data(self, **kwargs):
        """Calculate all motor cycle values dynamically."""
        context = super().get_context_data(**kwargs)
        design = DesignParameters.get_or_create_default()

        # STEP 1 — Torque cycle
        motor_torque_share_nm = (
            design.motor_torque_share_fraction
            * design.crane_peak_torque_substation_kNm
            * 1000
        )

        required_gearmotor_output_torque_nm = (
            motor_torque_share_nm
            / design.slewing_ring_ratio_pm401
        )

        required_gearmotor_structural_torque_nm = (
            design.crane_peak_torque_substation_kNm
            * 1000
            / design.slewing_ring_ratio_pm401
        )

        reference_gearbox_ratio = 27.82
        required_motor_shaft_torque_nm = (
            required_gearmotor_output_torque_nm
            / reference_gearbox_ratio
        )

        # STEP 2 — Speed cycle
        gearmotor_output_speed_min_rpm = (
            design.crane_min_slewing_speed_rpm
            * design.slewing_ring_ratio_pm401
        )

        gearmotor_output_speed_max_rpm = (
            design.crane_max_slewing_speed_rpm
            * design.slewing_ring_ratio_pm401
        )

        gearbox_ratio_min = (
            1390
            / (design.crane_max_slewing_speed_rpm * design.slewing_ring_ratio_pm401)
        )

        gearbox_ratio_max = (
            1465
            / (design.crane_min_slewing_speed_rpm * design.slewing_ring_ratio_pm401)
        )

        # STEP 3 — Power
        gearbox_mechanical_efficiency = 0.90

        required_motor_rated_power_kw = (
            required_gearmotor_output_torque_nm
            * gearmotor_output_speed_max_rpm
            / 9550
            / gearbox_mechanical_efficiency
        )

        # Round UP to nearest 0.25 kW step
        selected_motor_power_kw = math.ceil(required_motor_rated_power_kw * 4) / 4

        # STEP 4 — Duty cycle (thermal)
        duty_class = "S3-25%"
        duty_fraction = 0.25

        thermal_equivalent_s1_power_kw = (
            required_motor_rated_power_kw
            * math.sqrt(duty_fraction)
        )

        # Build results list
        results = [
            {
                'step': 1,
                'group': 'Torque Cycle',
                'parameter': 'Motor torque share of peak load',
                'formula': 'motor_torque_share_fraction × crane_peak_torque × 1000',
                'expanded_formula': f'0.30 × {design.crane_peak_torque_substation_kNm} × 1000',
                'value': motor_torque_share_nm,
                'unit': 'Newton-metres',
                'min_spec': None,
                'max_spec': None,
                'status': 'INFO',
            },
            {
                'step': 1,
                'group': 'Torque Cycle',
                'parameter': 'Required gearmotor output torque — duty',
                'formula': 'motor_torque_share ÷ slewing_ring_gear_ratio',
                'expanded_formula': f'{motor_torque_share_nm:.1f} ÷ {design.slewing_ring_ratio_pm401}',
                'value': required_gearmotor_output_torque_nm,
                'unit': 'Newton-metres',
                'min_spec': 169.1,
                'max_spec': None,
                'status': 'PASS' if required_gearmotor_output_torque_nm >= 169.1 else 'FAIL',
            },
            {
                'step': 1,
                'group': 'Torque Cycle',
                'parameter': 'Required gearmotor full-peak structural torque',
                'formula': 'crane_peak_torque × 1000 ÷ slewing_ring_gear_ratio',
                'expanded_formula': f'{design.crane_peak_torque_substation_kNm} × 1000 ÷ {design.slewing_ring_ratio_pm401}',
                'value': required_gearmotor_structural_torque_nm,
                'unit': 'Newton-metres',
                'min_spec': 563.6,
                'max_spec': None,
                'status': 'PASS' if required_gearmotor_structural_torque_nm >= 563.6 else 'FAIL',
            },
            {
                'step': 1,
                'group': 'Torque Cycle',
                'parameter': 'Equivalent required motor shaft torque',
                'formula': 'gearmotor_output_torque ÷ reference_gearbox_ratio',
                'expanded_formula': f'{required_gearmotor_output_torque_nm:.1f} ÷ {reference_gearbox_ratio}',
                'value': required_motor_shaft_torque_nm,
                'unit': 'Newton-metres',
                'min_spec': None,
                'max_spec': None,
                'status': 'INFO',
            },
            {
                'step': 2,
                'group': 'Speed Cycle',
                'parameter': 'Gearmotor output speed — minimum',
                'formula': 'crane_min_speed × slewing_ring_ratio',
                'expanded_formula': f'{design.crane_min_slewing_speed_rpm} × {design.slewing_ring_ratio_pm401}',
                'value': gearmotor_output_speed_min_rpm,
                'unit': 'revolutions per minute',
                'min_spec': None,
                'max_spec': None,
                'status': 'INFO',
            },
            {
                'step': 2,
                'group': 'Speed Cycle',
                'parameter': 'Gearmotor output speed — maximum',
                'formula': 'crane_max_speed × slewing_ring_ratio',
                'expanded_formula': f'{design.crane_max_slewing_speed_rpm} × {design.slewing_ring_ratio_pm401}',
                'value': gearmotor_output_speed_max_rpm,
                'unit': 'revolutions per minute',
                'min_spec': None,
                'max_spec': None,
                'status': 'INFO',
            },
            {
                'step': 2,
                'group': 'Speed Cycle',
                'parameter': 'Gearbox ratio — minimum bound',
                'formula': 'motor_rated_speed_minimum ÷ (crane_max_speed × slewing_ring_ratio)',
                'expanded_formula': f'1390 ÷ ({design.crane_max_slewing_speed_rpm} × {design.slewing_ring_ratio_pm401})',
                'value': gearbox_ratio_min,
                'unit': 'dimensionless',
                'min_spec': None,
                'max_spec': None,
                'status': 'INFO',
            },
            {
                'step': 2,
                'group': 'Speed Cycle',
                'parameter': 'Gearbox ratio — maximum bound',
                'formula': 'motor_rated_speed_maximum ÷ (crane_min_speed × slewing_ring_ratio)',
                'expanded_formula': f'1465 ÷ ({design.crane_min_slewing_speed_rpm} × {design.slewing_ring_ratio_pm401})',
                'value': gearbox_ratio_max,
                'unit': 'dimensionless',
                'min_spec': None,
                'max_spec': None,
                'status': 'INFO',
            },
            {
                'step': 3,
                'group': 'Power & Selection',
                'parameter': 'Gearbox mechanical efficiency',
                'formula': 'constant for helical bevel gearbox',
                'expanded_formula': 'Assumed 0.90 (90%)',
                'value': gearbox_mechanical_efficiency,
                'unit': 'dimensionless',
                'min_spec': None,
                'max_spec': None,
                'status': 'INFO',
            },
            {
                'step': 3,
                'group': 'Power & Selection',
                'parameter': 'Required motor rated power',
                'formula': 'gearmotor_output_torque × gearmotor_output_speed ÷ 9550 ÷ gearbox_efficiency',
                'expanded_formula': f'{required_gearmotor_output_torque_nm:.1f} × {gearmotor_output_speed_max_rpm:.1f} ÷ 9550 ÷ {gearbox_mechanical_efficiency}',
                'value': required_motor_rated_power_kw,
                'unit': 'kilowatts',
                'min_spec': None,
                'max_spec': None,
                'status': 'INFO',
            },
            {
                'step': 3,
                'group': 'Power & Selection',
                'parameter': 'Selected standard motor power rating',
                'formula': 'round required power UP to nearest 0.25 kilowatt step',
                'expanded_formula': f'CEILING({required_motor_rated_power_kw:.3f}, 0.25)',
                'value': selected_motor_power_kw,
                'unit': 'kilowatts',
                'min_spec': None,
                'max_spec': None,
                'status': 'PASS' if 0.75 <= selected_motor_power_kw <= 1.50 else 'CHECK',
            },
            {
                'step': 4,
                'group': 'Duty Cycle & Thermal',
                'parameter': 'Duty class',
                'formula': 'constant for slewing operation',
                'expanded_formula': 'S3-25% (intermittent duty, 25% load factor)',
                'value': duty_class,
                'unit': '—',
                'min_spec': None,
                'max_spec': None,
                'status': 'INFO',
            },
            {
                'step': 4,
                'group': 'Duty Cycle & Thermal',
                'parameter': 'Thermal-equivalent continuous (S1) power at S3-25% duty',
                'formula': 'operating_point_power × square_root(duty_cycle_fraction)',
                'expanded_formula': f'{required_motor_rated_power_kw:.3f} × √0.25 = {required_motor_rated_power_kw:.3f} × 0.5',
                'value': thermal_equivalent_s1_power_kw,
                'unit': 'kilowatts',
                'min_spec': None,
                'max_spec': None,
                'status': 'INFO',
            },
        ]

        context['results'] = results
        context['design'] = design
        context['required_gearmotor_output_torque_nm'] = required_gearmotor_output_torque_nm
        context['selected_motor_power_kw'] = selected_motor_power_kw

        return context
