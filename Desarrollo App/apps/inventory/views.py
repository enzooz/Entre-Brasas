"""
Vistas del app "inventory" (inventario).

Tres bloques:
  1. Ver el stock y registrar movimientos (entradas/salidas de insumos).
  2. ABM de ingredientes (alta, edición, activar/desactivar).
  3. Armado de recetas (qué insumos lleva cada producto).

El ABM sigue un patrón idéntico en todo el proyecto (también en menu/views.py):
    POST con form válido -> guardar, mensaje y redirect
    cualquier otro caso  -> mostrar el formulario (vacío o con los errores)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from .models import Ingredient, InventoryMovement, Recipe
from .forms import IngredientForm, InventoryMovementForm, RecipeForm


def inventory_view(request):
    """Pantalla principal del inventario: el stock actual y qué falta reponer."""
    ingredients = Ingredient.objects.filter(activo=True)

    # models.F() referencia OTRA COLUMNA de la misma fila. Esto se traduce a
    # SQL como "WHERE stock_actual < stock_minimo", o sea que la comparación
    # la hace la base de datos.
    # La alternativa sería traer todo y filtrar en Python con la property
    # stock_bajo, pero eso obliga a recorrer todos los ingredientes acá.
    low_stock = ingredients.filter(stock_actual__lt=models.F('stock_minimo'))

    return render(request, 'inventory/inventory_view.html', {
        'ingredients': ingredients,
        'low_stock': low_stock
    })


def register_movement(request):
    """
    Registra una entrada o salida manual de stock (una compra, una merma, un ajuste).

    Es la única vista del inventario con lógica de negocio adentro: además de
    guardar el movimiento, actualiza el stock del ingrediente.
    """
    if request.method == 'POST':
        form = InventoryMovementForm(request.POST)
        if form.is_valid():
            # commit=False arma el objeto en memoria pero NO lo guarda todavía.
            # Hace falta porque primero hay que validar el stock y tocar el ingrediente.
            movement = form.save(commit=False)
            ingredient = movement.ingrediente

            # No se puede sacar más de lo que hay.
            if movement.tipo == 'salida':
                if movement.cantidad > ingredient.stock_actual:
                    messages.error(request, f'Stock insuficiente. Stock actual: {ingredient.stock_actual} {ingredient.unidad}')
                    return redirect('inventory:inventory_view')

            if movement.tipo == 'entrada':
                ingredient.stock_actual += movement.cantidad
                # Si la compra vino con precio, se actualiza el costo de referencia
                # del ingrediente. Se usa después para calcular el costo de los productos.
                if movement.precio_unitario > 0:
                    ingredient.precio_compra = movement.precio_unitario
            else:
                ingredient.stock_actual -= movement.cantidad

            # OJO: estos dos save() no están dentro de una transacción.
            # Si el segundo fallara, el stock quedaría modificado sin el movimiento
            # que lo justifique. Se arregla envolviendo con @transaction.atomic.
            ingredient.save()
            movement.save()

            tipo_movimiento = 'Entrada' if movement.tipo == 'entrada' else 'Salida'
            messages.success(request, f'{tipo_movimiento} registrada: {movement.cantidad} {ingredient.unidad} de {ingredient.nombre}')
            return redirect('inventory:inventory_view')
    else:
        form = InventoryMovementForm()

    # Se llega acá si es GET, o si el form tenía errores (en ese caso 'form'
    # ya viene con los mensajes de error adentro para que el template los muestre).
    return render(request, 'inventory/form_movement.html', {'form': form})


def manage_ingredients(request):
    """Listado completo de ingredientes, incluidos los desactivados."""
    ingredients = Ingredient.objects.all()
    return render(request, 'inventory/manage_ingredients.html', {'ingredients': ingredients})


def create_ingredient(request):
    """
    Alta de ingrediente.

    El 'mode' que se pasa al template hace que el HTML diga "Crear" en vez de
    "Editar": el mismo template sirve para las dos pantallas.
    """
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
    """
    Edición de un ingrediente existente.

    La diferencia con create_ingredient es el instance=ingredient: le dice al
    form "no crees uno nuevo, modificá este". Sin eso, guardaría un duplicado.
    """
    ingredient = get_object_or_404(Ingredient, pk=pk)
    if request.method == 'POST':
        form = IngredientForm(request.POST, instance=ingredient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ingrediente actualizado exitosamente')
            return redirect('inventory:manage_ingredients')
    else:
        # Sin request.POST, el form se muestra precargado con los datos actuales.
        form = IngredientForm(instance=ingredient)
    return render(request, 'inventory/form_ingredient.html', {'form': form, 'mode': 'edit'})


def toggle_ingredient(request, pk):
    """
    Activa o desactiva un ingrediente (baja lógica: no se borra nunca).

    La guarda del principio protege la integridad histórica: si el ingrediente
    ya tiene movimientos, desactivarlo dejaría reportes viejos sin sentido.
    """
    ingredient = get_object_or_404(Ingredient, pk=pk)
    if ingredient.movimientos.exists():  # exists() es más barato que contar o traer las filas
        messages.error(request, 'No se puede desactivar un ingrediente con movimientos registrados')
    else:
        ingredient.activo = not ingredient.activo  # invierte el booleano
        ingredient.save()
        estado = 'activado' if ingredient.activo else 'desactivado'
        messages.success(request, f'Ingrediente {estado} exitosamente')
    return redirect('inventory:manage_ingredients')


def recipes(request):
    """
    Pantalla de recetas: se elige un producto y se ve/edita qué insumos lleva.

    El producto elegido viene por querystring: ?tipo=hamburger&producto=3
    """
    # Import adentro de la función para evitar un import circular entre
    # inventory y menu. Con el import arriba del archivo puede romper el arranque.
    from apps.menu.models import Hamburger, Addon

    hamburgers = Hamburger.objects.filter(activa=True)
    addons = Addon.objects.filter(activo=True)
    ingredients = Ingredient.objects.filter(activo=True)

    selected_product = request.GET.get('producto')
    selected_tipo = request.GET.get('tipo')
    recipe_items = []  # si no se eligió producto, la tabla sale vacía

    if selected_product and selected_tipo:
        recipe_items = Recipe.objects.filter(
            producto_tipo=selected_tipo,
            producto_id=selected_product
        # select_related trae el ingrediente en la MISMA consulta (con un JOIN),
        # en vez de una consulta extra por cada fila. Es el único lugar del
        # proyecto donde se usa, y es exactamente el caso en que corresponde.
        ).select_related('ingrediente')

    return render(request, 'inventory/recipes.html', {
        'hamburgers': hamburgers,
        'addons': addons,
        'ingredients': ingredients,
        'recipe_items': recipe_items,
        # Se devuelven para que el desplegable quede en el producto elegido.
        'selected_product': selected_product,
        'selected_tipo': selected_tipo,
    })


def add_recipe_item(request):
    """
    Agrega un ingrediente a la receta de un producto.

    producto_tipo y producto_id no están en RecipeForm (vienen de campos ocultos
    del HTML), así que se setean a mano con commit=False antes de guardar.
    """
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.producto_tipo = request.POST.get('producto_tipo')
            recipe.producto_id = request.POST.get('producto_id')
            recipe.save()
            messages.success(request, 'Ingrediente agregado a la receta')
            # OJO: la URL se arma a mano en vez de usar reverse(). Si cambia
            # el patrón en urls.py, este redirect queda roto en silencio.
            return redirect(f'/inventario/recetas/?tipo={recipe.producto_tipo}&producto={recipe.producto_id}')
    # Si el form era inválido, el error se pierde: vuelve a la pantalla sin avisar nada.
    return redirect('inventory:recipes')


def delete_recipe_item(request, pk):
    """
    Saca un ingrediente de una receta.

    Se guardan tipo e id ANTES de borrar, porque después del delete()
    el objeto ya no sirve para armar la URL de vuelta.
    """
    recipe = get_object_or_404(Recipe, pk=pk)
    tipo = recipe.producto_tipo
    producto_id = recipe.producto_id
    recipe.delete()
    messages.success(request, 'Ingrediente eliminado de la receta')
    return redirect(f'/inventario/recetas/?tipo={tipo}&producto={producto_id}')
