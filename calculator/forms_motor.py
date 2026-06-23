"""Motor entry forms for the 11-point validation system."""

from django import forms
from .models import Motor, RingSystem


FLOAT_WIDGET = {'class': 'form-control form-control-sm', 'step': 'any'}
FLOAT_WIDGET_OPT = {'class': 'form-control form-control-sm', 'step': 'any', 'placeholder': 'optional'}
TEXT_WIDGET = {'class': 'form-control form-control-sm'}
TEXT_WIDGET_OPT = {'class': 'form-control form-control-sm', 'placeholder': 'optional'}


class MotorForm(forms.ModelForm):
    """Form for entering motor datasheet specifications."""

    class Meta:
        model = Motor
        fields = [
            'supplier', 'model', 'gm_type',
            'i_gb', 'n_mot', 'P',
            'T_nom', 'T_pu', 'T_start', 'T_peak',
            'T_in_max', 'T_bd', 'fB',
            'duty', 'flange',
            'voltage', 'IP', 'insulation', 'heater', 'temp',
            'coating', 'frame', 'cooling', 'start_method', 'notes'
        ]
        widgets = {
            'supplier': forms.TextInput(attrs={**TEXT_WIDGET, 'placeholder': 'e.g. Watt Drive, Z:systems'}),
            'model': forms.TextInput(attrs={**TEXT_WIDGET, 'placeholder': 'e.g. EP2557M'}),
            'gm_type': forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. KF 60A 3C 80-04E'}),

            'i_gb': forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 27.82'}),
            'n_mot': forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 1410'}),
            'P': forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 0.75'}),

            'T_nom': forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'GM nominal output torque (Nm)'}),
            'T_pu': forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'GM pull-up torque (Nm) — optional'}),
            'T_start': forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'GM start/breakaway torque (Nm)'}),
            'T_peak': forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'GM peak/max torque (Nm)'}),

            'T_in_max': forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'Perm. GB input torque (Nm) — optional'}),
            'T_bd': forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'Motor breakdown torque (Nm) — optional'}),
            'fB': forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'Service factor — optional'}),

            'duty': forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. S2-12 min, S3-15, S3-25%'}),
            'flange': forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. □150 / Ø32 k6×50'}),

            'voltage': forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. 400/690 V 50 Hz'}),
            'IP': forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. IP66'}),
            'insulation': forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. H (Class H)'}),
            'heater': forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. 24 VDC'}),
            'temp': forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. −20 to +50°C'}),

            'coating': forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. C5H RAL7035'}),
            'frame': forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. Cast iron'}),
            'cooling': forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. IC410 TENV'}),
            'start_method': forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. DOL (direct-on-line)'}),

            'notes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3, 'placeholder': 'Any additional notes'}),
        }

    def __init__(self, *args, **kwargs):
        ring_system = kwargs.pop('ring_system', None)
        super().__init__(*args, **kwargs)
        if ring_system:
            self.instance.ring_system = ring_system


class QuickMotorForm(forms.Form):
    """Quick entry form with only required fields."""

    supplier = forms.CharField(max_length=200, label='Supplier', widget=forms.TextInput(attrs={**TEXT_WIDGET, 'placeholder': 'e.g. Watt Drive'}))
    model = forms.CharField(max_length=200, label='Model', widget=forms.TextInput(attrs={**TEXT_WIDGET, 'placeholder': 'e.g. EP2557M'}))

    i_gb = forms.FloatField(label='Gearbox ratio (i_gb)', widget=forms.NumberInput(attrs={**FLOAT_WIDGET}))
    n_mot = forms.FloatField(label='Motor speed (rpm)', widget=forms.NumberInput(attrs={**FLOAT_WIDGET}))
    P = forms.FloatField(label='Motor power (kW)', widget=forms.NumberInput(attrs={**FLOAT_WIDGET}))

    T_nom = forms.FloatField(label='GM nominal torque (Nm)', widget=forms.NumberInput(attrs={**FLOAT_WIDGET}))
    T_pu = forms.FloatField(label='GM pull-up torque (Nm)', required=False, widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT}))
    T_start = forms.FloatField(label='GM start torque (Nm)', widget=forms.NumberInput(attrs={**FLOAT_WIDGET}))
    T_peak = forms.FloatField(label='GM peak torque (Nm)', widget=forms.NumberInput(attrs={**FLOAT_WIDGET}))

    T_in_max = forms.FloatField(label='GB input limit (Nm)', required=False, widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT}))
    T_bd = forms.FloatField(label='Motor breakdown (Nm)', required=False, widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT}))

    duty = forms.CharField(max_length=100, label='Duty cycle', required=False, widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT}))
    flange = forms.CharField(max_length=200, label='Flange interface', required=False, widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT}))
