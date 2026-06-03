from django import forms
from .models import MotorCalculation


FLOAT_WIDGET     = {'class': 'form-control form-control-sm', 'step': 'any'}
FLOAT_WIDGET_OPT = {'class': 'form-control form-control-sm', 'step': 'any', 'placeholder': 'optional'}
TEXT_WIDGET      = {'class': 'form-control form-control-sm'}
TEXT_WIDGET_OPT  = {'class': 'form-control form-control-sm', 'placeholder': 'optional'}


class DrivetrainForm(forms.Form):
    # ── Crane type (new interface) ───────────────────────────────────────────
    crane_type = forms.ChoiceField(
        label='Crane Type',
        choices=[
            ('standard_pf', 'Standard PF Crane'),
            ('pf_xxl', 'PF-XXL Crane'),
        ],
        required=False,
        initial='standard_pf',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )

    # ── Motor specs (new interface) ───────────────────────────────────────────
    motor_power = forms.FloatField(
        label='Motor Power (kW)',
        required=False,
        min_value=0.01,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'e.g. 0.75'}),
    )
    motor_speed_new = forms.FloatField(
        label='Motor Speed (RPM)',
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'e.g. 1410'}),
    )

    # ── Gearbox output specs (new interface) ───────────────────────────────────
    supplier_output_torque = forms.FloatField(
        label='Geared Motor Output Torque (Nm)',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'e.g. 141'}),
    )
    supplier_starting_torque = forms.FloatField(
        label='Geared Motor Starting Torque (Nm)',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'e.g. 295'}),
    )

    # ── Gearbox ratio ────────────────────────────────────────────────────────
    gearbox_output_speed = forms.FloatField(
        label='Gearbox Output Speed (RPM)',
        required=False,
        min_value=0.001,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'e.g. 51'}),
    )
    gear_ratio = forms.FloatField(
        label='Gearbox Ratio (i_gb)',
        required=False,
        min_value=0.001,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'e.g. 27.82'}),
    )

    # ── Starting factor ──────────────────────────────────────────────────────
    mk_mn_ratio = forms.FloatField(
        label='Ma/Mn Starting Factor',
        required=False,
        min_value=0,
        initial=3.40,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'e.g. 3.40'}),
    )

    # ── Legacy fields (for backward compatibility) ───────────────────────────
    crane_torque_max = forms.FloatField(
        label='Maximum Torque (Nm)',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'e.g. 41 190'}),
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
                'Enter either the Gearbox output speed (RPM) or the Gearbox ratio (i_gb) — at least one is required.',
                code='gearbox_speed_missing',
            )
        return cleaned


class MotorSpecsForm(forms.Form):
    motor_type           = forms.CharField(required=False, label='Motor type',               widget=forms.TextInput(attrs={'placeholder': 'Squirrel cage async helical bevel gearmotor marine execution'}))
    frame_material       = forms.CharField(required=False, label='Frame / housing material',  widget=forms.TextInput(attrs={'placeholder': 'Cast Iron'}))
    input_flange_mm      = forms.FloatField(required=False, label='Input flange diameter (mm)', widget=forms.NumberInput(attrs={'placeholder': '165'}))
    output_flange_type   = forms.CharField(required=False, label='Output flange type',         widget=forms.TextInput(attrs={'placeholder': 'Square IEC O200 mm'}))
    output_shaft_mm      = forms.FloatField(required=False, label='Output shaft diameter (mm)', widget=forms.NumberInput(attrs={'placeholder': '32'}))
    output_shaft_length_mm = forms.FloatField(required=False, label='Output shaft length from flange (mm)', widget=forms.NumberInput(attrs={'placeholder': '50'}))
    cooling_method       = forms.CharField(required=False, label='Cooling method',             widget=forms.TextInput(attrs={'placeholder': 'IC410 TENV'}))
    ip_rating            = forms.CharField(required=False, label='IP protection class',        widget=forms.TextInput(attrs={'placeholder': 'IP66'}))
    insulation_class     = forms.CharField(required=False, label='Insulation class',           widget=forms.TextInput(attrs={'placeholder': 'H'}))
    efficiency_class     = forms.CharField(required=False, label='Efficiency class',           widget=forms.TextInput(attrs={'placeholder': 'IE2'}))
    duty_cycle           = forms.ChoiceField(required=False, label='Duty cycle', choices=[('','— Select —'),('S1','S1'),('S2-30min','S2-30min'),('S2-12min','S2-12min'),('S3-60%','S3-60%'),('S3-40%','S3-40%'),('S3-25%','S3-25%'),('S3-15%','S3-15%')])
    ambient_temp_min_c   = forms.FloatField(required=False, label='Ambient temp minimum (deg C)', widget=forms.NumberInput(attrs={'placeholder': '-20'}))
    ambient_temp_max_c   = forms.FloatField(required=False, label='Ambient temp maximum (deg C)', widget=forms.NumberInput(attrs={'placeholder': '45'}))
    voltage_400_50       = forms.ChoiceField(required=False, label='400V / 50Hz',  choices=[('','— Not confirmed —'),('Yes','Yes — confirmed'),('No','No')])
    voltage_400_60       = forms.ChoiceField(required=False, label='400V / 60Hz',  choices=[('','— Not confirmed —'),('Yes','Yes — confirmed'),('No','No')])
    voltage_480_60       = forms.ChoiceField(required=False, label='480V / 60Hz',  choices=[('','— Not confirmed —'),('Yes','Yes — confirmed'),('No','No')])
    voltage_690_50       = forms.ChoiceField(required=False, label='690V / 50Hz',  choices=[('','— Not confirmed —'),('Yes','Yes — confirmed'),('No','No')])
    voltage_690_60       = forms.ChoiceField(required=False, label='690V / 60Hz',  choices=[('','— Not confirmed —'),('Yes','Yes — confirmed'),('No','No')])
    heater_voltage_vdc   = forms.FloatField(required=False, label='Standstill heater (VDC)',   widget=forms.NumberInput(attrs={'placeholder': '24'}))
    coating_standard     = forms.CharField(required=False, label='Coating standard',           widget=forms.TextInput(attrs={'placeholder': 'C5H EN 12944-5'}))
    surface_prep         = forms.CharField(required=False, label='Surface preparation',        widget=forms.TextInput(attrs={'placeholder': 'ISO 8501-3 Level P3'}))
    coating_ndft_um      = forms.FloatField(required=False, label='Coating NDFT (um)',         widget=forms.NumberInput(attrs={'placeholder': '320'}))
    paint_color          = forms.CharField(required=False, label='Paint colour',               widget=forms.TextInput(attrs={'placeholder': 'RAL 7035'}))
    output_flange_coating = forms.CharField(required=False, label='Output flange coating',    widget=forms.TextInput(attrs={'placeholder': '1x primer only'}))
    fasteners            = forms.CharField(required=False, label='Fasteners material',         widget=forms.TextInput(attrs={'placeholder': 'Stainless A4'}))
    shaft_seal           = forms.CharField(required=False, label='Shaft seal material',        widget=forms.TextInput(attrs={'placeholder': 'FPM Viton'}))
    nameplate            = forms.CharField(required=False, label='Nameplate material',         widget=forms.TextInput(attrs={'placeholder': 'Stainless steel'}))


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
