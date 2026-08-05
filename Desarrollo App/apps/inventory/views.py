from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from .models import Ingredient, InventoryMovement, Recipe
from .forms import IngredientForm, InventoryMovementForm, RecipeForm


def inventory_view(request):
    ingredients = Ingredient.objects.filter(activo=True)
    low_stock = ingredients.filter(stock_actual__lt=models.F('stock_minimo'))
    return render(request, 'inventory/inventory_view.html', {
        'ingredients': ingredients,
        'low_stock': low_stock
    })


def register_movement(request):
    if request.method == 'POST':
        form = InventoryMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            ingredient = movement.ingrediente

            if movement.tipo == 'salida':
                if movement.cantidad > ingredient.stock_actual:
                    messages.error(request, f'Stock insuficiente. Stock actual: {ingredient.stock_actual} {ingredient.unidad}')
                    return redirect('inventory:inventory_view')

            if movement.tipo == 'entrada':
                ingredient.stock_actual += movement.cantidad
                if movement.precio_unitario > 0:
                    ingredient.precio_compra = movement.precio_unitario
            else:
                ingredient.stock_actual -= movement.cantidad

            ingredient.save()
            movement.save()

            tipo_movimiento = 'Entrada' if movement.tipo == 'entrada' else 'Salida'
            messages.success(request, f'{tipo_movimiento} registrada: {movement.cantidad} {ingredient.unidad} de {ingredient.nombre}')
            return redirect('inventory:inventory_view')
    else:
        form = InventoryMovementForm()
    return render(request, 'inventory/form_movement.html', {'form': form})


def manage_ingredients(request):
    ingredients = Ingredient.objects.all()
    return render(request, 'inventory/manage_ingredients.html', {'ingredients': ingredients})


def create_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ingrediente creado exitosamente')
            return redirect('inventory:manage_ingredients')
    else:
        form = IngredientForm()
    return render(request, 'inventory/form_ingredient.html', {'form': form, 'mode': 'create'})


def edit_ingredient(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    if request.method == 'POST':
        form = IngredientForm(request.POST, instance=ingredient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ingrediente actualizado exitosamente')
            return redirect('inventory:manage_ingredients')
    else:
        form = IngredientForm(instance=ingredient)
    return render(request, 'inventory/form_ingredient.html', {'form': form, 'mode': 'edit'})


def toggle_ingredient(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    if ingredient.movimientos.exists():
        messages.error(request, 'No se puede desactivar un ingrediente con movimientos registrados')
    else:
        ingredient.activo = not ingredient.activo
        ingredient.save()
        estado = 'activado' if ingredient.activo else 'desactivado'
        messages.success(request, f'Ingrediente {estado} exitosamente')
    return redirect('inventory:manage_ingredients')


def recipes(request):
    from apps.menu.models import Hamburger, Addon
    hamburgers = Hamburger.objects.filter(activa=True)
    addons = Addon.objects.filter(activo=True)
    ingredients = Ingredient.objects.filter(activo=True)

    selected_product = request.GET.get('producto')
    selected_tipo = request.GET.get('tipo')
    recipe_items = []

    if selected_product and selected_tipo:
        recipe_items = Recipe.objects.filter(
            producto_tipo=selected_tipo,
            producto_id=selected_product
        ).select_related('ingrediente')

    return render(request, 'inventory/recipes.html', {
        'hamburgers': hamburgers,
        'addons': addons,
        'ingredients': ingredients,
        'recipe_items': recipe_items,
        'selected_product': selected_product,
        'selected_tipo': selected_tipo,
    })


def add_recipe_item(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.producto_tipo = request.POST.get('producto_tipo')
            recipe.producto_id = request.POST.get('producto_id')
            recipe.save()
            messages.success(request, 'Ingrediente agregado a la receta')
            return redirect(f'/inventario/recetas/?tipo={recipe.producto_tipo}&producto={recipe.producto_id}')
    return redirect('inventory:recipes')


def delete_recipe_item(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    tipo = recipe.producto_tipo
    producto_id = recipe.producto_id
    recipe.delete()
    messages.success(request, 'Ingrediente eliminado de la receta')
    return redirect(f'/inventario/recetas/?tipo={tipo}&producto={producto_id}')
