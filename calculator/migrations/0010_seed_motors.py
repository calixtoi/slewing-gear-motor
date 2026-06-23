from django.db import migrations
import json


def seed_motors(apps, schema_editor):
    """Seed the three example motors from the specification."""
    Motor = apps.get_model('calculator', 'Motor')
    RingSystem = apps.get_model('calculator', 'RingSystem')

    # Import evaluation function
    import sys
    import os
    # This is a bit tricky in a migration, but we can import the service function
    from calculator.services import evaluate, verdict as compute_verdict

    pf_std = RingSystem.objects.get(system_type='standard_pf')
    pf_xxl = RingSystem.objects.get(system_type='pf_xxl')

    # WEG EP2557M 0.75 kW on PF Standard (FITS 11/11)
    weg, created = Motor.objects.get_or_create(
        ring_system=pf_std,
        supplier='Watt Drive',
        model='EP2557M',
        defaults={
            'gm_type': 'KF 60A 3C 80-04E',
            'i_gb': 27.82,
            'n_mot': 1410,
            'P': 0.75,
            'T_nom': 141,
            'T_pu': 295,
            'T_start': 353.3,
            'T_peak': 367.2,
            'T_in_max': 14.4,
            'T_bd': 13.2,
            'fB': 2.8,
            'duty': 'S2-12 min',
            'flange': '□150 / Ø32 k6×50',
            'voltage': '400/690 V 50 Hz',
            'IP': 'IP66',
            'insulation': 'H',
            'heater': '24 VDC',
            'temp': '−20 to +50',
            'coating': 'C5H RAL7035',
            'frame': 'Cast iron',
            'cooling': 'IC410 TENV',
            'start_method': 'DOL',
            'notes': 'Currently installed, validated reference motor. Expected: n_gm=50.68 rpm, n_slew=0.419 rpm',
        }
    )
    if created:
        motor_input = {'i_gb': 27.82, 'n_mot': 1410, 'P': 0.75, 'T_nom': 141, 'T_pu': 295, 'T_start': 353.3, 'T_peak': 367.2, 'T_in_max': 14.4, 'T_bd': 13.2, 'fB': 2.8, 'duty': 'S2-12 min', 'flange': '□150 / Ø32 k6×50'}
        result = evaluate(motor_input, pf_std)
        weg.i_tot = result.get('i_tot')
        weg.n_gm = result.get('n_gm')
        weg.n_slew = result.get('n_slew')
        weg.dP = result.get('dP')
        weg.M_S2 = result.get('M_S2')
        weg.M_PU = result.get('M_PU')
        weg.M_start = result.get('M_start')
        weg.M_peak = result.get('M_peak')
        weg.checks_json = json.dumps(result.get('checks', {}))
        weg.verdict = compute_verdict(result.get('checks', {}))
        weg.passed_count = sum(1 for c in result.get('checks', {}).values() if c['status'] == 'PASS')
        weg.save()

    # Z:systems ZK33CV on PF Standard (DOES NOT FIT - 5/11)
    zk33, created = Motor.objects.get_or_create(
        ring_system=pf_std,
        supplier='Z:systems',
        model='ZK33CV',
        defaults={
            'gm_type': 'ZK33CV DM90-4 TS P2',
            'i_gb': 30.91,
            'n_mot': 1415,
            'P': 1.5,
            'T_nom': 315,
            'T_pu': None,
            'T_start': 915,
            'T_peak': 915,
            'T_in_max': None,
            'T_bd': None,
            'fB': 0.9,
            'duty': 'S3-15 min/h (S3-25%)',
            'flange': '□160 / Ø32×50',
            'voltage': '400/690 V; 480 V 60 Hz',
            'IP': 'IP66',
            'insulation': 'H (155)',
            'heater': 'TBD',
            'temp': '−20 to +45',
            'coating': 'C5H',
            'frame': 'Cast iron',
            'cooling': 'IC410 TENV',
            'start_method': 'DOL',
            'notes': 'Counter-example: exceeds ring limits. Expected: M_start=44286 Nm > limit 41190 Nm',
        }
    )
    if created:
        motor_input = {'i_gb': 30.91, 'n_mot': 1415, 'P': 1.5, 'T_nom': 315, 'T_pu': None, 'T_start': 915, 'T_peak': 915, 'T_in_max': None, 'T_bd': None, 'fB': 0.9, 'duty': 'S3-15 min/h (S3-25%)', 'flange': '□160 / Ø32×50'}
        result = evaluate(motor_input, pf_std)
        zk33.i_tot = result.get('i_tot')
        zk33.n_gm = result.get('n_gm')
        zk33.n_slew = result.get('n_slew')
        zk33.dP = result.get('dP')
        zk33.M_S2 = result.get('M_S2')
        zk33.M_PU = result.get('M_PU')
        zk33.M_start = result.get('M_start')
        zk33.M_peak = result.get('M_peak')
        zk33.checks_json = json.dumps(result.get('checks', {}))
        zk33.verdict = compute_verdict(result.get('checks', {}))
        zk33.passed_count = sum(1 for c in result.get('checks', {}).values() if c['status'] == 'PASS')
        zk33.save()

    # Z:systems ZK43CV on PF-XXL (DOES NOT FIT)
    zk43, created = Motor.objects.get_or_create(
        ring_system=pf_xxl,
        supplier='Z:systems',
        model='ZK43CV',
        defaults={
            'gm_type': 'ZK43CV DM90-4 TS P2',
            'i_gb': 38.17,
            'n_mot': 1415,
            'P': 1.5,
            'T_nom': 390,
            'T_pu': None,
            'T_start': 1131,
            'T_peak': 1326,
            'T_in_max': None,
            'T_bd': 34.7,
            'fB': 1.9,
            'duty': 'S3-15 min/h',
            'flange': 'TBD — confirm',
            'voltage': '400/690 V 50 Hz',
            'IP': 'IP66',
            'insulation': 'H (155)',
            'heater': '25 W 24 VDC',
            'temp': '−20 to +45',
            'coating': 'C5H',
            'frame': 'Cast iron',
            'cooling': 'IC410 TENV',
            'start_method': 'DOL',
            'notes': 'PF-XXL candidate: fails check 6. Expected: n_gm=37.07 rpm, M_start=49764 Nm',
        }
    )
    if created:
        motor_input = {'i_gb': 38.17, 'n_mot': 1415, 'P': 1.5, 'T_nom': 390, 'T_pu': None, 'T_start': 1131, 'T_peak': 1326, 'T_in_max': None, 'T_bd': 34.7, 'fB': 1.9, 'duty': 'S3-15 min/h', 'flange': 'TBD — confirm'}
        result = evaluate(motor_input, pf_xxl)
        zk43.i_tot = result.get('i_tot')
        zk43.n_gm = result.get('n_gm')
        zk43.n_slew = result.get('n_slew')
        zk43.dP = result.get('dP')
        zk43.M_S2 = result.get('M_S2')
        zk43.M_PU = result.get('M_PU')
        zk43.M_start = result.get('M_start')
        zk43.M_peak = result.get('M_peak')
        zk43.checks_json = json.dumps(result.get('checks', {}))
        zk43.verdict = compute_verdict(result.get('checks', {}))
        zk43.passed_count = sum(1 for c in result.get('checks', {}).values() if c['status'] == 'PASS')
        zk43.save()


def reverse_seed(apps, schema_editor):
    """Remove seeded motors."""
    Motor = apps.get_model('calculator', 'Motor')
    Motor.objects.filter(
        supplier__in=['Watt Drive', 'Z:systems']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0009_seed_ring_systems'),
    ]

    operations = [
        migrations.RunPython(seed_motors, reverse_seed),
    ]
