from django.db import models


# Backward compatibility: alias for legacy code
MotorCalculation = None  # Will be set below


class RingSystem(models.Model):
    """Fixed system parameters for PF Standard and PF-XXL crane variants."""

    STANDARD_PF = 'standard_pf'
    PF_XXL = 'pf_xxl'
    SYSTEM_CHOICES = [
        (STANDARD_PF, 'PF Standard (ELW 597EM)'),
        (PF_XXL, 'PF-XXL (TGB P26-04)'),
    ]

    system_type = models.CharField(max_length=20, choices=SYSTEM_CHOICES, unique=True)
    ring_model = models.CharField(max_length=100, help_text='e.g., ELW 597EM or TGB P26-04')

    # Fixed parameters
    i_slew = models.FloatField(help_text='Slewing-ring reduction ratio (i_slew)')
    eta_slew = models.FloatField(default=0.40, help_text='Slewing-ring efficiency')
    CF = models.FloatField(help_text='Combined factor = i_slew × η_slew')
    M_max = models.FloatField(help_text='Ring maximum (structural) torque (Nm)')
    M_rated = models.FloatField(help_text='Ring nominal/rated operating torque (Nm)')

    # Speed windows
    n_slew_min = models.FloatField(help_text='Min crane slewing speed (rpm)')
    n_slew_max = models.FloatField(help_text='Max crane slewing speed (rpm)')
    n_slew_tgt = models.FloatField(help_text='Target crane slewing speed (rpm)')
    n_gm_min = models.FloatField(help_text='Min GM output speed (rpm)')
    n_gm_max = models.FloatField(help_text='Max GM output speed (rpm)')

    # Constants
    k = models.FloatField(default=9549.3, help_text='Torque constant = 60000/(2π)')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['system_type']

    def __str__(self):
        return self.get_system_type_display()

    @property
    def T_gm_nom_req(self):
        """Derived: Required GM nominal torque."""
        return self.M_rated / self.CF

    @property
    def T_gm_start_max(self):
        """Derived: Maximum GM starting torque."""
        return self.M_max / self.CF


class Motor(models.Model):
    """Motor candidate for a ring system, with all datasheet inputs and calculation results."""

    ring_system = models.ForeignKey(RingSystem, on_delete=models.CASCADE, related_name='motors')

    # Metadata
    supplier = models.CharField(max_length=200, help_text='Motor supplier (e.g., Watt Drive, Z:systems)')
    model = models.CharField(max_length=200, help_text='Motor model (e.g., EP2557M)')
    gm_type = models.CharField(max_length=200, blank=True, help_text='Geared-motor type designation')
    notes = models.TextField(blank=True, help_text='Any additional notes or context')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Drivetrain inputs
    i_gb = models.FloatField(help_text='Gearbox reduction ratio')
    n_mot = models.FloatField(help_text='Rated motor speed (rpm)')
    P = models.FloatField(help_text='Rated motor power (kW)')

    # Torques at GM output shaft (Nm)
    T_nom = models.FloatField(help_text='GM nominal output torque (Nm)')
    T_pu = models.FloatField(null=True, blank=True, help_text='GM pull-up / acceleration torque (Nm)')
    T_start = models.FloatField(help_text='GM start / breakaway torque (Nm)')
    T_peak = models.FloatField(help_text='GM peak / max torque (Nm)')

    # Motor and gearbox limits
    T_in_max = models.FloatField(null=True, blank=True, help_text='Permissible gearbox input torque (Nm)')
    T_bd = models.FloatField(null=True, blank=True, help_text='Motor breakdown torque (Nm)')

    # Physical specs
    fB = models.FloatField(null=True, blank=True, help_text='Service factor')
    duty = models.CharField(max_length=100, blank=True, help_text='Duty cycle (e.g., S2-12 min, S3-25%)')
    flange = models.CharField(max_length=200, blank=True, help_text='Flange interface (e.g., □150 / Ø32 k6×50)')
    voltage = models.CharField(max_length=100, blank=True, help_text='Supply voltage/frequency')
    IP = models.CharField(max_length=20, blank=True, help_text='IP protection class')
    insulation = models.CharField(max_length=20, blank=True, help_text='Insulation class')
    heater = models.CharField(max_length=100, blank=True, help_text='Standstill heater')
    temp = models.CharField(max_length=100, blank=True, help_text='Ambient temperature range')
    coating = models.CharField(max_length=100, blank=True, help_text='Coating standard')
    frame = models.CharField(max_length=100, blank=True, help_text='Frame material')
    cooling = models.CharField(max_length=100, blank=True, help_text='Cooling method')
    start_method = models.CharField(max_length=100, blank=True, default='DOL', help_text='Starting method (DOL, VFD, etc.)')

    # Calculated results
    i_tot = models.FloatField(null=True, blank=True, help_text='Total reduction ratio = i_gb × i_slew')
    n_gm = models.FloatField(null=True, blank=True, help_text='GM output speed (rpm)')
    n_slew = models.FloatField(null=True, blank=True, help_text='Crane slewing speed (rpm)')
    dP = models.FloatField(null=True, blank=True, help_text='Power consistency (fraction)')

    # Ring-level torques
    M_S2 = models.FloatField(null=True, blank=True, help_text='Ring running torque (Nm)')
    M_PU = models.FloatField(null=True, blank=True, help_text='Ring pull-up torque (Nm)')
    M_start = models.FloatField(null=True, blank=True, help_text='Ring start/breakaway torque (Nm)')
    M_peak = models.FloatField(null=True, blank=True, help_text='Ring peak torque (Nm)')

    # Validation results (JSON dict of check results)
    checks_json = models.TextField(blank=True, default='{}', help_text='JSON dict of 11-point checks')
    verdict = models.CharField(
        max_length=50,
        choices=[
            ('FITS', 'FITS (11/11)'),
            ('FITS_REVIEW', 'FITS — minor review'),
            ('DOES_NOT_FIT', 'DOES NOT FIT'),
        ],
        blank=True,
        help_text='Final verdict'
    )
    passed_count = models.IntegerField(default=0, help_text='Number of checks passed (0-11)')

    class Meta:
        ordering = ['-created_at']
        unique_together = [['ring_system', 'supplier', 'model']]

    def __str__(self):
        return f"{self.supplier} {self.model} ({self.ring_system})"

    def recalculate(self):
        """Run the full 11-point evaluation and store results."""
        from .services import evaluate, verdict as compute_verdict

        # Prepare input dict
        motor_input = {
            'i_gb': self.i_gb,
            'n_mot': self.n_mot,
            'P': self.P,
            'T_nom': self.T_nom,
            'T_pu': self.T_pu,
            'T_start': self.T_start,
            'T_peak': self.T_peak,
            'T_in_max': self.T_in_max,
            'T_bd': self.T_bd,
            'fB': self.fB,
            'duty': self.duty,
            'flange': self.flange,
        }

        # Evaluate
        result = evaluate(motor_input, self.ring_system)

        # Store results
        self.i_tot = result.get('i_tot')
        self.n_gm = result.get('n_gm')
        self.n_slew = result.get('n_slew')
        self.dP = result.get('dP')
        self.M_S2 = result.get('M_S2')
        self.M_PU = result.get('M_PU')
        self.M_start = result.get('M_start')
        self.M_peak = result.get('M_peak')

        # Store checks
        import json
        self.checks_json = json.dumps(result.get('checks', {}))

        # Compute verdict
        checks = result.get('checks', {})
        self.verdict = compute_verdict(checks)
        self.passed_count = sum(1 for c in checks.values() if c['status'] == 'PASS')

        self.save()
        return result

    @property
    def checks(self):
        """Parse checks_json into a dict."""
        import json
        try:
            return json.loads(self.checks_json)
        except (json.JSONDecodeError, TypeError):
            return {}
