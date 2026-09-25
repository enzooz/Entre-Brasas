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

from config.models import Configuracion
from inventario.models import Receta, MovimientoInventario


def calcular_envio(distancia_km, retiro_local):
    """
    Calcula cuanto se le cobra al cliente por el envio.

    Las reglas son:
      1. Si el cliente retira en el local, no paga envio.
      2. Si vive mas cerca que la distancia minima, tampoco paga.
      3. Si no, paga distancia x tarifa por km.
      4. Pero nunca paga menos que el costo minimo de envio.

    Los tres valores de configuracion (distancia minima, tarifa y costo minimo)
    los puede cambiar el duenio desde la pantalla de configuracion.
    """
    if retiro_local:
        return 0

    # El "or 0" cubre el caso en que el campo llegue vacio, porque
    # convertir un texto vacio a numero da error.
    distancia = float(distancia_km or 0)

    configuracion = Configuracion.get_config()

    if distancia < float(configuracion.distancia_minima):
        return 0

    costo = distancia * configuracion.tarifa_km

    # Si la cuenta dio menos que el minimo, se cobra el minimo.
    if costo < configuracion.costo_minimo_envio:
        costo = configuracion.costo_minimo_envio

    # round() antes de devolver: el costo se guarda como numero entero de pesos,
    # asi que redondeamos nosotros en vez de dejar que se corten los decimales.
    return round(costo)


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

    El trabajo se hace en DOS VUELTAS a proposito:
      1ra vuelta: revisa que alcance el stock de TODOS los ingredientes.
      2da vuelta: recien ahi descuenta.
    Si revisara y descontara en la misma vuelta, un pedido podria quedar
    descontado a medias cuando falta el ultimo ingrediente.

    El @transaction.atomic de arriba envuelve todo en una transaccion:
    si algo falla en el medio, la base de datos vuelve para atras y queda
    como si nunca hubiera pasado nada. No queremos descontar medio pedido.

    Si falta stock levanta un ValueError, que la vista atrapa y muestra
    como mensaje de error en pantalla.
    """

    # --- Primera vuelta: solo revisar ---
    for item in pedido.items.all():
        for receta in buscar_recetas_del_item(item):
            # Si la receta lleva 0.20 kg y el cliente pidio 3, hacen falta 0.60 kg.
            cantidad_necesaria = receta.cantidad_requerida * item.cantidad

            if receta.ingrediente.stock_actual < cantidad_necesaria:
                raise ValueError(
                    f'Stock insuficiente de {receta.ingrediente.nombre}. '
                    f'Se necesitan {cantidad_necesaria} {receta.ingrediente.unidad} '
                    f'y hay {receta.ingrediente.stock_actual} {receta.ingrediente.unidad}.'
                )

    # --- Segunda vuelta: descontar ---
    for item in pedido.items.all():
        for receta in buscar_recetas_del_item(item):
            cantidad_necesaria = receta.cantidad_requerida * item.cantidad

            # Se anota el movimiento, para saber despues que se consumio y por que.
            MovimientoInventario.objects.create(
                ingrediente=receta.ingrediente,
                tipo='salida',
                cantidad=cantidad_necesaria,
                motivo=f'Preparacion del pedido #{pedido.pk}',
                pedido_relacionado=pedido
            )

            # Y se baja el stock del ingrediente.
            ingrediente = receta.ingrediente
            ingrediente.stock_actual = ingrediente.stock_actual - cantidad_necesaria
            ingrediente.save()


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
