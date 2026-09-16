"""
Vistas del app "orders" (pedidos).

Una vista es una función que recibe un request (lo que pidió el navegador)
y devuelve un response (HTML renderizado o un redirect).

Patrón que se repite en casi todas:
    if request.method == 'POST':   -> el usuario mandó el formulario: guardar y redirigir
    else:                          -> el usuario está entrando: mostrar el formulario

El redirect después de un POST es a propósito (patrón Post/Redirect/Get):
evita que al apretar F5 se vuelva a mandar el mismo pedido.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order, OrderItem, OrderItemAddon, OrderStatusHistory
from apps.menu.models import Hamburger, Addon
from apps.config.models import SystemConfig
from .services import calcular_envio, calcular_total, descontar_stock, devolver_stock


def create_order(request):
    """
    Pantalla de alta de pedido (la pantalla principal del sistema).

    GET  -> muestra el formulario con las hamburguesas y adicionales disponibles.
    POST -> crea el pedido, sus items y calcula el total.
    """
    if request.method == 'POST':
        # El checkbox de HTML manda 'on' cuando está tildado, y no manda nada cuando no.
        # Por eso se compara contra 'on' en vez de usar bool().
        retiro_local = request.POST.get('retiro_local') == 'on'

        # OJO: acá se leen los campos con corchetes (request.POST['...']).
        # Si el campo no viene, Python lanza MultiValueDictKeyError y el server responde 500.
        # Además no hay validación de los datos: un teléfono podría ser "asdasd".
        # Existe un OrderForm en forms.py que hace exactamente esto bien, pero no se usa.
        order = Order.objects.create(
            cliente_nombre=request.POST['cliente_nombre'],
            cliente_telefono=request.POST['cliente_telefono'],
            cliente_direccion=request.POST['cliente_direccion'],
            observaciones=request.POST.get('observaciones', ''),  # .get() sí tiene default
            metodo_pago=request.POST['metodo_pago'],
            distancia_km=request.POST.get('distancia_km', 0) or 0,
            retiro_local=retiro_local,
            costo_envio=calcular_envio(request.POST, retiro_local),
        )

        # El pedido ya existe pero está vacío; ahora se le cuelgan las hamburguesas.
        crear_items_pedido(order, request.POST)

        # El total se calcula recién ahora, porque necesita los items ya creados.
        order.total = calcular_total(order)
        order.save()

        # messages guarda el texto en la sesión; el template base.html lo muestra
        # en la pantalla siguiente (después del redirect).
        messages.success(request, f'Pedido #{order.pk} creado exitosamente')
        return redirect('orders:order_queue')
    else:
        # Solo se ofrecen los productos activos (los dados de baja no aparecen).
        hamburgers = Hamburger.objects.filter(activa=True)
        addons = Addon.objects.filter(activo=True)
        config = SystemConfig.get_config()  # el JS necesita las tarifas para estimar el envío en vivo

    return render(request, 'orders/create_order.html', {
        'hamburgers': hamburgers,
        'addons': addons,
        'config': config
    })


def order_queue(request):
    """
    La cola de cocina: los pedidos que todavía están en curso.

    exclude() es lo contrario de filter(): trae todo MENOS lo que ya terminó.
    """
    orders = Order.objects.exclude(estado__in=['entregado', 'cancelado'])

    # Filtros opcionales que vienen por querystring (?search=juan&estado=pendiente).
    search = request.GET.get('search', '')
    estado_filter = request.GET.get('estado', '')

    # Los filtros se van encadenando sobre el queryset. Django no ejecuta nada
    # contra la base hasta que el template recorre 'orders' (queryset perezoso),
    # así que esto termina siendo UNA sola consulta SQL.
    if search:
        # icontains = "contiene", sin distinguir mayúsculas de minúsculas.
        orders = orders.filter(cliente_nombre__icontains=search)
    if estado_filter:
        orders = orders.filter(estado=estado_filter)

    return render(request, 'orders/order_queue.html', {
        'orders': orders,
        # Se devuelven los filtros al template para que los inputs queden completados.
        'search': search,
        'estado_filter': estado_filter,
    })


def order_detail(request, order_id):
    """
    Ficha de un pedido: qué se pidió, cuánto sale y en qué estado está.

    order_id llega desde la URL (ver urls.py, la ruta con int:order_id).
    """
    # get_object_or_404: si no existe, responde 404 en vez de explotar.
    order = get_object_or_404(Order, pk=order_id)

    # Estos dos totales se calculan acá y no en el template porque
    # los templates de Django no saben hacer aritmética.
    total_productos = sum(item.subtotal for item in order.items.all())
    total_adicionales = sum(
        addon.precio * item.cantidad
        for item in order.items.all()
        for addon in item.adicionales.all()
    )
    # OJO: esto genera una consulta por cada item y por cada adicional (problema N+1).
    # Se arreglaría con .prefetch_related('items__adicionales') al traer el pedido.

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'total_productos': total_productos,
        'total_adicionales': total_adicionales,
    })


def advance_order(request, order_id):
    """
    Mueve el pedido al siguiente estado del flujo.

    pendiente -> en_preparacion -> en_camino -> entregado

    OJO: esta vista modifica datos pero acepta GET. El template la llama con
    un formulario POST, pero nada lo obliga: entrar a mano a la URL
    /pedidos/5/avanzar/ avanza el pedido y saltea la protección CSRF.
    Se arregla agregando el decorador @require_POST.
    """
    order = get_object_or_404(Order, pk=order_id)

    # El flujo como diccionario: la clave es el estado actual, el valor el siguiente.
    # Los estados finales (entregado, cancelado) no están, así que devuelven None.
    ESTADOS_SIGUIENTES = {
        'pendiente': 'en_preparacion',
        'en_preparacion': 'en_camino',
        'en_camino': 'entregado',
    }

    nuevo_estado = ESTADOS_SIGUIENTES.get(order.estado)
    if not nuevo_estado:
        # Llegó acá si el pedido ya estaba entregado o cancelado.
        messages.error(request, 'No se puede avanzar el estado de este pedido')
        return redirect('orders:order_queue')

    # El stock se descuenta en la transición a "en preparación", no antes:
    # un pedido pendiente todavía no consumió nada.
    if nuevo_estado == 'en_preparacion':
        try:
            descontar_stock(order)
        except ValueError as e:
            # descontar_stock lanza ValueError si falta stock. Se muestra el mensaje
            # y se corta: el pedido NO avanza.
            messages.error(request, str(e))
            return redirect('orders:order_queue')

    # Se registra el cambio en el historial ANTES de pisar order.estado,
    # porque después de la asignación ya se perdió el estado anterior.
    OrderStatusHistory.objects.create(
        pedido=order,
        estado_anterior=order.estado,
        estado_nuevo=nuevo_estado
    )
    order.estado = nuevo_estado
    order.save()

    # get_estado_display() devuelve el texto lindo ("En preparación") en vez del código.
    messages.success(request, f'Pedido #{order.pk} avanzado a {order.get_estado_display()}')
    return redirect('orders:order_queue')


def cancel_order(request, order_id):
    """
    Cancela un pedido, con la opción de devolver el stock al inventario.

    OJO: igual que advance_order, no exige POST ni verifica que el pedido
    no esté ya cancelado.
    """
    order = get_object_or_404(Order, pk=order_id)

    # Solo tiene sentido devolver stock si el pedido ya lo había descontado,
    # o sea si llegó a "en preparación" o más adelante. Un pedido pendiente
    # nunca tocó el inventario.
    if order.estado in ['en_preparacion', 'en_camino']:
        devolver = request.POST.get('devolver_stock') == 'on'
        if devolver:
            devolver_stock(order)
            messages.success(request, f'Stock devuelto para el Pedido #{order.pk}')
        else:
            # La comida ya estaba hecha: los insumos se perdieron y no vuelven al stock.
            messages.warning(request, f'Stoque no devuelto - Pedido #{order.pk} registrado como pérdida')

    OrderStatusHistory.objects.create(
        pedido=order,
        estado_anterior=order.estado,
        estado_nuevo='cancelado',
        observacion=request.POST.get('motivo_cancelacion', '')  # queda registrado el porqué
    )
    order.estado = 'cancelado'
    order.save()

    messages.success(request, f'Pedido #{order.pk} cancelado')
    return redirect('orders:order_queue')


def order_history(request):
    """
    Historial: los pedidos ya terminados (entregados o cancelados).

    Es el espejo de order_queue(): esta trae lo cerrado, aquella lo abierto.
    Agrega filtro por rango de fechas.
    """
    orders = Order.objects.filter(estado__in=['entregado', 'cancelado'])

    search = request.GET.get('search', '')
    estado_filter = request.GET.get('estado', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')

    if search:
        orders = orders.filter(cliente_nombre__icontains=search)
    if estado_filter:
        orders = orders.filter(estado=estado_filter)
    if fecha_desde:
        # __date extrae solo la fecha del DateTimeField (ignora la hora),
        # __gte es "mayor o igual". Juntos: "creado desde tal día inclusive".
        orders = orders.filter(fecha_creacion__date__gte=fecha_desde)
    if fecha_hasta:
        # __lte es "menor o igual": hasta tal día inclusive.
        orders = orders.filter(fecha_creacion__date__lte=fecha_hasta)

    # OJO: no hay paginación. Con el tiempo esto trae TODOS los pedidos históricos
    # en una sola página.
    return render(request, 'orders/order_history.html', {
        'orders': orders,
        'search': search,
        'estado_filter': estado_filter,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    })


def crear_items_pedido(order, post_data):
    """
    Crea los OrderItem y OrderItemAddon a partir de los datos del formulario.

    No es una vista (no recibe request ni devuelve response): es una función
    auxiliar que usa create_order() para no quedar gigante.

    El formulario manda listas paralelas, porque el usuario puede cargar
    varias hamburguesas de una:
        hamburger_ids[] = ['1', '3', '1']
        quantities[]    = ['2', '1', '1']
    O sea: la posición i de una lista se corresponde con la posición i de la otra.
    """
    # getlist() devuelve todos los valores de un campo repetido (en vez de solo el último).
    hamburger_ids = post_data.getlist('hamburger_ids[]')
    quantities = post_data.getlist('quantities[]')

    # enumerate da el índice (i) y el valor a la vez, para poder cruzar las dos listas.
    for i, hamburger_id in enumerate(hamburger_ids):
        if not hamburger_id:
            continue  # saltea filas vacías que el JS pueda haber dejado

        hamburger = get_object_or_404(Hamburger, pk=hamburger_id)
        # El "if i < len" protege por si las listas vinieran desparejas.
        cantidad = int(quantities[i]) if i < len(quantities) else 1

        item = OrderItem.objects.create(
            pedido=order,
            hamburguesa=hamburger,
            cantidad=cantidad,
            precio_unitario=hamburger.precio_base  # se congela el precio de hoy
        )

        # Los adicionales se envían como nombres
        # El formulario agrupa los adicionales por hamburguesa usando el id en el nombre
        # del campo: addon_ids_hamburger_3[] son los adicionales de la hamburguesa 3.
        addon_key = f'addon_ids_hamburger_{hamburger_id}[]'
        addon_nombres = post_data.getlist(addon_key)
        for addon_nombre in addon_nombres:
            if addon_nombre:
                # OJO: se busca el adicional por NOMBRE en vez de por id.
                # Si alguien renombra un adicional, los pedidos nuevos dejan de encontrarlo,
                # y el .first() hace que falle en silencio (devuelve None y el if lo descarta).
                addon = Addon.objects.filter(nombre=addon_nombre).first()
                if addon:
                    OrderItemAddon.objects.create(
                        item=item,
                        adicional=addon,
                        precio=addon.precio
                    )
