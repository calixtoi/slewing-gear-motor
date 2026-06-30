from django.views.generic import TemplateView
from motor_verification.models import MotorSupplier
from motor_verification.validators import get_supplier_summary
from cover.models import DesignParameters


class HomeView(TemplateView):
    """Dashboard / landing page linking to all five functional apps."""
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        """Add status information and app descriptions."""
        context = super().get_context_data(**kwargs)

        # Check for FAIL suppliers
        design = DesignParameters.get_or_create_default()
        fail_suppliers = []
        for supplier in MotorSupplier.objects.all():
            summary = get_supplier_summary(supplier, design)
            if summary['fail_count'] > 0:
                fail_suppliers.append(supplier)

        context['fail_suppliers'] = fail_suppliers
        context['apps'] = [
            {
                'name': 'Cover',
                'slug': 'cover',
                'description': 'Design principles, executive summary, and editable source parameters that drive all calculations.',
                'icon': 'card-text',
            },
            {
                'name': 'Motor Cycle Calculation',
                'slug': 'calc',
                'description': 'Perform the full motor sizing calculation: peak torque → output speed → required power → motor selection.',
                'icon': 'calculator',
            },
            {
                'name': 'Ideal Motor Parameters',
                'slug': 'parameters',
                'description': 'Complete specification requirement table with all motor and gearbox parameters, grouped by category.',
                'icon': 'table',
            },
            {
                'name': 'Motor Verification',
                'slug': 'verification-list',
                'description': 'Side-by-side comparison of supplier motors against ideal specifications. Add suppliers via manual entry, text extraction, or PDF upload.',
                'icon': 'check-circle',
            },
            {
                'name': 'Formula Library',
                'slug': 'formulas',
                'description': 'Complete reference of every formula used in the tool, written in full plain English without abbreviations.',
                'icon': 'book',
            },
        ]

        return context
