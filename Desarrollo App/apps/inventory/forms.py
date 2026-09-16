"""
Formularios del app "inventory".

Los tres se usan de verdad desde inventory/views.py, así que sus validaciones
sí se ejecutan. Es el archivo de forms más completo del proyecto.
"""

from django import forms
from .models import Ingredient, Recipe, InventoryMovement


class IngredientForm(forms.ModelForm):
    """Alta y edición de un insumo."""

    class Meta:
        model = Ingredient
        # Quedan afuera a propósito:
        #   precio_compra -> se actualiza solo al registrar una compra (ver register_movement)
        #   activo        -> se maneja con el botón toggle
        fields = ['nombre', 'stock_actual', 'unidad', 'stock_minimo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidad': forms.Select(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'nombre': {'unique': 'Ya existe un ingrediente con ese nombre'},
        }

    def clean_stock_minimo(self):
        """
        El stock mínimo tiene que ser positivo: si fuera 0 el aviso de
        "reponer" no se dispararía nunca y el ingrediente se acabaría sin avisar.
        """
        stock_minimo = self.cleaned_data.get('stock_minimo')
        if stock_minimo <= 0:
            raise forms.ValidationError('El stock mínimo debe ser mayor a 0')
        return stock_minimo


class InventoryMovementForm(forms.ModelForm):
    """Carga manual de una entrada o salida de stock."""

    class Meta:
        model = InventoryMovement
        # pedido_relacionado no está: solo lo completa el sistema cuando
        # el movimiento lo genera un pedido automáticamente.
        fields = ['ingrediente', 'tipo', 'cantidad', 'precio_unitario', 'motivo']
        widgets = {
            # El Select de 'ingrediente' se llena solo con todos los Ingredient
            # de la base: Django lo arma a partir de la ForeignKey.
            'ingrediente': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            # step='0.01' porque la cantidad es DecimalField con 2 decimales.
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '1', 'placeholder': 'Precio por unidad (opcional)'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_cantidad(self):
        """Un movimiento de 0 o negativo no tiene sentido: el signo lo define 'tipo'."""
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a 0')
        return cantidad

    def clean_motivo(self):
        """
        El motivo es obligatorio para poder auditar después por qué se movió el stock.

        El strip() saca los espacios de los costados, así "   " no pasa como
        motivo válido, y además guarda el texto limpio.
        """
        motivo = self.cleaned_data.get('motivo')
        if not motivo or not motivo.strip():
            raise forms.ValidationError('El motivo es obligatorio para trazabilidad')
        return motivo.strip()


class RecipeForm(forms.ModelForm):
    """
    Una línea de receta: qué ingrediente y cuánto.

    Notar que producto_tipo y producto_id NO están en fields: los completa la
    vista add_recipe_item() a partir del producto que el usuario tenía elegido
    en pantalla (llegan como campos ocultos del HTML).
    """

    class Meta:
        model = Recipe
        fields = ['ingrediente', 'cantidad_requerida']
        widgets = {
            'ingrediente': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_requerida': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
        }

    def clean_cantidad_requerida(self):
        cantidad = self.cleaned_data.get('cantidad_requerida')
        if cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a 0')
        return cantidad
