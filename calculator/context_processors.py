from .models import Motor, RingSystem


def sidebar_data(request):
    """Provide sidebar context with recent motors and counts by system."""
    qs = Motor.objects.select_related('ring_system').values(
        'pk', 'supplier', 'model', 'ring_system__system_type', 'verdict'
    ).order_by('-created_at')

    return {
        'sidebar_motors': qs[:30],
        'sidebar_standard_count': Motor.objects.filter(ring_system__system_type=RingSystem.STANDARD_PF).count(),
        'sidebar_xxl_count': Motor.objects.filter(ring_system__system_type=RingSystem.PF_XXL).count(),
    }
