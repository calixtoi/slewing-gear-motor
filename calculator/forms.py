from django import forms
from .models import MotorCalculation


FLOAT_WIDGET     = {'class': 'form-control form-control-sm', 'step': 'any'}
FLOAT_WIDGET_OPT = {'class': 'form-control form-control-sm', 'step': 'any', 'placeholder': 'optional'}
TEXT_WIDGET      = {'class': 'form-control form-control-sm'}
TEXT_WIDGET_OPT  = {'class': 'form-control form-control-sm', 'placeholder': 'optional'}


class DrivetrainForm(forms.Form):
    # ── Crane load ──────────────────────────────────────────────────────────
    crane_torque_max = forms.FloatField(
        label='Maximum Torque',
        min_value=0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 41 190'}),
    )
    crane_torque_nom = forms.FloatField(
        label='Nominal Torque',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'e.g. 15 360 (enables gearbox sizing)'}),
    )

    # ── Worm gear ────────────────────────────────────────────────────────────
    worm_ratio = forms.FloatField(
        label='Worm Gear Ratio',
        min_value=1,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 121'}),
    )
    worm_efficiency = forms.FloatField(
        label='Worm Gear Efficiency',
        min_value=0.01, max_value=1.0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 0.40'}),
    )

    # ── Motor ────────────────────────────────────────────────────────────────
    motor_speed = forms.FloatField(
        label='Motor Speed',
        min_value=1,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 1454'}),
    )
    motor_rated_torque = forms.FloatField(
        label='Motor Rated Torque',
        min_value=0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 12'}),
    )
    starting_factor = forms.FloatField(
        label='Starting Factor',
        min_value=0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 3.40'}),
    )

    bevel_efficiency = forms.FloatField(
        label='Bevel Gearbox Efficiency',
        min_value=0.01, max_value=1.0,
        initial=0.95,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 0.95'}),
    )

    # ── Gearbox ──────────────────────────────────────────────────────────────
    gearbox_output_speed = forms.FloatField(
        label='Gearbox Output Speed',
        required=False,
        min_value=0.001,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'e.g. 43.5'}),
    )
    gear_ratio = forms.FloatField(
        label='Bevel Gear Ratio',
        required=False,
        min_value=0.001,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'e.g. 27.65'}),
    )

    # ── Supplier data (optional comparison) ─────────────────────────────────
    supplier_motor_power_kw = forms.FloatField(
        label='Motor Power',
        required=False, min_value=0,
        widget=forms.NumberInput(attrs=FLOAT_WIDGET_OPT),
    )
    supplier_motor_rated_torque = forms.FloatField(
        label='Motor Rated Torque',
        required=False, min_value=0,
        widget=forms.NumberInput(attrs=FLOAT_WIDGET_OPT),
    )
    supplier_motor_starting_torque = forms.FloatField(
        label='Motor Starting Torque',
        required=False, min_value=0,
        widget=forms.NumberInput(attrs=FLOAT_WIDGET_OPT),
    )
    supplier_gearbox_rated_torque = forms.FloatField(
        label='Gearbox Rated Torque',
        required=False, min_value=0,
        widget=forms.NumberInput(attrs=FLOAT_WIDGET_OPT),
    )
    supplier_bevel_ratio = forms.FloatField(
        label='Bevel Gear Ratio',
        required=False, min_value=0,
        widget=forms.NumberInput(attrs=FLOAT_WIDGET_OPT),
    )
    supplier_worm_ratio = forms.FloatField(
        label='Worm Gear Ratio',
        required=False, min_value=0,
        widget=forms.NumberInput(attrs=FLOAT_WIDGET_OPT),
    )

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('gearbox_output_speed') and not cleaned.get('gear_ratio'):
            raise forms.ValidationError(
                'Enter either the Gearbox output speed or the Gear ratio — at least one is required.',
                code='gearbox_speed_missing',
            )
        return cleaned


class MotorSpecsForm(forms.Form):
    """Motor physical specification fields for compliance checking and storage."""

    spec_frame_material = forms.CharField(
        label='Frame Material', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. Cast Iron / GJL-250'}),
    )
    spec_output_flange = forms.CharField(
        label='Motor Flange (IEC90 B5)', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. IEC90 B5 · Ø165 mm'}),
    )
    spec_shaft = forms.CharField(
        label='Shaft', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. 32 × 50'}),
    )
    spec_cooling_method = forms.CharField(
        label='Cooling Method', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. IC410 TENV'}),
    )
    spec_ip_rating = forms.CharField(
        label='IP Rating', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. IP66'}),
    )
    spec_ambient_temp = forms.CharField(
        label='Ambient Temperature', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. -20°C to +45°C'}),
    )
    spec_coating = forms.CharField(
        label='Coating Class', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. C5H / EN 12944-5'}),
    )
    spec_top_color = forms.CharField(
        label='Top Color', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. RAL7035'}),
    )
    spec_heater = forms.CharField(
        label='Standstill Heater', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. 24VDC'}),
    )
    spec_insulation_class = forms.CharField(
        label='Insulation Class', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. F or H'}),
    )
    spec_duty_cycle = forms.CharField(
        label='Duty Cycle', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. S3-25%'}),
    )
    spec_painting = forms.CharField(
        label='Painting Description', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. Marine C5H system, epoxy primer'}),
    )
    spec_motor_certificate = forms.CharField(
        label='Motor Certificate', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. DNV, GL, ABS'}),
    )
    spec_weight_kg = forms.FloatField(
        label='Weight (kg)', required=False, min_value=0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'e.g. 45'}),
    )
    spec_efficiency_class = forms.CharField(
        label='Efficiency Class', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. IE2, IE3, IE4'}),
    )
    spec_voltage = forms.CharField(
        label='Voltage / Frequency', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. 400/690V 50Hz · 400/480/690V 60Hz'}),
    )


class SaveCalculationForm(forms.Form):
    supplier_name = forms.CharField(
        max_length=200,
        label='Supplier / Motor name',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'e.g. Siemens 1LA7 0.75 kW',
        }),
    )
    crane_type = forms.ChoiceField(
        choices=MotorCalculation.CRANE_CHOICES,
        label='Crane type',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    price_prototype = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False,
        label='Prototype Price (€)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'step': '0.01', 'placeholder': 'e.g. 1250.00',
        }),
    )
    price_series = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False,
        label='Series Price — 100 units (€)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'step': '0.01', 'placeholder': 'e.g. 980.00',
        }),
    )


class TextDatasheetForm(forms.Form):
    supplier_name = forms.CharField(
        max_length=200, label='Supplier Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'e.g. Bonfiglioli, ABB, Siemens',
        }),
    )
    crane_type = forms.ChoiceField(
        choices=MotorCalculation.CRANE_CHOICES,
        label='Crane Type',
        initial=MotorCalculation.STANDARD_PF,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    price_prototype = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False,
        label='Prototype Price (€)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'step': '0.01', 'placeholder': 'e.g. 1250.00',
        }),
    )
    price_series = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False,
        label='Series Price — 100 units (€)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'step': '0.01', 'placeholder': 'e.g. 980.00',
        }),
    )
    text_content = forms.CharField(
        label='Datasheet Text',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': (
                'Paste the full datasheet text from the supplier email or PDF.\n\n'
                'Lines the parser looks for (examples):\n'
                '  Rated power: 0.75 kW\n'
                '  Rated speed: 1454 rpm\n'
                '  Rated torque (Mn): 4.9 Nm\n'
                '  Ma/Mn: 3.4\n'
                '  Starting torque: 16.7 Nm\n'
                '  Output torque: 405 Nm\n'
                '  Reduction ratio: 33.4:1'
            ),
        }),
    )


class DatasheetUploadForm(forms.Form):
    pdf_file = forms.FileField(
        label='PDF Datasheet',
        widget=forms.FileInput(attrs={
            'class': 'form-control form-control-sm',
            'accept': '.pdf',
        }),
    )
    supplier_name = forms.CharField(
        max_length=200,
        label='Supplier Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'e.g. Bonfiglioli, ABB, Siemens',
        }),
    )
    crane_type = forms.ChoiceField(
        choices=MotorCalculation.CRANE_CHOICES,
        label='Crane Type',
        initial=MotorCalculation.STANDARD_PF,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    price_prototype = forms.DecimalField(
        max_digits=10, decimal_places=2,
        required=False,
        label='Prototype Price (€)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'step': '0.01',
            'placeholder': 'e.g. 1250.00',
        }),
    )
    price_series = forms.DecimalField(
        max_digits=10, decimal_places=2,
        required=False,
        label='Series Price — 100 units (€)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'step': '0.01',
            'placeholder': 'e.g. 980.00',
        }),
    )
