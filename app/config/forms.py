"""
Formulario de la app Config.
"""
from django import forms
from decimal import Decimal
import math

from .models import Configuracion


class ConfiguracionForm(forms.ModelForm):
    geoapify_api_key = forms.CharField(
        label='Clave de Geoapify (API key)', required=False, max_length=128,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )
    eliminar_clave_geoapify = forms.BooleanField(label='Eliminar la clave guardada', required=False)
    local_latitud = forms.FloatField(label='Latitud del local', required=False, min_value=-90, max_value=90,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}))
    local_longitud = forms.FloatField(label='Longitud del local', required=False, min_value=-180, max_value=180,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}))
    distancia_minima = forms.DecimalField(
        label='Distancia incluida en el envío mínimo (km)', max_digits=4,
        decimal_places=1, min_value=0, max_value=Decimal('999.9'),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '999.9', 'step': '0.1'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clave_guardada = bool(self.instance.geoapify_api_key)
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
            'geoapify_api_key', 'local_latitud', 'local_longitud',
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
            'distancia_minima': 'Distancia incluida en el envío mínimo (km)',
            'costo_minimo_envio': 'Envío mínimo ($)',
        }

    def clean_whatsapp_cocina(self):
        """Deja solo los numeros: saca espacios, guiones y el + del principio."""
        numero = self.cleaned_data.get('whatsapp_cocina', '')
        return ''.join(caracter for caracter in numero if caracter.isdigit())

    def clean_geoapify_api_key(self):
        import re
        clave = self.cleaned_data.get('geoapify_api_key', '').strip()
        if clave and not re.fullmatch(r'[A-Za-z0-9_-]+', clave):
            raise forms.ValidationError('Pegá solamente la API key, no el enlace completo.')
        return clave

    def clean(self):
        datos = super().clean()
        if datos.get('eliminar_clave_geoapify'):
            datos['geoapify_api_key'] = ''
        elif not datos.get('geoapify_api_key'):
            datos['geoapify_api_key'] = self.instance.geoapify_api_key
        for campo in ('local_latitud', 'local_longitud'):
            if datos.get(campo) is None:
                datos[campo] = getattr(self.instance, campo)
            elif not math.isfinite(datos[campo]):
                self.add_error(campo, 'Ingresá una coordenada válida.')
        return datos
