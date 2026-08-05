from django import forms
from .models import Hamburger, Addon


class HamburgerForm(forms.ModelForm):
    class Meta:
        model = Hamburger
        fields = ['nombre', 'descripcion', 'precio_base', 'incluye_papas']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio_base': forms.NumberInput(attrs={'class': 'form-control'}),
            'incluye_papas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        error_messages = {
            'nombre': {'unique': 'Ya existe una hamburguesa con ese nombre'},
        }

    def clean_precio_base(self):
        precio = self.cleaned_data.get('precio_base')
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0')
        return precio


class AddonForm(forms.ModelForm):
    class Meta:
        model = Addon
        fields = ['nombre', 'precio', 'productos']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'productos': forms.CheckboxSelectMultiple(),
        }
        error_messages = {
            'nombre': {'unique': 'Ya existe un adicional con ese nombre'},
        }

    def clean(self):
        cleaned_data = super().clean()
        productos = cleaned_data.get('productos')
        if not productos:
            raise forms.ValidationError('Debe asociar al menos un producto')
        return cleaned_data

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0')
        return precio
