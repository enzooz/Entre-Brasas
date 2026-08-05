from django import forms
from .models import Ingredient, Recipe, InventoryMovement


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
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
        stock_minimo = self.cleaned_data.get('stock_minimo')
        if stock_minimo <= 0:
            raise forms.ValidationError('El stock mínimo debe ser mayor a 0')
        return stock_minimo


class InventoryMovementForm(forms.ModelForm):
    class Meta:
        model = InventoryMovement
        fields = ['ingrediente', 'tipo', 'cantidad', 'precio_unitario', 'motivo']
        widgets = {
            'ingrediente': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '1', 'placeholder': 'Precio por unidad (opcional)'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a 0')
        return cantidad

    def clean_motivo(self):
        motivo = self.cleaned_data.get('motivo')
        if not motivo or not motivo.strip():
            raise forms.ValidationError('El motivo es obligatorio para trazabilidad')
        return motivo.strip()


class RecipeForm(forms.ModelForm):
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
