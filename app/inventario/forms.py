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
    # El tipo se escribe a mano (en vez de dejar que Django lo arme desde el
    # modelo) porque suma una opcion que no existe en la base: el CONTEO.
    # En un conteo se escribe cuanto hay de verdad, y la vista calcula la
    # diferencia y la guarda como una entrada o una salida comun. Asi la
    # tabla de movimientos sigue teniendo solo entradas y salidas.
    tipo = forms.ChoiceField(
        choices=MovimientoInventario.TIPOS + [('conteo', 'Conteo (conte lo que hay de verdad)')],
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = MovimientoInventario

        # pedido_relacionado no esta: ese campo lo completa el sistema solo
        # cuando el movimiento lo genera un pedido. "tipo" tampoco: lo
        # declaramos arriba y la vista lo pasa al movimiento.
        fields = ['ingrediente', 'cantidad', 'precio_unitario', 'motivo']

        widgets = {
            # Django arma la lista de ingredientes sola, a partir de la relacion.
            'ingrediente': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Solo para compras (opcional)',
            }),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # El orden en que se muestran los campos en la pantalla.
    field_order = ['ingrediente', 'tipo', 'cantidad', 'precio_unitario', 'motivo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # En el modelo estos dos campos no pueden quedar vacios, asi que
        # Django los pediria siempre. Pero el precio solo tiene sentido en
        # una compra, y en un conteo el motivo lo escribe el sistema. Si
        # hace falta, clean() pide el motivo segun el tipo.
        self.fields['precio_unitario'].required = False
        self.fields['motivo'].required = False

    def clean_precio_unitario(self):
        """Si no se escribio precio, queda en 0 (no se actualiza el precio de compra)."""
        return self.cleaned_data.get('precio_unitario') or 0

    def clean_motivo(self):
        """
        strip() saca los espacios de los costados, asi alguien no puede poner
        solo espacios para zafar. Ademas guarda el texto ya limpio.
        """
        return (self.cleaned_data.get('motivo') or '').strip()

    def clean(self):
        """
        Las reglas que dependen del tipo de movimiento:

        - Entrada o salida: la cantidad tiene que ser mayor a 0 (que sume o
          reste lo decide el tipo, no el signo) y el motivo es obligatorio,
          para poder revisar despues por que se movio el stock.
        - Conteo: la cantidad puede ser 0 (se conto y no queda nada) y el
          motivo es opcional, porque el sistema escribe uno solo.
        """
        datos = super().clean()
        tipo = datos.get('tipo')
        cantidad = datos.get('cantidad')

        if cantidad is not None:
            if tipo == 'conteo' and cantidad < 0:
                self.add_error('cantidad', 'La cantidad contada no puede ser negativa')
            elif tipo != 'conteo' and cantidad <= 0:
                self.add_error('cantidad', 'La cantidad tiene que ser mayor a 0')

        if tipo != 'conteo' and not datos.get('motivo'):
            self.add_error('motivo', 'Hay que escribir el motivo del movimiento')

        return datos


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
