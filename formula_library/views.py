from django.views.generic import TemplateView


class FormulaLibraryView(TemplateView):
    """Display all formulas used in the tool with full explanations."""
    template_name = 'formula_library/formulas.html'

    def get_context_data(self, **kwargs):
        """Build the complete formula library."""
        context = super().get_context_data(**kwargs)

        formulas = [
            {
                'id': 'F01',
                'name': 'Motor torque share of crane peak load',
                'formula_symbolic': 'motor_share_torque = torque_share_fraction × crane_peak_torque',
                'formula_expanded': 'Motor torque share (Newton-metres) = Motor torque share fraction (dimensionless) × Crane peak slewing torque (Newton-metres)',
                'variables': [
                    {
                        'symbol': 'Motor torque share (Newton-metres)',
                        'description': 'The portion of the maximum structural peak torque that the gearmotor must be able to deliver.',
                    },
                    {
                        'symbol': 'Motor torque share fraction (dimensionless)',
                        'description': 'A design rule fraction — minimum 0.30 (30%) — derived from PF200 proven concept.',
                    },
                    {
                        'symbol': 'Crane peak slewing torque (Newton-metres)',
                        'description': 'The highest structural torque at the slewing ring across all operating scenarios. Worst case: 62,000 Newton-metres (Substation operation).',
                    },
                ],
                'example': '0.30 × 62,000 = 18,600 Newton-metres',
                'source': 'Design brief section 7; PF200 design philosophy',
                'used_in': 'Motor Cycle Calculation — Step 1',
            },
            {
                'id': 'F02',
                'name': 'Required gearmotor output torque',
                'formula_symbolic': 'required_gearmotor_output_torque = motor_share_torque ÷ slewing_ring_gear_ratio',
                'formula_expanded': 'Required gearmotor output torque (Newton-metres) = Motor torque share (Newton-metres) ÷ Slewing ring gear ratio (dimensionless)',
                'variables': [
                    {
                        'symbol': 'Required gearmotor output torque (Newton-metres)',
                        'description': 'The minimum torque the gearmotor must deliver at its output shaft to drive the crane. This is the core sizing result for gearmotor selection.',
                    },
                    {
                        'symbol': 'Motor torque share (Newton-metres)',
                        'description': 'See Formula F01.',
                    },
                    {
                        'symbol': 'Slewing ring gear ratio (dimensionless)',
                        'description': 'The number of gearmotor output-shaft revolutions per one complete crane revolution. PM401: 110 revolutions per crane revolution.',
                    },
                ],
                'example': '18,600 ÷ 110 = 169.1 Newton-metres',
                'source': 'Motor Cycle Calc step 2',
                'used_in': 'Motor Cycle Calculation — Step 1',
            },
            {
                'id': 'F03',
                'name': 'Required gearmotor full-peak structural torque',
                'formula_symbolic': 'structural_torque = crane_peak_torque ÷ slewing_ring_gear_ratio',
                'formula_expanded': 'Required gearmotor structural torque (Newton-metres) = Crane peak slewing torque (Newton-metres) ÷ Slewing ring gear ratio (dimensionless)',
                'variables': [
                    {
                        'symbol': 'Required gearmotor structural torque (Newton-metres)',
                        'description': 'The maximum torque that the gearmotor output shaft and gearbox casing must be able to withstand without permanent deformation. This is the structural capacity requirement.',
                    },
                    {
                        'symbol': 'Crane peak slewing torque (Newton-metres)',
                        'description': 'See Formula F01.',
                    },
                    {
                        'symbol': 'Slewing ring gear ratio (dimensionless)',
                        'description': 'See Formula F02.',
                    },
                ],
                'example': '62,000 ÷ 110 = 563.6 Newton-metres',
                'source': 'Motor Cycle Calc step 3',
                'used_in': 'Motor Cycle Calculation — Step 1',
            },
            {
                'id': 'F04',
                'name': 'Gearmotor output speed range',
                'formula_symbolic': 'gearmotor_output_speed = crane_slewing_speed × slewing_ring_gear_ratio',
                'formula_expanded': 'Gearmotor output shaft speed (revolutions per minute) = Crane slewing speed (revolutions per minute) × Slewing ring gear ratio (dimensionless)',
                'variables': [
                    {
                        'symbol': 'Gearmotor output shaft speed (revolutions per minute)',
                        'description': 'The rotational speed at the gearmotor output shaft, which drives the slewing ring.',
                    },
                    {
                        'symbol': 'Crane slewing speed (revolutions per minute)',
                        'description': 'The angular velocity of the crane platform. Practical operating window: 0.20 to 0.40 revolutions per minute.',
                    },
                    {
                        'symbol': 'Slewing ring gear ratio (dimensionless)',
                        'description': 'See Formula F02.',
                    },
                ],
                'example': 'Minimum: 0.20 × 110 = 22 rpm; Maximum: 0.40 × 110 = 44 rpm',
                'source': 'Motor Cycle Calc — speed window',
                'used_in': 'Motor Cycle Calculation — Step 2',
            },
            {
                'id': 'F05',
                'name': 'Gearbox internal ratio — speed window band',
                'formula_symbolic': 'gearbox_ratio_min = motor_speed_min ÷ (crane_max_speed × slewing_ratio)\ngearbox_ratio_max = motor_speed_max ÷ (crane_min_speed × slewing_ratio)',
                'formula_expanded': 'Minimum gearbox internal ratio = Minimum motor rated speed ÷ (Maximum crane slewing speed × Slewing ring ratio)\nMaximum gearbox internal ratio = Maximum motor rated speed ÷ (Minimum crane slewing speed × Slewing ring ratio)',
                'variables': [
                    {
                        'symbol': 'Gearbox internal ratio (dimensionless)',
                        'description': 'The ratio of gearmotor input shaft speed to output shaft speed, internal to the gearbox itself.',
                    },
                    {
                        'symbol': 'Motor rated speed band (revolutions per minute)',
                        'description': 'Accepted 4-pole motor speeds at 50 Hz: 1390 to 1465 revolutions per minute.',
                    },
                ],
                'example': 'Minimum: 1390 ÷ (0.40 × 110) = 31.6; Maximum: 1465 ÷ (0.20 × 110) = 66.6',
                'source': 'Motor Cycle Calc — gearbox ratio envelope',
                'used_in': 'Motor Cycle Calculation — Step 2',
            },
            {
                'id': 'F06',
                'name': 'Required motor rated power',
                'formula_symbolic': 'required_motor_power = gearmotor_output_torque × gearmotor_output_speed ÷ 9550 ÷ gearbox_efficiency',
                'formula_expanded': 'Required motor rated power (kilowatts) = Required gearmotor output torque (Newton-metres) × Gearmotor output speed (revolutions per minute) ÷ 9550 ÷ Gearbox mechanical efficiency',
                'variables': [
                    {
                        'symbol': 'Required motor rated power (kilowatts)',
                        'description': 'The minimum electrical input power the motor must be able to deliver continuously.',
                    },
                    {
                        'symbol': '9550 — power-torque conversion constant',
                        'description': 'Universal constant: Power (kilowatts) = Torque (Newton-metres) × Speed (revolutions per minute) ÷ 9550.',
                    },
                    {
                        'symbol': 'Gearbox mechanical efficiency (dimensionless)',
                        'description': 'Assumed 0.90 (90%) for a helical bevel gearbox.',
                    },
                ],
                'example': '169.1 × 44 ÷ 9550 ÷ 0.90 = 0.866 kilowatts',
                'source': 'Motor Cycle Calc — rated power calculation',
                'used_in': 'Motor Cycle Calculation — Step 3',
            },
            {
                'id': 'F07',
                'name': 'Selected standard motor power rating',
                'formula_symbolic': 'selected_power = CEILING(required_power, 0.25)',
                'formula_expanded': 'Selected standard motor power rating (kilowatts) = Round the required motor rated power upward to the nearest 0.25 kilowatt step',
                'variables': [
                    {
                        'symbol': 'CEILING function',
                        'description': 'Rounding operation that always rounds UP to the nearest multiple of the step value. Example: CEILING(0.866, 0.25) = 1.00 kW. Standard IEC steps: 0.25, 0.37, 0.55, 0.75, 1.1, 1.5, 2.2 kW.',
                    },
                ],
                'example': 'CEILING(0.866, 0.25) = 1.00 kilowatt',
                'source': 'Motor Cycle Calc — motor selection',
                'used_in': 'Motor Cycle Calculation — Step 3',
            },
            {
                'id': 'F08',
                'name': 'Thermal-equivalent continuous power at S3-25% duty',
                'formula_symbolic': 'thermal_equivalent_power = operating_power × √(duty_fraction)',
                'formula_expanded': 'Thermal-equivalent continuous-duty (S1) power (kilowatts) = Operating-point mechanical power (kilowatts) × Square root of the duty cycle fraction',
                'variables': [
                    {
                        'symbol': 'Thermal-equivalent continuous-duty (S1) power (kilowatts)',
                        'description': 'The power rating a motor with continuous-duty capability must have to be thermally equivalent to intermittent-duty operation.',
                    },
                    {
                        'symbol': 'Duty cycle fraction (dimensionless)',
                        'description': 'S3-25% duty: motor runs for 25% of cycle time (0.25 as fraction).',
                    },
                    {
                        'symbol': 'Square root of duty fraction',
                        'description': 'Arises from motor heating proportional to current squared, cooling proportional to time.',
                    },
                ],
                'example': '0.866 × √0.25 = 0.866 × 0.5 = 0.433 kilowatts',
                'source': 'Motor Cycle Calc — duty cycle; IEC 60034-1',
                'used_in': 'Motor Cycle Calculation — Step 4',
            },
        ]

        context['formulas'] = formulas

        return context
