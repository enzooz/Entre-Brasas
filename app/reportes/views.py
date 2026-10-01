"""
Vistas de la app Reportes.

Calcula los numeros de venta a partir de los pedidos ENTREGADOS que hay en
la base de datos. Los pedidos cancelados no cuentan como venta.

Todas las cuentas se hacen recorriendo los pedidos con bucles comunes.
"""
from django.shortcuts import render

from pedidos.models import Pedido


def reportes_ventas(request):
    """
    Pantalla de reportes: cuanto se vendio, con que se pago y que se vendio mas.

    Se puede filtrar por rango de fechas con los campos de la pantalla.
    """
    pedidos = Pedido.objects.filter(estado='entregado')

    # Filtro opcional por fechas.
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')

    if fecha_desde:
        pedidos = pedidos.filter(fecha_creacion__date__gte=fecha_desde)

    if fecha_hasta:
        pedidos = pedidos.filter(fecha_creacion__date__lte=fecha_hasta)

    # --- Totales generales ---
    total_vendido = 0
    total_envios = 0
    cantidad_pedidos = 0

    for pedido in pedidos:
        total_vendido = total_vendido + pedido.total
        total_envios = total_envios + pedido.costo_envio
        cantidad_pedidos = cantidad_pedidos + 1

    # El ticket promedio es cuanto gasta un cliente por pedido.
    # Preguntamos si hubo pedidos para no dividir por cero.
    if cantidad_pedidos > 0:
        ticket_promedio = round(total_vendido / cantidad_pedidos)
    else:
        ticket_promedio = 0

    # --- Como pagaron los clientes ---
    # Empezamos los dos contadores en cero y vamos sumando.
    pagos_efectivo = 0
    pagos_transferencia = 0

    for pedido in pedidos:
        if pedido.metodo_pago == 'efectivo':
            pagos_efectivo = pagos_efectivo + 1
        else:
            pagos_transferencia = pagos_transferencia + 1

    # --- Que hamburguesas se vendieron mas ---
    # Usamos un diccionario donde la clave es el nombre de la hamburguesa
    # y el valor es cuantas se vendieron.
    ventas_por_hamburguesa = {}

    for pedido in pedidos:
        for item in pedido.items.all():
            nombre = item.hamburguesa.nombre

            # Si es la primera vez que vemos esta hamburguesa, arrancamos en 0.
            if nombre not in ventas_por_hamburguesa:
                ventas_por_hamburguesa[nombre] = 0

            ventas_por_hamburguesa[nombre] = ventas_por_hamburguesa[nombre] + item.cantidad

    # --- Que adicionales se pidieron mas ---
    ventas_por_adicional = {}

    for pedido in pedidos:
        for item in pedido.items.all():
            for adicional_del_item in item.adicionales.all():
                nombre = adicional_del_item.adicional.nombre

                if nombre not in ventas_por_adicional:
                    ventas_por_adicional[nombre] = 0

                ventas_por_adicional[nombre] = ventas_por_adicional[nombre] + item.cantidad

    return render(request, 'reportes/reportes_ventas.html', {
        'total_vendido': total_vendido,
        'total_envios': total_envios,
        'cantidad_pedidos': cantidad_pedidos,
        'ticket_promedio': ticket_promedio,
        'pagos_efectivo': pagos_efectivo,
        'pagos_transferencia': pagos_transferencia,
        # ordenar_por_cantidad deja primero lo que mas se vendio.
        'top_hamburguesas': ordenar_por_cantidad(ventas_por_hamburguesa),
        'top_adicionales': ordenar_por_cantidad(ventas_por_adicional),
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    })


def ordenar_por_cantidad(ventas):
    """
    Recibe un diccionario {nombre: cantidad} y devuelve una lista ordenada
    de mayor a menor, lista para mostrar en la pantalla.

    Devuelve una lista de diccionarios porque los templates de Django no
    pueden recorrer los pares de un diccionario comodamente.
    """
    lista = []

    for nombre in ventas:
        lista.append({'nombre': nombre, 'cantidad': ventas[nombre]})

    # sort() ordena la lista. Con "key" le decimos por cual valor de cada
    # fila tiene que comparar, y con reverse=True la deja de mayor a menor.
    lista.sort(key=cantidad_de_la_fila, reverse=True)

    return lista


def cantidad_de_la_fila(fila):
    """
    Devuelve la cantidad de una fila.

    La usa el sort() de arriba para saber por cual valor ordenar.
    """
    return fila['cantidad']
