"""
Vistas de la app Menu: el alta, la edicion y la baja de hamburguesas
y adicionales.

Las cuatro vistas de cada producto siempre hacen lo mismo:
    listar_X   -> mostrar la tabla
    crear_X    -> formulario vacio, guardar, volver a la tabla
    editar_X   -> formulario con los datos cargados, guardar, volver
    activar_X  -> activar o desactivar (nunca se borra)

crear y editar usan la MISMA pantalla HTML. La variable "modo" que les
pasamos es la que hace que el titulo diga "Nueva" o "Editar".
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Prefetch

from .models import Hamburguesa, Adicional
from .forms import HamburguesaForm, AdicionalForm


def listar_hamburguesas(request):
    """Muestra solo el menú activo, sin borrar productos del historial."""
    return render(request, 'menu/listar_hamburguesas.html', {
        'hamburguesas': Hamburguesa.objects.filter(activa=True)
    })


def crear_hamburguesa(request):
    """Carga una hamburguesa nueva."""
    if request.method == 'POST':
        # Le pasamos al formulario lo que escribio el usuario.
        form = HamburguesaForm(request.POST)

        # is_valid() dispara todas las revisiones, incluida clean_precio().
        if form.is_valid():
            form.save()
            messages.success(request, 'Hamburguesa creada correctamente')
            return redirect('menu:listar_hamburguesas')
        # Si el formulario tenia errores no entramos al if, y se cae hasta
        # el render de abajo, que muestra el mismo formulario con los errores.
    else:
        form = HamburguesaForm()  # formulario vacio

    return render(request, 'menu/formulario_hamburguesa.html', {
        'form': form,
        'modo': 'crear',
    })


def editar_hamburguesa(request, hamburguesa_id):
    """
    Modifica una hamburguesa que ya existe.

    La unica diferencia con crear_hamburguesa es el instance=hamburguesa:
    le avisa al formulario sobre que objeto trabajar. Sin eso, al guardar
    crearia una hamburguesa nueva en vez de modificar la que elegimos.
    """
    hamburguesa = get_object_or_404(Hamburguesa, pk=hamburguesa_id)

    if request.method == 'POST':
        form = HamburguesaForm(request.POST, instance=hamburguesa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hamburguesa modificada correctamente')
            return redirect('menu:listar_hamburguesas')
    else:
        # Sin request.POST, el formulario aparece con los datos actuales cargados.
        form = HamburguesaForm(instance=hamburguesa)

    return render(request, 'menu/formulario_hamburguesa.html', {
        'form': form,
        'modo': 'editar',
        'hamburguesa': hamburguesa,
    })


def activar_hamburguesa(request, hamburguesa_id):
    """
    Saca una hamburguesa del menu o la vuelve a poner.

    Nunca se borra: si borraramos la hamburguesa, los pedidos viejos que la
    incluyen se romperian.

    Antes de desactivarla revisamos que no tenga pedidos asociados, para no
    dejar pedidos historicos apuntando a un producto que ya no se ofrece.
    """
    hamburguesa = get_object_or_404(Hamburguesa, pk=hamburguesa_id)

    # exists() pregunta si hay al menos uno. Es mas rapido que traerlos todos.
    # items_pedido es el related_name que pusimos en ItemPedido.
    if hamburguesa.activa and hamburguesa.items_pedido.exists():
        messages.error(
            request,
            'No se puede desactivar una hamburguesa que ya tiene pedidos'
        )
        return redirect('menu:listar_hamburguesas')

    # "not" da vuelta el valor: si estaba activa la desactiva y al reves.
    hamburguesa.activa = not hamburguesa.activa
    hamburguesa.save()

    if hamburguesa.activa:
        messages.success(request, 'Hamburguesa activada')
    else:
        messages.success(request, 'Hamburguesa desactivada')

    return redirect('menu:listar_hamburguesas')


def listar_adicionales(request):
    """Muestra adicionales activos y sus hamburguesas disponibles."""
    return render(request, 'menu/listar_adicionales.html', {
        'adicionales': Adicional.objects.filter(activo=True).prefetch_related(
            Prefetch('hamburguesas', queryset=Hamburguesa.objects.filter(activa=True), to_attr='hamburguesas_activas')
        )
    })


def crear_adicional(request):
    """Carga un adicional nuevo. Funciona igual que crear_hamburguesa."""
    if request.method == 'POST':
        form = AdicionalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Adicional creado correctamente')
            return redirect('menu:listar_adicionales')
    else:
        form = AdicionalForm()

    return render(request, 'menu/formulario_adicional.html', {
        'form': form,
        'modo': 'crear',
    })


def editar_adicional(request, adicional_id):
    """Modifica un adicional. Funciona igual que editar_hamburguesa."""
    adicional = get_object_or_404(Adicional, pk=adicional_id)

    if request.method == 'POST':
        form = AdicionalForm(request.POST, instance=adicional)
        if form.is_valid():
            form.save()
            messages.success(request, 'Adicional modificado correctamente')
            return redirect('menu:listar_adicionales')
    else:
        form = AdicionalForm(instance=adicional)

    return render(request, 'menu/formulario_adicional.html', {
        'form': form,
        'modo': 'editar',
        'adicional': adicional,
    })


def activar_adicional(request, adicional_id):
    """
    Activa o desactiva un adicional.

    Igual que con las hamburguesas, revisamos que no tenga pedidos antes
    de darlo de baja.
    """
    adicional = get_object_or_404(Adicional, pk=adicional_id)

    if adicional.activo and adicional.items_pedido.exists():
        messages.error(
            request,
            'No se puede desactivar un adicional que ya tiene pedidos'
        )
        return redirect('menu:listar_adicionales')

    adicional.activo = not adicional.activo
    adicional.save()

    if adicional.activo:
        messages.success(request, 'Adicional activado')
    else:
        messages.success(request, 'Adicional desactivado')

    return redirect('menu:listar_adicionales')
