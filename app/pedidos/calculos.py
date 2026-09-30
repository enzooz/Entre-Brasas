"""
Calculos de la app Pedidos.

En este archivo estan LAS CUENTAS del sistema: cuanto sale el envio,
cuanto sale el pedido y como se descuenta el stock.

Las vistas (views.py) se ocupan de recibir lo que manda el navegador y de
responder una pantalla. Cuando hay que hacer una cuenta, llaman a una funcion
de aca. La ventaja es que cada archivo hace una sola cosa:
    views.py    -> las pantallas
    calculos.py -> las cuentas
"""
from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP

from config.models import Configuracion
from inventario.models import Receta, MovimientoInventario


def calcular_envio(distancia_km, retiro_local):
    """
    Calcula cuanto se le cobra al cliente por el envio.

    Las reglas son:
      1. Si el cliente retira en el local, no paga envio.
      2. Si vive mas cerca que la distancia minima, tampoco paga.
      3. Si no, paga el envio minimo MAS la tarifa por toda la distancia:
         envio minimo + distancia en km x 10 x tarifa por cada 100 metros.

    Los tres valores de configuracion (distancia minima, tarifa y costo minimo)
    los puede cambiar el duenio desde la pantalla de configuracion.
    """
    if retiro_local:
        return 0

    # El "or 0" cubre el caso en que el campo llegue vacio, porque
    # convertir un texto vacio a numero da error.
    distancia = Decimal(str(distancia_km or 0).replace(',', '.'))

    configuracion = Configuracion.get_config()

    if distancia < configuracion.distancia_minima:
        return 0

    # El minimo es un importe base, no un piso que reemplaza la tarifa.
    costo = (Decimal(configuracion.costo_minimo_envio)
             + distancia * Decimal('10') * configuracion.tarifa_100m)

    # Solo se redondea el importe a pesos, NUNCA la distancia. 5,4 km son
    # exactamente 54 tramos. HALF_UP coincide con Math.round del navegador.
    return int(Decimal(costo).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def calcular_total(pedido):
    """
    Suma el total del pedido: hamburguesas + adicionales + envio.

    Se llama DESPUES de crear los items, porque necesita recorrerlos.

    Ojo con los adicionales: se multiplican por la cantidad del item.
    Si el cliente pidio 2 hamburguesas con bacon, paga 2 bacon.
    """
    total = 0

    for item in pedido.items.all():
        total = total + (item.precio_unitario * item.cantidad)

        for adicional in item.adicionales.all():
            total = total + (adicional.precio * item.cantidad)

    total = total + pedido.costo_envio

    return total


def buscar_recetas_del_item(item):
    """
    Devuelve todas las lineas de receta que consume un item del pedido:
    las de la hamburguesa mas las de cada adicional que le agregaron.

    Se usa desde descontar_stock().
    """
    recetas = []

    # Las recetas de la hamburguesa.
    for receta in Receta.objects.filter(hamburguesa=item.hamburguesa):
        recetas.append(receta)

    # Las recetas de cada adicional que lleva este item.
    for adicional_del_item in item.adicionales.all():
        for receta in Receta.objects.filter(adicional=adicional_del_item.adicional):
            recetas.append(receta)

    return recetas


@transaction.atomic
def descontar_stock(pedido):
    """
    Descuenta del inventario los ingredientes que consume un pedido.

    Se hace cuando el pedido pasa a "En preparacion", que es cuando la cocina
    lo empieza a preparar de verdad y gasta los insumos.

    NUNCA frena el pedido por falta de stock. Si la hamburguesa se esta
    haciendo, los ingredientes estan en la cocina aunque el sistema no lo
    sepa (por ejemplo, porque todavia no se cargo el stock real). Frenar el
    pedido no ayuda a nadie; lo que sirve es avisar que los numeros del
    inventario no cierran. Por eso el stock puede quedar en negativo: es la
    senial de que hay que hacer un conteo (Registrar movimiento -> Conteo).

    El @transaction.atomic de arriba envuelve todo en una transaccion:
    si algo falla en el medio, la base de datos vuelve para atras y queda
    como si nunca hubiera pasado nada. No queremos descontar medio pedido.

    Devuelve la lista de ingredientes que RECIEN pasaron a negativo con este
    pedido, para que la vista pueda avisar. Los que ya estaban en negativo
    no se repiten: si no, mientras el local no cuente, cada pedido mostraria
    el mismo aviso largo. (Inventario igual los muestra en rojo.)
    Si no paso nada de eso, la lista viene vacia.
    """
    quedaron_en_negativo = []

    for item in pedido.items.all():
        for receta in buscar_recetas_del_item(item):
            # Si la receta lleva 0.20 kg y el cliente pidio 3, hacen falta 0.60 kg.
            cantidad_necesaria = receta.cantidad_requerida * item.cantidad

            # Se anota el movimiento, para saber despues que se consumio y por que.
            MovimientoInventario.objects.create(
                ingrediente=receta.ingrediente,
                tipo='salida',
                cantidad=cantidad_necesaria,
                motivo=f'Preparacion del pedido #{pedido.pk}',
                pedido_relacionado=pedido
            )

            # Y se baja el stock del ingrediente, aunque quede en negativo.
            ingrediente = receta.ingrediente
            habia = ingrediente.stock_actual
            ingrediente.stock_actual = ingrediente.stock_actual - cantidad_necesaria
            ingrediente.save()

            ya_anotado = any(i.pk == ingrediente.pk for i in quedaron_en_negativo)
            if ya_anotado:
                # El mismo ingrediente aparece dos veces (la Crispy y su
                # medallon extra): se actualiza para avisar con lo ultimo.
                quedaron_en_negativo = [i for i in quedaron_en_negativo if i.pk != ingrediente.pk]
                quedaron_en_negativo.append(ingrediente)
            elif habia >= 0 and ingrediente.stock_actual < 0:
                quedaron_en_negativo.append(ingrediente)

    return quedaron_en_negativo


@transaction.atomic
def devolver_stock(pedido):
    """
    Devuelve al inventario el stock que habia consumido un pedido cancelado.

    En vez de borrar los movimientos de salida (lo que nos dejaria sin
    historial), se crean movimientos de entrada por la misma cantidad.
    Asi queda registrado que salio y que despues volvio.

    Solo se llama si el operador marca "devolver stock" al cancelar. Si la
    comida ya estaba hecha, los insumos se perdieron y no vuelven.
    """
    salidas = MovimientoInventario.objects.filter(
        pedido_relacionado=pedido,
        tipo='salida'
    )

    for salida in salidas:
        MovimientoInventario.objects.create(
            ingrediente=salida.ingrediente,
            tipo='entrada',
            cantidad=salida.cantidad,
            motivo=f'Devolucion por cancelacion del pedido #{pedido.pk}',
            pedido_relacionado=pedido
        )

        ingrediente = salida.ingrediente
        ingrediente.stock_actual = ingrediente.stock_actual + salida.cantidad
        ingrediente.save()
