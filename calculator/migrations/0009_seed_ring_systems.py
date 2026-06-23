from django.db import migrations


def seed_ring_systems(apps, schema_editor):
    """Seed the two ring system variants with their fixed parameters."""
    RingSystem = apps.get_model('calculator', 'RingSystem')

    # PF Standard
    RingSystem.objects.get_or_create(
        system_type='standard_pf',
        defaults={
            'ring_model': 'ELW 597EM',
            'i_slew': 121,
            'eta_slew': 0.40,
            'CF': 48.4,
            'M_max': 41190,
            'M_rated': 15360,
            'n_slew_min': 0.2,
            'n_slew_max': 1.0,
            'n_slew_tgt': 0.40,
            'n_gm_min': 30,
            'n_gm_max': 60,
            'k': 9549.3,
        }
    )

    # PF-XXL
    RingSystem.objects.get_or_create(
        system_type='pf_xxl',
        defaults={
            'ring_model': 'TGB P26-04',
            'i_slew': 110,
            'eta_slew': 0.40,
            'CF': 44.0,
            'M_max': 70000,
            'M_rated': 65000,
            'n_slew_min': 0.2,
            'n_slew_max': 0.5,
            'n_slew_tgt': 0.35,
            'n_gm_min': 22,
            'n_gm_max': 55,
            'k': 9549.3,
        }
    )


def reverse_seed(apps, schema_editor):
    """Remove seeded ring systems."""
    RingSystem = apps.get_model('calculator', 'RingSystem')
    RingSystem.objects.filter(system_type__in=['standard_pf', 'pf_xxl']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0008_motor_ringsystem_delete_motorcalculation_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_ring_systems, reverse_seed),
    ]
