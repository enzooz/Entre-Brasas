"""
Vistas de la app Pedidos.

Una vista es una funcion que recibe un request (lo que pide el navegador)
y devuelve una respuesta (una pantalla HTML o una redireccion).

El patron que se repite en casi todas es este:
    si el metodo es POST  -> el usuario mando el formulario: guardamos y redirigimos
    si no                 -> el usuario esta entrando: mostramos la pantalla

Redirigir despues de guardar es a proposito: evita que si el usuario aprieta
F5 se vuelva a mandar el mismo pedido dos veces.

Las cuentas no estan aca, estan en calculos.py.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from menu.models import Hamburguesa, Adicional
from config.models import Configuracion

from .models import Pedido, ItemPedido, AdicionalDeItem, HistorialEstado
from .calculos import calcular_envio, calcular_total, descontar_stock, devolver_stock


def crear_pedido(request):
    """
    Pantalla para cargar un pedido nuevo. Es la pantalla principal del sistema.
    """
    if request.method == 'POST':
        # El formulario manda "true" o "false" como texto, asi que lo
        # comparamos con el texto "true" para obtener un verdadero/falso.
        retiro_local = request.POST.get('retiro_local') == 'true'

        distancia_km = request.POST.get('distancia_km') or 0

        pedido = Pedido.objects.create(
            cliente_nombre=request.POST.get('cliente_nombre', ''),
            cliente_telefono=request.POST.get('cliente_telefono', ''),
            cliente_direccion=request.POST.get('cliente_direccion', ''),
            observaciones=request.POST.get('observaciones', ''),
            metodo_pago=request.POST.get('metodo_pago', 'efectivo'),
            distancia_km=distancia_km,
            retiro_local=retiro_local,
            costo_envio=calcular_envio(distancia_km, retiro_local),
        )

        # El pedido ya existe pero esta vacio: ahora le agregamos las hamburguesas.
        crear_items_del_pedido(pedido, request.POST)

        # El total se calcula recien ahora, porque necesita los items ya creados.
        pedido.total = calcular_total(pedido)
        pedido.save()

        messages.success(request, f'Pedido #{pedido.pk} creado correctamente')
        return redirect('pedidos:cola_pedidos')

    # Si es GET mostramos el formulario con los productos disponibles.
    # Solo los activos: los dados de baja no se ofrecen.
    return render(request, 'pedidos/crear_pedido.html', {
        'hamburguesas': Hamburguesa.objects.filter(activa=True),
        'adicionales': Adicional.objects.filter(activo=True),
        'configuracion': Configuracion.get_config(),
    })


def crear_items_del_pedido(pedido, datos):
    """
    Crea las lineas del pedido a partir de lo que mando el formulario.

    No es una vista: es una funcion de ayuda que usa crear_pedido() para
    no quedar demasiado larga.

    El formulario manda dos listas que van de a pares, porque el usuario
    puede cargar varias hamburguesas en un mismo pedido:

        hamburger_ids[] = ['1', '3', '1']
        quantities[]    = ['2', '1', '1']

    O sea: la primera hamburguesa de la lista va con la primera cantidad,
    la segunda con la segunda, y asi.
    """
    # getlist() trae TODOS los valores de un campo que se repite.
    # Si usaramos .get() nos traeria solo el ultimo.
    ids_hamburguesas = datos.getlist('hamburger_ids[]')
    cantidades = datos.getlist('quantities[]')

    # enumerate nos da la posicion (i) y el valor al mismo tiempo,
    # asi podemos ir buscando la cantidad que esta en la misma posicion.
    for i, id_hamburguesa in enumerate(ids_hamburguesas):
        # Si el usuario dejo una fila sin elegir hamburguesa, la salteamos.
        if not id_hamburguesa:
            continue

        hamburguesa = get_object_or_404(Hamburguesa, pk=id_hamburguesa)

        # Por las dudas de que las listas vengan desparejas.
        if i < len(cantidades):
            cantidad = int(cantidades[i])
        else:
            cantidad = 1

        item = ItemPedido.objects.create(
            pedido=pedido,
            hamburguesa=hamburguesa,
            cantidad=cantidad,
            precio_unitario=hamburguesa.precio  # se guarda el precio de hoy
        )

        # Los adicionales de cada hamburguesa vienen en un campo que lleva
        # el numero de la hamburguesa en el nombre. Por ejemplo, los
        # adicionales de la hamburguesa 3 vienen en "adicionales_3[]".
        nombre_del_campo = f'adicionales_{id_hamburguesa}[]'

        for id_adicional in datos.getlist(nombre_del_campo):
            if not id_adicional:
                continue

            adicional = get_object_or_404(Adicional, pk=id_adicional)

            AdicionalDeItem.objects.create(
                item=item,
                adicional=adicional,
                precio=adicional.precio  # tambien se congela el precio
            )


def cola_pedidos(request):
    """
    La cola de cocina: los pedidos que todavia estan en curso.

    exclude() es lo contrario de filter(): trae todo MENOS lo que le pasamos.
    """
    pedidos = Pedido.objects.exclude(estado__in=['entregado', 'cancelado'])

    # Filtros opcionales, vienen en la direccion: ?busqueda=juan&estado=pendiente
    busqueda = request.GET.get('busqueda', '')
    estado = request.GET.get('estado', '')

    # Cada filter() le agrega una condicion mas a la busqueda.
    if busqueda:
        # icontains quiere decir "que contenga", sin diferenciar mayusculas.
        pedidos = pedidos.filter(cliente_nombre__icontains=busqueda)

    if estado:
        pedidos = pedidos.filter(estado=estado)

    return render(request, 'pedidos/cola_pedidos.html', {
        'pedidos': pedidos,
        # Devolvemos los filtros para que los campos queden completados.
        'busqueda': busqueda,
        'estado': estado,
        'estados': Pedido.ESTADOS,
    })


def detalle_pedido(request, pedido_id):
    """
    La ficha de un pedido: que se pidio, cuanto sale y en que estado esta.

    pedido_id llega desde la direccion (ver urls.py).
    """
    # get_object_or_404: si el pedido no existe muestra una pagina de
    # "no encontrado" en vez de romperse.
    pedido = get_object_or_404(Pedido, pk=pedido_id)

    # Estas dos cuentas se hacen aca y no en la pantalla porque los
    # templates de Django no saben sumar ni multiplicar.
    total_hamburguesas = 0
    total_adicionales = 0

    for item in pedido.items.all():
        total_hamburguesas = total_hamburguesas + item.subtotal

        for adicional in item.adicionales.all():
            total_adicionales = total_adicionales + (adicional.precio * item.cantidad)

    return render(request, 'pedidos/detalle_pedido.html', {
        'pedido': pedido,
        'total_hamburguesas': total_hamburguesas,
        'total_adicionales': total_adicionales,
    })


def avanzar_pedido(request, pedido_id):
    """
    Pasa el pedido al siguiente estado.

    El recorrido es:
        pendiente -> en preparacion -> en camino -> entregado
    """
    pedido = get_object_or_404(Pedido, pk=pedido_id)

    # El recorrido de los estados esta en el modelo (Pedido.SIGUIENTE_ESTADO).
    nuevo_estado = pedido.siguiente_estado

    # None quiere decir que el pedido ya estaba entregado o cancelado.
    if not nuevo_estado:
        messages.error(request, 'Este pedido ya no se puede avanzar')
        return redirect('pedidos:cola_pedidos')

    # El stock se descuenta cuando el pedido entra en preparacion, no antes:
    # un pedido pendiente todavia no consumio nada.
    if nuevo_estado == 'en_preparacion':
        try:
            descontar_stock(pedido)
        except ValueError as error:
            # descontar_stock avisa asi cuando falta stock.
            # Mostramos el mensaje y el pedido no avanza.
            messages.error(request, str(error))
            return redirect('pedidos:cola_pedidos')

    # Guardamos el cambio en el historial ANTES de pisar el estado,
    # porque despues ya no vamos a saber cual era el anterior.
    HistorialEstado.objects.create(
        pedido=pedido,
        estado_anterior=pedido.estado,
        estado_nuevo=nuevo_estado
    )

    pedido.estado = nuevo_estado
    pedido.save()

    # get_estado_display() devuelve el texto lindo ("En preparacion")
    # en lugar del valor que se guarda ("en_preparacion").
    messages.success(request, f'Pedido #{pedido.pk} pasa a {pedido.get_estado_display()}')
    return redirect('pedidos:cola_pedidos')


def cancelar_pedido(request, pedido_id):
    """
    Cancela un pedido y, si corresponde, devuelve el stock al inventario.
    """
    pedido = get_object_or_404(Pedido, pk=pedido_id)

    # Un pedido ya cerrado no se puede volver a cancelar.
    if pedido.estado in ['entregado', 'cancelado']:
        messages.error(request, 'Este pedido ya esta cerrado y no se puede cancelar')
        return redirect('pedidos:cola_pedidos')

    # Solo tiene sentido devolver stock si el pedido llego a descontarlo,
    # o sea si estaba en preparacion o en camino. Un pedido pendiente
    # nunca toco el inventario.
    if pedido.estado in ['en_preparacion', 'en_camino']:
        if request.POST.get('devolver_stock') == 'si':
            devolver_stock(pedido)
            messages.success(request, f'Se devolvio el stock del pedido #{pedido.pk}')
        else:
            messages.warning(
                request,
                f'El pedido #{pedido.pk} se cancela sin devolver stock (se registra como perdida)'
            )

    HistorialEstado.objects.create(
        pedido=pedido,
        estado_anterior=pedido.estado,
        estado_nuevo='cancelado',
        observacion=request.POST.get('motivo', '')
    )

    pedido.estado = 'cancelado'
    pedido.save()

    messages.success(request, f'Pedido #{pedido.pk} cancelado')
    return redirect('pedidos:cola_pedidos')


def historial_pedidos(request):
    """
    Los pedidos que ya terminaron, entregados o cancelados.

    Es el espejo de cola_pedidos(): aquella trae los abiertos, esta los cerrados.
    Ademas permite filtrar por rango de fechas.
    """
    pedidos = Pedido.objects.filter(estado__in=['entregado', 'cancelado'])

    busqueda = request.GET.get('busqueda', '')
    estado = request.GET.get('estado', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')

    if busqueda:
        pedidos = pedidos.filter(cliente_nombre__icontains=busqueda)

    if estado:
        pedidos = pedidos.filter(estado=estado)

    if fecha_desde:
        # __date se queda solo con la fecha e ignora la hora.
        # __gte quiere decir "mayor o igual que".
        pedidos = pedidos.filter(fecha_creacion__date__gte=fecha_desde)

    if fecha_hasta:
        # __lte quiere decir "menor o igual que".
        pedidos = pedidos.filter(fecha_creacion__date__lte=fecha_hasta)

    return render(request, 'pedidos/historial_pedidos.html', {
        'pedidos': pedidos,
        'busqueda': busqueda,
        'estado': estado,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    })
