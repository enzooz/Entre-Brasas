from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Hamburger, Addon
from .forms import HamburgerForm, AddonForm


def manage_hamburgers(request):
    hamburgers = Hamburger.objects.all()
    return render(request, 'menu/manage_hamburgers.html', {'hamburgers': hamburgers})


def create_hamburger(request):
    if request.method == 'POST':
        form = HamburgerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hamburguesa creada exitosamente')
            return redirect('menu:manage_hamburgers')
    else:
        form = HamburgerForm()
    return render(request, 'menu/form_hamburger.html', {'form': form, 'mode': 'create'})


def edit_hamburger(request, pk):
    hamburger = get_object_or_404(Hamburger, pk=pk)
    if request.method == 'POST':
        form = HamburgerForm(request.POST, instance=hamburger)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hamburguesa actualizada exitosamente')
            return redirect('menu:manage_hamburgers')
    else:
        form = HamburgerForm(instance=hamburger)
    return render(request, 'menu/form_hamburger.html', {'form': form, 'mode': 'edit'})


def toggle_hamburger(request, pk):
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
    addons = Addon.objects.all()
    return render(request, 'menu/manage_addons.html', {'addons': addons})


def create_addon(request):
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
    addon = get_object_or_404(Addon, pk=pk)
    addon.activo = not addon.activo
    addon.save()
    estado = 'activado' if addon.activo else 'desactivado'
    messages.success(request, f'Adicional {estado} exitosamente')
    return redirect('menu:manage_addons')
