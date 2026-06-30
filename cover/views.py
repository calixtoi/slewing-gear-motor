from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import DesignParameters
from .forms import DesignParametersForm


class CoverView(UpdateView):
    """Edit design parameters and display cover sheet information."""
    model = DesignParameters
    form_class = DesignParametersForm
    template_name = 'cover/cover.html'
    success_url = reverse_lazy('cover')

    def get_object(self, queryset=None):
        """Get or create the singleton design parameters object."""
        return DesignParameters.get_or_create_default()

    def get_context_data(self, **kwargs):
        """Add calculated key results to context."""
        context = super().get_context_data(**kwargs)
        design = self.object

        # Calculate key results
        required_gearmotor_output_torque_nm = (
            design.motor_torque_share_fraction
            * design.crane_peak_torque_substation_kNm
            * 1000
            / design.slewing_ring_ratio_pm401
        )

        gearmotor_output_speed_min_rpm = (
            design.crane_min_slewing_speed_rpm
            * design.slewing_ring_ratio_pm401
        )
        gearmotor_output_speed_max_rpm = (
            design.crane_max_slewing_speed_rpm
            * design.slewing_ring_ratio_pm401
        )

        pf200_torque_share_percent = (
            (required_gearmotor_output_torque_nm
             * design.slewing_ring_ratio_pf200_ref
             / (design.crane_peak_torque_pf200_kNm * 1000))
            * 100
        )

        slewing_ring_efficiency_percent = design.slewing_ring_efficiency * 100

        context['required_gearmotor_output_torque_nm'] = required_gearmotor_output_torque_nm
        context['gearmotor_output_speed_min_rpm'] = gearmotor_output_speed_min_rpm
        context['gearmotor_output_speed_max_rpm'] = gearmotor_output_speed_max_rpm
        context['pf200_torque_share_percent'] = pf200_torque_share_percent
        context['slewing_ring_efficiency_percent'] = slewing_ring_efficiency_percent
        context['design_principles'] = [
            "The slewing ring mechanism has a fixed 110:1 gear ratio and 40% mechanical efficiency, accounting for friction losses in the slewing ring drive.",
            "The motor is not intended to carry the full peak structural load, but rather a minimum design fraction thereof.",
            "This design philosophy is derived from proven PF200 operation, where the motor shared only 35% of the worst-case peak torque.",
            "For PM401, a conservative minimum of 30% motor torque share is adopted to ensure robust behaviour across all operating scenarios.",
            "The gearbox is nevertheless sized to withstand the full structural peak torque, ensuring protection against overload.",
            "Motor rated speed must fall within the accepted 4-pole motor band: 1390 – 1465 revolutions per minute at 50 Hz.",
            "The gearbox internal ratio is determined by the required output speed window and the motor speed band.",
            "Duty cycle is intermittent S3-25%, reflecting the practical operational pattern of crane slewing.",
            "Efficiency class IE2 is specified to balance cost and energy performance over the product lifecycle.",
            "Corrosivity protection (C5H per EN 12944-5) ensures reliability in harsh offshore environments.",
            "All interface dimensions and mounting positions are governed by the existing PF crane architecture.",
        ]
        return context

    def form_valid(self, form):
        """Save form and display success message."""
        messages.success(self.request, 'Design parameters saved and recalculated successfully.')
        return super().form_valid(form)
