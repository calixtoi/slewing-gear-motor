from django import forms
from .models import DesignParameters


class DesignParametersForm(forms.ModelForm):
    class Meta:
        model = DesignParameters
        fields = [
            'crane_peak_torque_pf200_kNm',
            'crane_peak_torque_tp_kNm',
            'crane_peak_torque_substation_kNm',
            'slewing_ring_ratio_pm401',
            'slewing_ring_ratio_pf200_ref',
            'motor_torque_share_fraction',
            'crane_max_slewing_speed_rpm',
            'crane_min_slewing_speed_rpm',
        ]
        labels = {
            'crane_peak_torque_pf200_kNm': 'Crane peak slewing torque — PF200 reference (kNm)',
            'crane_peak_torque_tp_kNm': 'Crane peak slewing torque — PM010 / TP operation (kNm)',
            'crane_peak_torque_substation_kNm': 'Crane peak slewing torque — PM401 / Substation — worst case (kNm)',
            'slewing_ring_ratio_pm401': 'Slewing ring gear ratio — PM401 / Substation (dimensionless)',
            'slewing_ring_ratio_pf200_ref': 'Slewing ring gear ratio — PF200 / PM010 reference (dimensionless)',
            'motor_torque_share_fraction': 'Motor torque share — design rule minimum (fraction)',
            'crane_max_slewing_speed_rpm': 'Practical maximum crane slewing speed (revolutions per minute)',
            'crane_min_slewing_speed_rpm': 'Minimum crane slewing speed (revolutions per minute)',
        }
        widgets = {
            'crane_peak_torque_pf200_kNm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'crane_peak_torque_tp_kNm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'crane_peak_torque_substation_kNm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'slewing_ring_ratio_pm401': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'slewing_ring_ratio_pf200_ref': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'motor_torque_share_fraction': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'crane_max_slewing_speed_rpm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'crane_min_slewing_speed_rpm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
