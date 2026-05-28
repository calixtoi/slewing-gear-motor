from django.core.management.base import BaseCommand
from motors.models import MotorSupplier, SupplierMotor


class Command(BaseCommand):
    help = 'Load Zsystems ZK43CV DM90-4 TS P2 (V2) motor data'

    def handle(self, *args, **options):
        # Create supplier
        supplier, created = MotorSupplier.objects.get_or_create(
            name='Zsystems',
            defaults={'country': 'Austria'}
        )

        # Create the Zsystems motor
        motor, created = SupplierMotor.objects.get_or_create(
            model_number='ZK43CV DM90-4 TS P2 (V2)',
            defaults={
                'supplier': supplier,
                'model_name': 'Zsystems ZK43CV DM90-4 TS P2 (V2) - Slewing Gearmotor',
                'crane_type': SupplierMotor.STANDARD_PF,

                # Motor specs
                'motor_power': 1.5,
                'motor_speed': 1415,
                'motor_torque': 10.2,
                'motor_starting_torque': 67.877,
                'motor_starting_factor': 2.90,
                'motor_voltage_50hz': '400V/690V',
                'motor_voltage_60hz': '400V/480V/690V',
                'motor_frame': 'IEC 90 B5',
                'motor_flange': 'IEC90 B5 · Ø165 mm bolt circle',
                'motor_shaft': 'Ø32k6 × 50 mm',
                'motor_cooling': 'IC410 / TENV (none)',
                'motor_ip_rating': 'IP66',
                'motor_insulation_class': '155 / Class H',
                'motor_efficiency_class': 'IE2 or higher',
                'motor_ambient_temp_min': -20.0,
                'motor_ambient_temp_max': 45.0,
                'motor_heater': '24V, 25W',
                'motor_coating': 'C5H after EN 12944-5 (P3)',
                'motor_color': 'RAL7035 lichtgrau',
                'motor_power_factor': 0.84,

                # Gearbox specs
                'gearbox_model': 'ZK43',
                'gearbox_ratio': 38.17,
                'gearbox_output_speed': 37,
                'gearbox_output_torque': 390,
                'gearbox_nominal_torque': 760,
                'gearbox_starting_torque_max': 1131,
                'gearbox_tip_torque_max': 1326,
                'gearbox_efficiency_factor': 1.90,
                'gearbox_output_flange': 'Ø200 mm',
                'gearbox_output_shaft': 'Ø40x80 with keyway (optional custom)',
                'gearbox_oil_capacity': 1.8,
                'gearbox_oil_type': 'CLP VG220 Mineral Oil',

                # Compliance
                'compliant': True,
                'compliance_notes': 'Meets all PF crane requirements: Cast iron frame, IEC90 B5 flange Ø165mm, IP66, Class H insulation, C5H coating, 24V heater, -20…+45°C ambient range',
                'pdf_url': 'file:///\\\\satsbgc13fil21\\ba\\Marine\\BU_Marine_Wind\\02_Design_Wind\\02_PROJECTS\\PF_range\\PF Redesign\\10_Steuerung\\Slewing Gear Motor\\Suppliers\\ZSYSTEMS (AUSTRIA)\\ZK43CV DM90-4 TS P2 (V2).pdf',
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created motor: {motor.model_number}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Motor {motor.model_number} already exists')
            )
