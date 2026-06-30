from django import forms
from .models import MotorSupplier


class MotorSupplierForm(forms.ModelForm):
    class Meta:
        model = MotorSupplier
        fields = [
            'supplier_name', 'motor_model', 'datasheet_source', 'notes',
            'gear_series', 'gearmotor_output_speed_rpm', 'gearmotor_output_torque_nm',
            'gearbox_internal_ratio', 'max_permissible_input_speed_rpm', 'mounting_position',
            'output_flange_description', 'output_shaft_description', 'keyway_standard',
            'painting_system', 'colour_ral', 'input_flange_description',
            'housing_material', 'duty_cycle', 'efficiency_class', 'motor_rated_power_kw',
            'motor_rated_speed_rpm', 'supply_voltage_v', 'supply_frequency_hz',
            'winding_connection', 'protection_class', 'terminal_box_position', 'cable_entries',
            'cooling_method', 'heater_spec', 'total_weight_kg', 'certifications',
            'temperature_range', 'corrosivity_category', 'rotation', 'starting_method',
            'heater_terminal_blocks', 'gearbox_structural_capacity_nm',
        ]
        widgets = {
            'supplier_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Siemens, Bonfiglioli'}),
            'motor_model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. BFME112M-4B'}),
            'datasheet_source': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document ref or datasheet URL'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'General notes about this supplier'}),
            # Gear data
            'gear_series': forms.TextInput(attrs={'class': 'form-control'}),
            'gearmotor_output_speed_rpm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'gearmotor_output_torque_nm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'gearbox_internal_ratio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_permissible_input_speed_rpm': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'mounting_position': forms.TextInput(attrs={'class': 'form-control'}),
            'output_flange_description': forms.TextInput(attrs={'class': 'form-control'}),
            'output_shaft_description': forms.TextInput(attrs={'class': 'form-control'}),
            'keyway_standard': forms.TextInput(attrs={'class': 'form-control'}),
            'painting_system': forms.TextInput(attrs={'class': 'form-control'}),
            'colour_ral': forms.TextInput(attrs={'class': 'form-control'}),
            # Input side
            'input_flange_description': forms.TextInput(attrs={'class': 'form-control'}),
            # Motor data
            'housing_material': forms.TextInput(attrs={'class': 'form-control'}),
            'duty_cycle': forms.TextInput(attrs={'class': 'form-control'}),
            'efficiency_class': forms.TextInput(attrs={'class': 'form-control'}),
            'motor_rated_power_kw': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'motor_rated_speed_rpm': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'supply_voltage_v': forms.TextInput(attrs={'class': 'form-control'}),
            'supply_frequency_hz': forms.TextInput(attrs={'class': 'form-control'}),
            'winding_connection': forms.TextInput(attrs={'class': 'form-control'}),
            'protection_class': forms.TextInput(attrs={'class': 'form-control'}),
            'terminal_box_position': forms.TextInput(attrs={'class': 'form-control'}),
            'cable_entries': forms.TextInput(attrs={'class': 'form-control'}),
            # Further executions
            'cooling_method': forms.TextInput(attrs={'class': 'form-control'}),
            'heater_spec': forms.TextInput(attrs={'class': 'form-control'}),
            'total_weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            # General
            'certifications': forms.TextInput(attrs={'class': 'form-control'}),
            'temperature_range': forms.TextInput(attrs={'class': 'form-control'}),
            'corrosivity_category': forms.TextInput(attrs={'class': 'form-control'}),
            'rotation': forms.TextInput(attrs={'class': 'form-control'}),
            'starting_method': forms.TextInput(attrs={'class': 'form-control'}),
            'heater_terminal_blocks': forms.TextInput(attrs={'class': 'form-control'}),
            'gearbox_structural_capacity_nm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }


class PdfUploadForm(forms.Form):
    pdf_file = forms.FileField(
        label='Upload PDF datasheet',
        help_text='Maximum 10 MB',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'})
    )


class TextPasteForm(forms.Form):
    raw_text = forms.CharField(
        label='Paste supplier text or email',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Paste supplier email, PDF text, quote, or technical note...'
        })
    )
    use_ai = forms.BooleanField(
        label='Use AI extraction (if available)',
        required=False,
        help_text='Attempts to use OpenAI GPT to extract data (requires OPENAI_API_KEY)'
    )
