from django.db import models


class MotorSupplier(models.Model):
    """Supplier information"""
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class SupplierMotor(models.Model):
    """Complete motor/gearbox assembly from a supplier"""
    STANDARD_PF = 'standard_pf'
    PF_XXL = 'pf_xxl'
    CRANE_TYPE_CHOICES = [
        (STANDARD_PF, 'Standard PF'),
        (PF_XXL, 'PF-XXL'),
    ]

    supplier = models.ForeignKey(MotorSupplier, on_delete=models.CASCADE, related_name='motors', null=True, blank=True)
    model_number = models.CharField(max_length=255, unique=True)
    model_name = models.CharField(max_length=500)
    crane_type = models.CharField(max_length=50, choices=CRANE_TYPE_CHOICES, default=STANDARD_PF)

    # Motor specs
    motor_power = models.FloatField(help_text='kW')
    motor_speed = models.FloatField(help_text='rpm')
    motor_torque = models.FloatField(help_text='Nm')
    motor_starting_torque = models.FloatField(null=True, blank=True, help_text='Nm max')
    motor_starting_factor = models.FloatField(null=True, blank=True, help_text='Ma/Mn ratio')
    motor_voltage_50hz = models.CharField(max_length=100)
    motor_voltage_60hz = models.CharField(max_length=100)
    motor_frame = models.CharField(max_length=100)
    motor_flange = models.CharField(max_length=100)
    motor_shaft = models.CharField(max_length=100)
    motor_cooling = models.CharField(max_length=100)
    motor_ip_rating = models.CharField(max_length=50)
    motor_insulation_class = models.CharField(max_length=50)
    motor_efficiency_class = models.CharField(max_length=50)
    motor_ambient_temp_min = models.FloatField(null=True, blank=True, help_text='°C')
    motor_ambient_temp_max = models.FloatField(null=True, blank=True, help_text='°C')
    motor_heater = models.CharField(max_length=100, blank=True)
    motor_coating = models.CharField(max_length=100, blank=True)
    motor_color = models.CharField(max_length=100, blank=True)
    motor_power_factor = models.FloatField(null=True, blank=True)

    # Gearbox specs
    gearbox_model = models.CharField(max_length=255)
    gearbox_ratio = models.FloatField()
    gearbox_output_speed = models.FloatField(help_text='rpm')
    gearbox_output_torque = models.FloatField(help_text='Nm')
    gearbox_nominal_torque = models.FloatField(null=True, blank=True, help_text='Nm')
    gearbox_starting_torque_max = models.FloatField(null=True, blank=True, help_text='Nm')
    gearbox_tip_torque_max = models.FloatField(null=True, blank=True, help_text='Nm')
    gearbox_efficiency_factor = models.FloatField(null=True, blank=True, help_text='CG factor')
    gearbox_output_flange = models.CharField(max_length=100)
    gearbox_output_shaft = models.CharField(max_length=100)
    gearbox_oil_capacity = models.FloatField(null=True, blank=True, help_text='liters')
    gearbox_oil_type = models.CharField(max_length=255, blank=True)

    # Compliance
    compliant = models.BooleanField(default=False)
    compliance_notes = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pdf_url = models.URLField(blank=True, help_text='Link to supplier datasheet')

    class Meta:
        ordering = ['model_number']

    def __str__(self):
        return f"{self.model_number} - {self.model_name}"
