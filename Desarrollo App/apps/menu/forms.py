"""
Formularios del app "menu".

A diferencia de OrderForm (que está escrito pero no se usa), ESTOS SÍ se usan:
las vistas de menu/views.py los instancian y llaman a is_valid().
Por eso las validaciones de acá abajo sí se ejecutan de verdad.
"""

from django import forms
from .models import Hamburger, Addon


class HamburgerForm(forms.ModelForm):
    class Meta:
        model = Hamburger
        # 'activa' no está en la lista a propósito: se maneja con el botón
        # toggle, no editando el producto.
        fields = ['nombre', 'descripcion', 'precio_base', 'incluye_papas']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio_base': forms.NumberInput(attrs={'class': 'form-control'}),
            'incluye_papas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        # Reemplaza el mensaje técnico por defecto de Django ("Hamburger with this
        # Nombre already exists") por uno en castellano.
        error_messages = {
            'nombre': {'unique': 'Ya existe una hamburguesa con ese nombre'},
        }

    def clean_precio_base(self):
        """Validación de un campo: Django llama solo a los clean_NOMBRECAMPO."""
        precio = self.cleaned_data.get('precio_base')
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0')
        return precio  # siempre hay que devolver el valor


class AddonForm(forms.ModelForm):
    class Meta:
        model = Addon
        fields = ['nombre', 'precio', 'productos']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            # Para el ManyToMany: en vez de una lista desplegable, muestra
            # una casilla por hamburguesa para tildar varias.
            'productos': forms.CheckboxSelectMultiple(),
        }
        error_messages = {
            'nombre': {'unique': 'Ya existe un adicional con ese nombre'},
        }

    def clean(self):
        """
        clean() sin sufijo valida el formulario COMPLETO, no un campo suelto.

        Se usa cuando la regla involucra varios campos o, como acá, cuando hay
        que revisar algo que el campo solo no puede: que se haya tildado al
        menos un producto.

        El super().clean() del principio es obligatorio: ejecuta primero las
        validaciones campo por campo.
        """
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
