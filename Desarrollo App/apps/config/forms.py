"""
Formulario del app "config": edita la única fila de SystemConfig.

No tiene métodos clean() porque la validación alcanza con lo que ya hacen
los modelos (PositiveIntegerField no admite negativos) y los atributos
min de los widgets, que el navegador respeta.
"""

from django import forms
from .models import SystemConfig


class SystemConfigForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        fields = ['tarifa_km', 'distancia_minima', 'costo_minimo_envio', 'costo_hora_mano_obra']
        widgets = {
            # min='0' impide números negativos desde el navegador.
            'tarifa_km': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            # step='0.1' permite cargar decimales (la distancia es un DecimalField).
            'distancia_minima': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'costo_minimo_envio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'costo_hora_mano_obra': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
