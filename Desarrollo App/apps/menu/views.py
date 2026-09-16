"""
Vistas del app "menu": el ABM de hamburguesas y adicionales.

Este archivo es el ejemplo más claro del patrón que se repite en todo el
proyecto. Son cuatro vistas por entidad, siempre iguales:

    manage_X  -> listar
    create_X  -> alta      (form vacío  -> guardar -> redirect)
    edit_X    -> edición   (form con instance= -> guardar -> redirect)
    toggle_X  -> activar/desactivar (baja lógica, nunca se borra)

create y edit comparten el mismo template HTML; la variable 'mode' que se pasa
al contexto es la que hace que diga "Crear" o "Editar".
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Hamburger, Addon
from .forms import HamburgerForm, AddonForm


def manage_hamburgers(request):
    """Listado de hamburguesas. Trae todas, activas y desactivadas."""
    hamburgers = Hamburger.objects.all()
    return render(request, 'menu/manage_hamburgers.html', {'hamburgers': hamburgers})


def create_hamburger(request):
    """Alta de hamburguesa."""
    if request.method == 'POST':
        # Al form se le pasan los datos que mandó el usuario.
        form = HamburgerForm(request.POST)
        # is_valid() dispara todas las validaciones (incluido clean_precio_base
        # de forms.py) y llena form.cleaned_data si todo está bien.
        if form.is_valid():
            form.save()
            messages.success(request, 'Hamburguesa creada exitosamente')
            return redirect('menu:manage_hamburgers')
        # Si NO es válido, no se entra al if y se cae al render de abajo,
        # que muestra el mismo form con los errores adentro.
    else:
        form = HamburgerForm()  # form vacío para el GET
    return render(request, 'menu/form_hamburger.html', {'form': form, 'mode': 'create'})


def edit_hamburger(request, pk):
    """
    Edición de una hamburguesa existente.

    instance=hamburger es lo único que cambia respecto del alta: le dice al form
    sobre qué objeto trabajar. Sin eso, form.save() crearía una hamburguesa nueva.
    """
    hamburger = get_object_or_404(Hamburger, pk=pk)
    if request.method == 'POST':
        form = HamburgerForm(request.POST, instance=hamburger)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hamburguesa actualizada exitosamente')
            return redirect('menu:manage_hamburgers')
    else:
        form = HamburgerForm(instance=hamburger)  # precargado con los datos actuales
    return render(request, 'menu/form_hamburger.html', {'form': form, 'mode': 'edit'})


def toggle_hamburger(request, pk):
    """
    Saca o vuelve a poner una hamburguesa en el menú.

    No se borra nunca: si se borrara, los pedidos históricos que la incluyen
    se romperían (OrderItem.hamburguesa es CASCADE, se los llevaría puestos).

    orderitem_set es el nombre que Django arma solo cuando la ForeignKey NO
    define related_name: es "nombre_del_modelo_en_minúscula" + "_set".
    Acá pregunta "¿esta hamburguesa aparece en algún pedido?".
    """
    hamburger = get_object_or_404(Hamburger, pk=pk)
    if hamburger.orderitem_set.exists():
        messages.error(request, 'No se puede desactivar una hamburguesa con pedidos asociados')
    else:
        hamburger.activa = not hamburger.activa
        hamburger.save()
        estado = 'activada' if hamburger.activa else 'desactivada'
        messages.success(request, f'Hamburguesa {estado} exitosamente')
    return redirect('menu:manage_hamburgers')


def manage_addons(request):
    """Listado de adicionales."""
    addons = Addon.objects.all()
    return render(request, 'menu/manage_addons.html', {'addons': addons})


def create_addon(request):
    """Alta de adicional. Mismo patrón que create_hamburger."""
    if request.method == 'POST':
        form = AddonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Adicional creado exitosamente')
            return redirect('menu:manage_addons')
    else:
        form = AddonForm()
    return render(request, 'menu/form_addon.html', {'form': form, 'mode': 'create'})


def edit_addon(request, pk):
    """Edición de adicional. Mismo patrón que edit_hamburger."""
    addon = get_object_or_404(Addon, pk=pk)
    if request.method == 'POST':
        form = AddonForm(request.POST, instance=addon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Adicional actualizado exitosamente')
            return redirect('menu:manage_addons')
    else:
        form = AddonForm(instance=addon)
    return render(request, 'menu/form_addon.html', {'form': form, 'mode': 'edit'})


def toggle_addon(request, pk):
    """
    Activa o desactiva un adicional.

    OJO: a diferencia de toggle_hamburger, acá NO se verifica si el adicional
    ya fue usado en pedidos. La protección está en una entidad y falta en la otra.
    """
    addon = get_object_or_404(Addon, pk=pk)
    addon.activo = not addon.activo
    addon.save()
    estado = 'activado' if addon.activo else 'desactivado'
    messages.success(request, f'Adicional {estado} exitosamente')
    return redirect('menu:manage_addons')
