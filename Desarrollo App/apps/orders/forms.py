from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'cliente_nombre', 'cliente_telefono', 'cliente_direccion',
            'observaciones', 'metodo_pago', 'distancia_km', 'retiro_local'
        ]
        widgets = {
            'cliente_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente_telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente_direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            'distancia_km': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'retiro_local': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_cliente_telefono(self):
        telefono = self.cleaned_data.get('cliente_telefono')
        import re
        if not re.match(r'^[\d\s\-\(\)+]+$', telefono):
            raise forms.ValidationError('Ingrese un número de teléfono válido')
        return telefono
