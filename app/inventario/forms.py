"""
Formularios de la app Inventario.
"""
from django import forms

from .models import Ingrediente, MovimientoInventario, Receta


class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente

        # Quedan afuera a proposito:
        #   precio_compra -> se actualiza solo cuando se registra una compra
        #   activo        -> se maneja con el boton de activar/desactivar
        fields = ['nombre', 'stock_actual', 'unidad', 'stock_minimo']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'unidad': forms.Select(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
        }

        error_messages = {
            'nombre': {'unique': 'Ya existe un ingrediente con ese nombre'},
        }

    def clean_stock_minimo(self):
        """
        El stock minimo tiene que ser mayor a cero.

        Si fuera cero, el aviso de "hay que reponer" no saltaria nunca y el
        ingrediente se terminaria sin que nadie se entere.
        """
        stock_minimo = self.cleaned_data.get('stock_minimo')

        if stock_minimo <= 0:
            raise forms.ValidationError('El stock minimo tiene que ser mayor a 0')

        return stock_minimo


class MovimientoForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario

        # pedido_relacionado no esta: ese campo lo completa el sistema solo
        # cuando el movimiento lo genera un pedido.
        fields = ['ingrediente', 'tipo', 'cantidad', 'precio_unitario', 'motivo']

        widgets = {
            # Django arma la lista de ingredientes sola, a partir de la relacion.
            'ingrediente': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Solo para compras (opcional)',
            }),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_cantidad(self):
        """
        La cantidad siempre es positiva.

        Que el movimiento sume o reste lo decide el campo "tipo"
        (entrada o salida), no el signo del numero.
        """
        cantidad = self.cleaned_data.get('cantidad')

        if cantidad <= 0:
            raise forms.ValidationError('La cantidad tiene que ser mayor a 0')

        return cantidad

    def clean_motivo(self):
        """
        El motivo es obligatorio para poder revisar despues por que se movio
        el stock.

        strip() saca los espacios de los costados, asi alguien no puede poner
        solo espacios para zafar. Ademas guarda el texto ya limpio.
        """
        motivo = self.cleaned_data.get('motivo')

        if not motivo or not motivo.strip():
            raise forms.ValidationError('Hay que escribir el motivo del movimiento')

        return motivo.strip()


class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta

        # Solo pedimos el ingrediente y la cantidad. A que producto pertenece
        # la receta lo completa la vista, segun cual haya elegido el usuario
        # en la pantalla.
        fields = ['ingrediente', 'cantidad_requerida']

        widgets = {
            'ingrediente': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_requerida': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
        }

    def clean_cantidad_requerida(self):
        cantidad = self.cleaned_data.get('cantidad_requerida')

        if cantidad <= 0:
            raise forms.ValidationError('La cantidad tiene que ser mayor a 0')

        return cantidad
