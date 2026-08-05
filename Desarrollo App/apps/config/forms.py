from django import forms
from .models import SystemConfig


class SystemConfigForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        fields = ['tarifa_km', 'distancia_minima', 'costo_minimo_envio', 'costo_hora_mano_obra']
        widgets = {
            'tarifa_km': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'distancia_minima': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'costo_minimo_envio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'costo_hora_mano_obra': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
