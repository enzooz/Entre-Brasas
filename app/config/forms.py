"""
Formulario de la app Config.
"""
from django import forms

from .models import Configuracion


class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = [
            'tarifa_km',
            'distancia_minima',
            'costo_minimo_envio',
            'costo_hora_mano_obra',
            'whatsapp_cocina',
        ]

        # min='0' hace que el navegador no deje escribir numeros negativos.
        # step='0.1' permite cargar decimales en la distancia.
        widgets = {
            'tarifa_km': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'distancia_minima': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'costo_minimo_envio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'costo_hora_mano_obra': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'whatsapp_cocina': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '5493624000000'}),
        }

    def clean_whatsapp_cocina(self):
        """Deja solo los numeros: saca espacios, guiones y el + del principio."""
        numero = self.cleaned_data.get('whatsapp_cocina', '')
        return ''.join(caracter for caracter in numero if caracter.isdigit())
