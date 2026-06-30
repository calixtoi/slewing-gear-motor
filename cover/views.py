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
            "This tool sizes a single motor for all PM010 variants (PF120, PF160, PF200) and PM401 crane types.",
            "PM010 is the SAP designation for the PF-Redesign product line, which includes three sub-variants: PF120 (light), PF160 (medium), and PF200 (heavy).",
            "The motor is sized to handle the worst-case peak torque across all variants and operating scenarios: 62 kNm (Substation operation, PM401).",
            "The motor does not carry the full peak structural load, but rather a conservative 30% minimum share thereof — following proven PF200 design philosophy (35% historical share).",
            "This fractional approach ensures robust motor behaviour across all PM010 variants while keeping motor costs reasonable and gearbox sized for full structural protection.",
            "The gearbox is nevertheless sized to withstand the full structural peak torque (563.6 N·m at the output), ensuring protection against overload across all variants.",
            "The slewing ring mechanism is a fixed 110:1 gear ratio component with 40% mechanical efficiency, accounting for friction losses in the slewing ring drive.",
            "Motor rated speed must fall within the accepted 4-pole motor band: 1390 – 1465 revolutions per minute at 50 Hz.",
            "The gearbox internal ratio is determined by the required output speed window (22–44 rpm) and the motor speed band.",
            "Duty cycle is intermittent S3-25%, reflecting the practical operational pattern of crane slewing.",
            "Efficiency class IE2 is specified to balance cost and energy performance over the product lifecycle.",
            "Corrosivity protection (C5H per EN 12944-5) ensures reliability in harsh offshore environments for all PM010 and PM401 variants.",
            "All interface dimensions and mounting positions are governed by the existing PF crane architecture to ensure backward compatibility.",
        ]
        return context

    def form_valid(self, form):
        """Save form and display success message."""
        messages.success(self.request, 'Design parameters saved and recalculated successfully.')
        return super().form_valid(form)
