from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order, OrderItem, OrderItemAddon, OrderStatusHistory
from apps.menu.models import Hamburger, Addon
from apps.config.models import SystemConfig
from .services import calcular_envio, calcular_total, descontar_stock, devolver_stock


def create_order(request):
    if request.method == 'POST':
        retiro_local = request.POST.get('retiro_local') == 'on'

        order = Order.objects.create(
            cliente_nombre=request.POST['cliente_nombre'],
            cliente_telefono=request.POST['cliente_telefono'],
            cliente_direccion=request.POST['cliente_direccion'],
            observaciones=request.POST.get('observaciones', ''),
            metodo_pago=request.POST['metodo_pago'],
            distancia_km=request.POST.get('distancia_km', 0) or 0,
            retiro_local=retiro_local,
            costo_envio=calcular_envio(request.POST, retiro_local),
        )

        crear_items_pedido(order, request.POST)

        order.total = calcular_total(order)
        order.save()

        messages.success(request, f'Pedido #{order.pk} creado exitosamente')
        return redirect('orders:order_queue')
    else:
        hamburgers = Hamburger.objects.filter(activa=True)
        addons = Addon.objects.filter(activo=True)
        config = SystemConfig.get_config()

    return render(request, 'orders/create_order.html', {
        'hamburgers': hamburgers,
        'addons': addons,
        'config': config
    })


def order_queue(request):
    orders = Order.objects.exclude(estado__in=['entregado', 'cancelado'])
    search = request.GET.get('search', '')
    estado_filter = request.GET.get('estado', '')

    if search:
        orders = orders.filter(cliente_nombre__icontains=search)
    if estado_filter:
        orders = orders.filter(estado=estado_filter)

    return render(request, 'orders/order_queue.html', {
        'orders': orders,
        'search': search,
        'estado_filter': estado_filter,
    })


def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    # Calcular totales para el template
    total_productos = sum(item.subtotal for item in order.items.all())
    total_adicionales = sum(
        addon.precio * item.cantidad
        for item in order.items.all()
        for addon in item.adicionales.all()
    )
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'total_productos': total_productos,
        'total_adicionales': total_adicionales,
    })


def advance_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    ESTADOS_SIGUIENTES = {
        'pendiente': 'en_preparacion',
        'en_preparacion': 'en_camino',
        'en_camino': 'entregado',
    }

    nuevo_estado = ESTADOS_SIGUIENTES.get(order.estado)
    if not nuevo_estado:
        messages.error(request, 'No se puede avanzar el estado de este pedido')
        return redirect('orders:order_queue')

    if nuevo_estado == 'en_preparacion':
        try:
            descontar_stock(order)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('orders:order_queue')

    OrderStatusHistory.objects.create(
        pedido=order,
        estado_anterior=order.estado,
        estado_nuevo=nuevo_estado
    )
    order.estado = nuevo_estado
    order.save()

    messages.success(request, f'Pedido #{order.pk} avanzado a {order.get_estado_display()}')
    return redirect('orders:order_queue')


def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if order.estado in ['en_preparacion', 'en_camino']:
        devolver = request.POST.get('devolver_stock') == 'on'
        if devolver:
            devolver_stock(order)
            messages.success(request, f'Stock devuelto para el Pedido #{order.pk}')
        else:
            messages.warning(request, f'Stoque no devuelto - Pedido #{order.pk} registrado como pérdida')

    OrderStatusHistory.objects.create(
        pedido=order,
        estado_anterior=order.estado,
        estado_nuevo='cancelado',
        observacion=request.POST.get('motivo_cancelacion', '')
    )
    order.estado = 'cancelado'
    order.save()

    messages.success(request, f'Pedido #{order.pk} cancelado')
    return redirect('orders:order_queue')


def order_history(request):
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
        orders = orders.filter(fecha_creacion__date__gte=fecha_desde)
    if fecha_hasta:
        orders = orders.filter(fecha_creacion__date__lte=fecha_hasta)

    return render(request, 'orders/order_history.html', {
        'orders': orders,
        'search': search,
        'estado_filter': estado_filter,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    })


def crear_items_pedido(order, post_data):
    """Crea los items del pedido desde los datos del formulario."""
    hamburger_ids = post_data.getlist('hamburger_ids[]')
    quantities = post_data.getlist('quantities[]')

    for i, hamburger_id in enumerate(hamburger_ids):
        if not hamburger_id:
            continue

        hamburger = get_object_or_404(Hamburger, pk=hamburger_id)
        cantidad = int(quantities[i]) if i < len(quantities) else 1

        item = OrderItem.objects.create(
            pedido=order,
            hamburguesa=hamburger,
            cantidad=cantidad,
            precio_unitario=hamburger.precio_base
        )

        # Los adicionales se envían como nombres
        addon_key = f'addon_ids_hamburger_{hamburger_id}[]'
        addon_nombres = post_data.getlist(addon_key)
        for addon_nombre in addon_nombres:
            if addon_nombre:
                addon = Addon.objects.filter(nombre=addon_nombre).first()
                if addon:
                    OrderItemAddon.objects.create(
                        item=item,
                        adicional=addon,
                        precio=addon.precio
                    )
