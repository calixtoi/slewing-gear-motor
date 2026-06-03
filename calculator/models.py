from django.db import models


class MotorCalculation(models.Model):
    STANDARD_PF = 'standard_pf'
    PF_XXL = 'pf_xxl'
    CRANE_CHOICES = [
        (STANDARD_PF, 'Standard PF Crane'),
        (PF_XXL, 'PF-XXL'),
    ]

    # ── Metadata ─────────────────────────────────────────────────────────────
    supplier_name = models.CharField(max_length=200)
    crane_type = models.CharField(max_length=20, choices=CRANE_CHOICES)
    saved_at = models.DateTimeField(auto_now_add=True)
    price_prototype = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_series = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # ── Calculation inputs ────────────────────────────────────────────────────
    crane_torque_max = models.FloatField()
    crane_torque_nom = models.FloatField(null=True, blank=True)
    worm_ratio = models.FloatField()
    worm_efficiency = models.FloatField()
    motor_speed = models.FloatField()
    motor_rated_torque = models.FloatField()
    starting_factor = models.FloatField()
    gearbox_output_speed = models.FloatField()
    bevel_efficiency = models.FloatField(default=0.95)

    # ── Optional supplier comparison inputs ───────────────────────────────────
    supplier_motor_power_kw = models.FloatField(null=True, blank=True)
    supplier_motor_rated_torque = models.FloatField(null=True, blank=True)
    supplier_motor_starting_torque = models.FloatField(null=True, blank=True)
    supplier_gearbox_rated_torque = models.FloatField(null=True, blank=True)
    supplier_bevel_ratio = models.FloatField(null=True, blank=True)
    supplier_worm_ratio = models.FloatField(null=True, blank=True)

    # ── Motor physical specs (from datasheet or manual entry) ────────────────
    spec_frame_material   = models.CharField(max_length=200, blank=True, default='')
    spec_output_flange    = models.CharField(max_length=100, blank=True, default='')
    spec_shaft            = models.CharField(max_length=100, blank=True, default='')
    spec_cooling_method   = models.CharField(max_length=100, blank=True, default='')
    spec_ip_rating        = models.CharField(max_length=50,  blank=True, default='')
    spec_ambient_temp     = models.CharField(max_length=100, blank=True, default='')
    spec_coating          = models.CharField(max_length=200, blank=True, default='')
    spec_top_color        = models.CharField(max_length=100, blank=True, default='')
    spec_heater           = models.CharField(max_length=100, blank=True, default='')
    spec_insulation_class = models.CharField(max_length=20,  blank=True, default='')
    spec_duty_cycle       = models.CharField(max_length=50,  blank=True, default='')
    spec_painting         = models.CharField(max_length=500, blank=True, default='')
    spec_motor_certificate = models.CharField(max_length=200, blank=True, default='')
    spec_weight_kg        = models.FloatField(null=True, blank=True)
    spec_efficiency_class = models.CharField(max_length=20,  blank=True, default='')
    spec_voltage          = models.CharField(max_length=100, blank=True, default='')

    # ── Key results (stored for list display; detail re-runs engine) ──────────
    torque_check = models.CharField(max_length=30)
    torque_margin = models.FloatField()
    motor_power_kw = models.FloatField()

    # ── System parameters recorded at calculation time ─────────────────────────
    i_slew           = models.FloatField(default=0)
    eta_slew         = models.FloatField(default=0.40)
    CF               = models.FloatField(default=0)
    T_crane_lim      = models.FloatField(default=0)
    T_gm_start_MAX   = models.FloatField(default=0)
    gm_out_speed_rpm = models.FloatField(default=0)
    gm_out_nom_nm    = models.FloatField(default=0)
    gm_out_start_nm  = models.FloatField(default=0)
    Mk_Mn            = models.FloatField(default=3.40)

    # ── Crane output results ──────────────────────────────────────────────────
    n_crane  = models.FloatField(default=0)
    M_Nenn   = models.FloatField(default=0)
    Ma_Max   = models.FloatField(default=0)
    Mk_Max   = models.FloatField(default=0)
    overall_pass = models.BooleanField(default=False)

    # ── Physical specification fields ─────────────────────────────────────────
    spec_motor_type       = models.CharField(max_length=200, blank=True)
    spec_frame_material   = models.CharField(max_length=100, blank=True)
    spec_input_flange_mm  = models.FloatField(null=True, blank=True)
    spec_output_flange    = models.CharField(max_length=100, blank=True)
    spec_output_shaft_mm  = models.FloatField(null=True, blank=True)
    spec_shaft_length_mm  = models.FloatField(null=True, blank=True)
    spec_cooling_method   = models.CharField(max_length=100, blank=True)
    spec_ip_rating        = models.CharField(max_length=20,  blank=True)
    spec_insulation_class = models.CharField(max_length=20,  blank=True)
    spec_efficiency_class = models.CharField(max_length=20,  blank=True)
    spec_duty_cycle       = models.CharField(max_length=50,  blank=True)
    spec_ambient_temp_min = models.FloatField(null=True, blank=True)
    spec_ambient_temp_max = models.FloatField(null=True, blank=True)
    spec_voltage_400_50   = models.CharField(max_length=20, blank=True)
    spec_voltage_400_60   = models.CharField(max_length=20, blank=True)
    spec_voltage_480_60   = models.CharField(max_length=20, blank=True)
    spec_voltage_690_50   = models.CharField(max_length=20, blank=True)
    spec_voltage_690_60   = models.CharField(max_length=20, blank=True)
    spec_heater_vdc       = models.FloatField(null=True, blank=True)
    spec_coating_standard = models.CharField(max_length=100, blank=True)
    spec_surface_prep     = models.CharField(max_length=100, blank=True)
    spec_coating_ndft_um  = models.FloatField(null=True, blank=True)
    spec_paint_color      = models.CharField(max_length=50,  blank=True)
    spec_output_flange_coating = models.CharField(max_length=200, blank=True)
    spec_fasteners        = models.CharField(max_length=100, blank=True)
    spec_shaft_seal       = models.CharField(max_length=100, blank=True)
    spec_nameplate        = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.supplier_name} ({self.get_crane_type_display()})"

    @property
    def Ma_Mn_actual(self):
        if self.gm_out_nom_nm:
            return self.gm_out_start_nm / self.gm_out_nom_nm
        return 0

    @property
    def start_utilisation_pct(self):
        if self.T_crane_lim:
            return self.Ma_Max / self.T_crane_lim * 100
        return 0

    @property
    def nom_utilisation_pct(self):
        if self.T_crane_lim:
            return self.M_Nenn / self.T_crane_lim * 100
        return 0

    @property
    def start_torque_margin_nm(self):
        return self.T_crane_lim - self.Ma_Max

    @property
    def requires_soft_start(self):
        return self.Ma_Max > self.T_crane_lim

    def recalculate(self):
        from .engine import drivetrain_sizing
        return drivetrain_sizing(
            crane_torque_max=self.crane_torque_max,
            crane_torque_nom=self.crane_torque_nom,
            worm_ratio=self.worm_ratio,
            worm_efficiency=self.worm_efficiency,
            motor_speed=self.motor_speed,
            gearbox_output_speed=self.gearbox_output_speed,
            motor_rated_torque=self.motor_rated_torque,
            starting_factor=self.starting_factor,
            bevel_efficiency=self.bevel_efficiency,
            supplier_motor_power_kw=self.supplier_motor_power_kw,
            supplier_motor_rated_torque=self.supplier_motor_rated_torque,
            supplier_motor_starting_torque=self.supplier_motor_starting_torque,
            supplier_gearbox_rated_torque=self.supplier_gearbox_rated_torque,
            supplier_bevel_ratio=self.supplier_bevel_ratio,
            supplier_worm_ratio=self.supplier_worm_ratio,
        )
