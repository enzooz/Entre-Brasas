from apps.config.models import SystemConfig
from apps.inventory.models import Recipe, InventoryMovement
from django.db import transaction


def calcular_envio(post_data, retiro_local):
    """Calcula el costo de envío según distancia y configuración."""
    if retiro_local:
        return 0

    distancia = float(post_data.get('distancia_km', 0) or 0)
    config = SystemConfig.get_config()

    if distancia < config.distancia_minima:
        return 0

    costo = distancia * config.tarifa_km
    return max(costo, config.costo_minimo_envio)


def calcular_total(order):
    """Calcula el total del pedido (productos + adicionales + envío)."""
    total = 0
    for item in order.items.all():
        total += item.precio_unitario * item.cantidad
        for addon in item.adicionales.all():
            total += addon.precio * item.cantidad
    total += order.costo_envio
    return total


@transaction.atomic
def descontar_stock(order):
    """
    Descuenta stock cuando un pedido pasa a "En preparación".
    Lanza ValueError si no hay stock suficiente.
    """
    for item in order.items.all():
        recetas = Recipe.objects.filter(
            producto_tipo='hamburger',
            producto_id=item.hamburguesa.id
        )
        for receta in recetas:
            cantidad_total = receta.cantidad_requerida * item.cantidad
            if receta.ingrediente.stock_actual < cantidad_total:
                raise ValueError(
                    f'Stock insuficiente: {receta.ingrediente.nombre}. '
                    f'Requerido: {cantidad_total} {receta.ingrediente.unidad}, '
                    f'Disponible: {receta.ingrediente.stock_actual} {receta.ingrediente.unidad}'
                )

    for item in order.items.all():
        recetas = Recipe.objects.filter(
            producto_tipo='hamburger',
            producto_id=item.hamburguesa.id
        )
        for receta in recetas:
            cantidad_total = receta.cantidad_requerida * item.cantidad
            InventoryMovement.objects.create(
                ingrediente=receta.ingrediente,
                tipo='salida',
                cantidad=cantidad_total,
                motivo=f'Descuento automático - Pedido #{order.id}',
                pedido_relacionado=order
            )
            receta.ingrediente.stock_actual -= cantidad_total
            receta.ingrediente.save()


@transaction.atomic
def devolver_stock(order):
    """Devuelve stock cuando se cancela un pedido."""
    movements = InventoryMovement.objects.filter(
        pedido_relacionado=order,
        tipo='salida'
    )
    for movement in movements:
        InventoryMovement.objects.create(
            ingrediente=movement.ingrediente,
            tipo='entrada',
            cantidad=movement.cantidad,
            motivo=f'Devolución por cancelación - Pedido #{order.id}',
            pedido_relacionado=order
        )
        movement.ingrediente.stock_actual += movement.cantidad
        movement.ingrediente.save()
