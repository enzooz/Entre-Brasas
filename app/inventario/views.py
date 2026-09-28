"""
Vistas de la app Inventario.

Tiene tres partes:
  1. Ver el stock y registrar entradas, salidas y conteos de insumos.
  2. Alta, edicion y baja de ingredientes.
  3. Armado de las recetas (que insumos lleva cada producto).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.urls import reverse

from menu.models import Hamburguesa, Adicional

from .models import Ingrediente, MovimientoInventario, Receta, formatear_cantidad
from .forms import IngredienteForm, MovimientoForm, RecetaForm


def ver_inventario(request):
    """
    Pantalla principal del inventario: el stock de cada insumo y cuales
    hay que reponer.
    """
    ingredientes = Ingrediente.objects.filter(activo=True)

    # Armamos la lista de los que estan por debajo del minimo.
    # stock_bajo es la property que definimos en el modelo: compara el stock
    # actual contra el stock minimo de ese ingrediente.
    # Los que estan en 0 o en negativo van aparte: todavia no se cargo el
    # stock real, o se uso mas de lo cargado (los pedidos nunca se frenan
    # por stock). Para esos lo que hay que hacer es contar, no comprar.
    sin_contar = [ingrediente for ingrediente in ingredientes if ingrediente.stock_actual <= 0]

    faltantes = []
    for ingrediente in ingredientes:
        if ingrediente.stock_bajo and ingrediente not in sin_contar:
            faltantes.append(ingrediente)

    return render(request, 'inventario/ver_inventario.html', {
        'ingredientes': ingredientes,
        'faltantes': faltantes,
        'sin_contar': sin_contar,
    })


@transaction.atomic
def registrar_movimiento(request):
    """
    Registra un movimiento de stock hecho a mano: una compra (entrada), una
    perdida (salida) o un conteo.

    Es la unica vista del inventario que ademas de guardar hace una cuenta:
    actualiza el stock del ingrediente.

    Lleva @transaction.atomic porque toca dos tablas (el ingrediente y el
    movimiento). Si fallara la segunda, no queremos que quede modificada
    solo la primera.
    """
    if request.method == 'POST':
        form = MovimientoForm(request.POST)

        if form.is_valid():
            # commit=False arma el objeto en memoria pero todavia no lo guarda.
            # Lo necesitamos asi porque antes hay que revisar el stock.
            movimiento = form.save(commit=False)
            movimiento.tipo = form.cleaned_data['tipo']
            ingrediente = movimiento.ingrediente

            if movimiento.tipo == 'conteo':
                return registrar_conteo(request, movimiento, ingrediente)

            if movimiento.tipo == 'salida':
                # No se puede sacar mas de lo que hay.
                if movimiento.cantidad > ingrediente.stock_actual:
                    messages.error(
                        request,
                        f'No hay stock suficiente. Hay {ingrediente.stock_actual} '
                        f'{ingrediente.unidad} de {ingrediente.nombre}.'
                    )
                    return redirect('inventario:ver_inventario')

                ingrediente.stock_actual = ingrediente.stock_actual - movimiento.cantidad
            else:
                ingrediente.stock_actual = ingrediente.stock_actual + movimiento.cantidad

                # Si la compra vino con precio, actualizamos el costo de
                # referencia del ingrediente. Se usa para calcular cuanto
                # cuesta preparar cada hamburguesa.
                if movimiento.precio_unitario > 0:
                    ingrediente.precio_compra = movimiento.precio_unitario

            ingrediente.save()
            movimiento.save()

            messages.success(
                request,
                f'{movimiento.get_tipo_display()} registrada: {movimiento.cantidad} '
                f'{ingrediente.unidad} de {ingrediente.nombre}'
            )
            return redirect('inventario:ver_inventario')
    else:
        form = MovimientoForm()

    # Llegamos aca si es GET, o si el formulario tenia errores. En ese
    # segundo caso "form" ya viene con los errores adentro para mostrarlos.
    return render(request, 'inventario/formulario_movimiento.html', {
        'form': form,
        # Para mostrar la unidad (kg, L, etc.) al lado de la cantidad
        # cuando se elige el ingrediente.
        'ingredientes': Ingrediente.objects.all(),
    })


def registrar_conteo(request, movimiento, ingrediente):
    """
    Pone el stock de un ingrediente en lo que se conto de verdad.

    No es una vista: la llama registrar_movimiento() cuando el tipo es
    "conteo". En movimiento.cantidad viene lo que se conto.

    El conteo no se guarda como un tipo nuevo: se calcula la diferencia con
    lo que dice el sistema y se guarda como una entrada (si habia mas) o una
    salida (si habia menos). Asi queda en el historial cuanto se ajusto y
    por que. Ejemplo: el sistema dice -2 medallones, se cuentan 80 ->
    entrada de 82 con el motivo "Conteo: habia -2, se contaron 80".
    """
    contado = movimiento.cantidad
    diferencia = contado - ingrediente.stock_actual

    if diferencia == 0:
        messages.info(
            request,
            f'El stock de {ingrediente.nombre} ya era {formatear_cantidad(contado)} '
            f'{ingrediente.unidad}: no hubo que ajustar nada.'
        )
        return redirect('inventario:ver_inventario')

    motivo = (f'Conteo: habia {formatear_cantidad(ingrediente.stock_actual)}, '
              f'se contaron {formatear_cantidad(contado)}')
    if movimiento.motivo:
        motivo = f'{motivo} ({movimiento.motivo})'

    movimiento.tipo = 'entrada' if diferencia > 0 else 'salida'
    movimiento.cantidad = abs(diferencia)
    movimiento.motivo = motivo
    # En un conteo no se compro nada, asi que el precio no aplica.
    movimiento.precio_unitario = 0
    movimiento.save()

    ingrediente.stock_actual = contado
    ingrediente.save()

    messages.success(
        request,
        f'Conteo registrado: {ingrediente.nombre} queda en {formatear_cantidad(contado)} {ingrediente.unidad}.'
    )
    return redirect('inventario:ver_inventario')


def listar_ingredientes(request):
    """Muestra todos los ingredientes, activos y desactivados."""
    return render(request, 'inventario/listar_ingredientes.html', {
        'ingredientes': Ingrediente.objects.all()
    })


def crear_ingrediente(request):
    """Carga un ingrediente nuevo."""
    if request.method == 'POST':
        form = IngredienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ingrediente creado correctamente')
            return redirect('inventario:listar_ingredientes')
    else:
        form = IngredienteForm()

    return render(request, 'inventario/formulario_ingrediente.html', {
        'form': form,
        'modo': 'crear',
    })


def editar_ingrediente(request, ingrediente_id):
    """Modifica un ingrediente que ya existe."""
    ingrediente = get_object_or_404(Ingrediente, pk=ingrediente_id)

    if request.method == 'POST':
        form = IngredienteForm(request.POST, instance=ingrediente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ingrediente modificado correctamente')
            return redirect('inventario:listar_ingredientes')
    else:
        form = IngredienteForm(instance=ingrediente)

    return render(request, 'inventario/formulario_ingrediente.html', {
        'form': form,
        'modo': 'editar',
        'ingrediente': ingrediente,
    })


def activar_ingrediente(request, ingrediente_id):
    """
    Activa o desactiva un ingrediente.

    Si el ingrediente ya tiene movimientos registrados no se puede desactivar,
    porque dejaria sin sentido los movimientos historicos.
    """
    ingrediente = get_object_or_404(Ingrediente, pk=ingrediente_id)

    if ingrediente.activo and ingrediente.movimientos.exists():
        messages.error(
            request,
            'No se puede desactivar un ingrediente que ya tiene movimientos'
        )
        return redirect('inventario:listar_ingredientes')

    ingrediente.activo = not ingrediente.activo
    ingrediente.save()

    if ingrediente.activo:
        messages.success(request, 'Ingrediente activado')
    else:
        messages.success(request, 'Ingrediente desactivado')

    return redirect('inventario:listar_ingredientes')


def ver_recetas(request):
    """
    Pantalla de recetas: se elige un producto y se ve o se arma su receta.

    El producto elegido viene en la direccion, por ejemplo:
        /inventario/recetas/?tipo=hamburguesa&producto=3
    """
    # tipo nos dice si el producto es una hamburguesa o un adicional.
    tipo = request.GET.get('tipo', '')
    producto_id = request.GET.get('producto', '')

    producto = None
    lineas_receta = []

    if tipo == 'hamburguesa' and producto_id:
        producto = get_object_or_404(Hamburguesa, pk=producto_id)
        # recetas es el related_name que pusimos en el modelo Receta.
        lineas_receta = producto.recetas.all()

    elif tipo == 'adicional' and producto_id:
        producto = get_object_or_404(Adicional, pk=producto_id)
        lineas_receta = producto.recetas.all()

    return render(request, 'inventario/ver_recetas.html', {
        'hamburguesas': Hamburguesa.objects.filter(activa=True),
        'adicionales': Adicional.objects.filter(activo=True),
        'ingredientes': Ingrediente.objects.filter(activo=True),
        'producto': producto,
        'tipo': tipo,
        'producto_id': producto_id,
        'lineas_receta': lineas_receta,
        'form': RecetaForm(),
    })


def volver_a_recetas(tipo, producto_id):
    """
    Arma la direccion de la pantalla de recetas con el producto que se
    estaba mirando, para volver ahi despues de agregar o borrar una linea.

    reverse() busca la direccion a partir del nombre que le pusimos en
    urls.py. Asi, si manana cambia la direccion, esto sigue funcionando.
    """
    direccion = reverse('inventario:ver_recetas')
    return redirect(f'{direccion}?tipo={tipo}&producto={producto_id}')


def agregar_a_receta(request):
    """
    Agrega un ingrediente a la receta de un producto.

    El ingrediente y la cantidad los valida el formulario. A que producto
    pertenece la receta lo completamos aca, con lo que venia en la pantalla.
    """
    if request.method != 'POST':
        return redirect('inventario:ver_recetas')

    tipo = request.POST.get('tipo', '')
    producto_id = request.POST.get('producto_id', '')

    form = RecetaForm(request.POST)

    if not form.is_valid():
        messages.error(request, 'Revisa el ingrediente y la cantidad')
        return volver_a_recetas(tipo, producto_id)

    receta = form.save(commit=False)

    # Segun el tipo, completamos uno u otro campo. El que no corresponde
    # queda vacio.
    if tipo == 'hamburguesa':
        receta.hamburguesa = get_object_or_404(Hamburguesa, pk=producto_id)
    elif tipo == 'adicional':
        receta.adicional = get_object_or_404(Adicional, pk=producto_id)
    else:
        messages.error(request, 'Hay que elegir un producto primero')
        return redirect('inventario:ver_recetas')

    receta.save()
    messages.success(request, 'Ingrediente agregado a la receta')
    return volver_a_recetas(tipo, producto_id)


def borrar_de_receta(request, receta_id):
    """
    Saca un ingrediente de una receta.

    Guardamos a que producto pertenecia ANTES de borrar, porque despues
    el objeto ya no nos sirve para volver a la pantalla correcta.
    """
    receta = get_object_or_404(Receta, pk=receta_id)

    if receta.hamburguesa:
        tipo = 'hamburguesa'
        producto_id = receta.hamburguesa.pk
    else:
        tipo = 'adicional'
        producto_id = receta.adicional.pk

    receta.delete()
    messages.success(request, 'Ingrediente sacado de la receta')

    return volver_a_recetas(tipo, producto_id)
