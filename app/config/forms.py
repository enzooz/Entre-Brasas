"""
Formulario de la app Config.
"""
from django import forms
from decimal import Decimal

from .models import Configuracion


class ConfiguracionForm(forms.ModelForm):
    distancia_minima = forms.DecimalField(
        label='Distancia mínima para cobrar envío (km)', max_digits=4,
        decimal_places=1, min_value=0, max_value=Decimal('999.9'),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '999.9', 'step': '0.1'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        distancia = self.initial.get('distancia_minima')
        if distancia is not None:
            # Mostrar 1 o 1.1, no los dos decimales del almacenamiento histórico.
            self.initial['distancia_minima'] = format(Decimal(str(distancia)).normalize(), 'f')

    class Meta:
        model = Configuracion
        fields = [
            'tarifa_100m',
            'distancia_minima',
            'costo_minimo_envio',
            'costo_hora_mano_obra',
            'whatsapp_cocina',
        ]

        # min='0' hace que el navegador no deje escribir numeros negativos.
        # step='0.1' permite cargar decimales en la distancia.
        widgets = {
            'tarifa_100m': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'aria-describedby': 'ayudaTarifa'}),
            'distancia_minima': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'costo_minimo_envio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'aria-describedby': 'ayudaEnvioMinimo'}),
            'costo_hora_mano_obra': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'whatsapp_cocina': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '5493624000000'}),
        }

        labels = {
            'distancia_minima': 'Distancia mínima para cobrar envío (km)',
            'costo_minimo_envio': 'Envío mínimo / importe base ($)',
        }

    def clean_whatsapp_cocina(self):
        """Deja solo los numeros: saca espacios, guiones y el + del principio."""
        numero = self.cleaned_data.get('whatsapp_cocina', '')
        return ''.join(caracter for caracter in numero if caracter.isdigit())
