from django.db import models


class MotorSupplier(models.Model):
    """Motor supplier specification data for verification against ideal parameters."""

    supplier_name = models.CharField(
        max_length=200,
        help_text="Supplier name or company"
    )
    motor_model = models.CharField(
        max_length=300,
        help_text="Motor model / type designation"
    )
    datasheet_source = models.CharField(
        max_length=500,
        blank=True,
        help_text="Source document or reference"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(
        blank=True,
        help_text="General notes"
    )

    # GEAR DATA
    gear_series = models.CharField(
        max_length=200,
        blank=True,
        help_text="Gear series (e.g. helical bevel geared motor)"
    )
    gearmotor_output_speed_rpm = models.FloatField(
        null=True,
        blank=True,
        help_text="Gearmotor output speed (revolutions per minute)"
    )
    gearmotor_output_torque_nm = models.FloatField(
        null=True,
        blank=True,
        help_text="Gearmotor rated output torque (Newton-metres)"
    )
    gearbox_internal_ratio = models.FloatField(
        null=True,
        blank=True,
        help_text="Gearbox internal ratio (dimensionless)"
    )
    max_permissible_input_speed_rpm = models.FloatField(
        null=True,
        blank=True,
        help_text="Maximum permissible motor input speed (revolutions per minute)"
    )
    mounting_position = models.CharField(
        max_length=100,
        blank=True,
        help_text="Mounting position (e.g. M2, M4, M5)"
    )
    output_flange_description = models.CharField(
        max_length=300,
        blank=True,
        help_text="Output flange description"
    )
    output_shaft_description = models.CharField(
        max_length=200,
        blank=True,
        help_text="Output shaft specification"
    )
    keyway_standard = models.CharField(
        max_length=100,
        blank=True,
        help_text="Keyway standard"
    )
    painting_system = models.CharField(
        max_length=100,
        blank=True,
        help_text="Painting / corrosion protection system"
    )
    colour_ral = models.CharField(
        max_length=50,
        blank=True,
        help_text="Colour (RAL code)"
    )

    # INPUT SIDE
    input_flange_description = models.CharField(
        max_length=300,
        blank=True,
        help_text="Input flange description"
    )

    # MOTOR DATA
    housing_material = models.CharField(
        max_length=100,
        blank=True,
        help_text="Motor housing material"
    )
    duty_cycle = models.CharField(
        max_length=50,
        blank=True,
        help_text="Motor duty cycle (e.g. S3-25%)"
    )
    efficiency_class = models.CharField(
        max_length=20,
        blank=True,
        help_text="Motor efficiency class (e.g. IE2, IE3)"
    )
    motor_rated_power_kw = models.FloatField(
        null=True,
        blank=True,
        help_text="Motor rated power (kilowatts)"
    )
    motor_rated_speed_rpm = models.FloatField(
        null=True,
        blank=True,
        help_text="Motor rated speed (revolutions per minute)"
    )
    supply_voltage_v = models.CharField(
        max_length=100,
        blank=True,
        help_text="Supply voltage (Volts)"
    )
    supply_frequency_hz = models.CharField(
        max_length=50,
        blank=True,
        help_text="Supply frequency (Hertz)"
    )
    winding_connection = models.CharField(
        max_length=50,
        blank=True,
        help_text="Winding connection (Delta / Star)"
    )
    protection_class = models.CharField(
        max_length=20,
        blank=True,
        help_text="Degree of protection (IP class)"
    )
    terminal_box_position = models.CharField(
        max_length=200,
        blank=True,
        help_text="Terminal box mounting position"
    )
    cable_entries = models.CharField(
        max_length=200,
        blank=True,
        help_text="Cable entry thread sizes"
    )

    # FURTHER EXECUTIONS
    cooling_method = models.CharField(
        max_length=100,
        blank=True,
        help_text="Cooling method (IC designation)"
    )
    heater_spec = models.CharField(
        max_length=100,
        blank=True,
        help_text="Anti-condensation heater specification (Watts / Volts)"
    )
    total_weight_kg = models.FloatField(
        null=True,
        blank=True,
        help_text="Total weight of gearmotor (kilograms)"
    )

    # GENERAL
    certifications = models.CharField(
        max_length=300,
        blank=True,
        help_text="Certifications (CE, 3.1, UL, UKCA, etc.)"
    )
    temperature_range = models.CharField(
        max_length=100,
        blank=True,
        help_text="Ambient temperature range"
    )
    corrosivity_category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Corrosivity category (C4, C5H, C5M, CX)"
    )
    rotation = models.CharField(
        max_length=100,
        blank=True,
        help_text="Direction of rotation"
    )
    starting_method = models.CharField(
        max_length=100,
        blank=True,
        help_text="Starting method"
    )
    heater_terminal_blocks = models.CharField(
        max_length=200,
        blank=True,
        help_text="Anti-condensation heater terminal block provision"
    )
    gearbox_structural_capacity_nm = models.FloatField(
        null=True,
        blank=True,
        help_text="Gearbox structural torque capacity (Newton-metres)"
    )

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Motor Supplier"
        verbose_name_plural = "Motor Suppliers"

    def __str__(self):
        return f"{self.supplier_name} - {self.motor_model}"
