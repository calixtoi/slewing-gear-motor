from django.db import models


class DesignParameters(models.Model):
    """Singleton model storing all design parameter inputs that drive the calculations."""

    crane_peak_torque_pf200_kNm = models.FloatField(
        default=42.0,
        help_text="Historical reference value including Dynamic Amplification Factor and Partial Safety Factor. Used for comparison only."
    )
    crane_peak_torque_tp_kNm = models.FloatField(
        default=43.0,
        help_text="Worst-case peak torque for the TP (Transport Position) operating scenario."
    )
    crane_peak_torque_substation_kNm = models.FloatField(
        default=62.0,
        help_text="Governing dimensioning basis: highest structural peak torque across all variants. Selected because Substation operation produces the highest loads."
    )
    slewing_ring_ratio_pm401 = models.FloatField(
        default=110.0,
        help_text="Number of gearmotor revolutions per one full crane revolution. Source: TGB P26-04."
    )
    slewing_ring_ratio_pf200_ref = models.FloatField(
        default=121.0,
        help_text="Reference ratio for the PF200 historical baseline. Source: ELW 597EM."
    )
    motor_torque_share_fraction = models.FloatField(
        default=0.30,
        help_text="The motor must deliver at least this fraction of the worst-case peak torque. Derived from PF200 proven operation at 35%; conservatively set to 30% for PM401."
    )
    crane_max_slewing_speed_rpm = models.FloatField(
        default=0.40,
        help_text="Upper crane speed limit imposed by crane tip velocity. Must not be exceeded in normal electrical slewing."
    )
    crane_min_slewing_speed_rpm = models.FloatField(
        default=0.20,
        help_text="Lower bound of the practical electrical slewing window."
    )

    class Meta:
        verbose_name = "Design Parameters"
        verbose_name_plural = "Design Parameters"

    def __str__(self):
        return "Design Parameters (Singleton)"

    @staticmethod
    def get_or_create_default():
        """Get or create the singleton instance with default values."""
        obj, created = DesignParameters.objects.get_or_create(
            pk=1,
            defaults={
                'crane_peak_torque_pf200_kNm': 42.0,
                'crane_peak_torque_tp_kNm': 43.0,
                'crane_peak_torque_substation_kNm': 62.0,
                'slewing_ring_ratio_pm401': 110.0,
                'slewing_ring_ratio_pf200_ref': 121.0,
                'motor_torque_share_fraction': 0.30,
                'crane_max_slewing_speed_rpm': 0.40,
                'crane_min_slewing_speed_rpm': 0.20,
            }
        )
        return obj
