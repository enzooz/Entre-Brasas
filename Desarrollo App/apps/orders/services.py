"""
Capa de servicios del app "orders".

Acá vive la LÓGICA DE NEGOCIO: los cálculos y las reglas del sistema.
Las vistas (views.py) solo se ocupan de recibir el request y responder;
cuando hay que "pensar" algo, llaman a una función de este archivo.

Separar esto tiene dos ventajas: las vistas quedan cortas y legibles,
y estas funciones se pueden testear sin levantar un servidor web.
"""

from apps.config.models import SystemConfig
from apps.inventory.models import Recipe, InventoryMovement
from django.db import transaction


def calcular_envio(post_data, retiro_local):
    """
    Calcula cuánto se le cobra al cliente por el envío.

    La regla es:
      1. Si el cliente retira en el local -> no paga envío.
      2. Si vive más cerca que la distancia mínima -> tampoco paga (es "a la vuelta").
      3. Si no, paga distancia x tarifa_por_km, pero nunca menos que el costo mínimo.

    Los valores de tarifa, distancia mínima y costo mínimo salen de SystemConfig,
    o sea que el dueño del local los puede cambiar desde la pantalla de configuración
    sin tocar el código.
    """
    if retiro_local:
        return 0

    # El "or 0" cubre el caso en que el campo llegue vacío (""), porque float("") explota.
    distancia = float(post_data.get('distancia_km', 0) or 0)
    config = SystemConfig.get_config()

    if distancia < config.distancia_minima:
        return 0

    costo = distancia * config.tarifa_km
    # max() aplica el piso: si el cálculo da menos que el mínimo, se cobra el mínimo.
    # OJO: esto devuelve un float, pero Order.costo_envio es un entero.
    # Al guardar, Django trunca los decimales (1732.5 se guarda como 1732).
    return max(costo, config.costo_minimo_envio)


def calcular_total(order):
    """
    Suma el total del pedido: productos + adicionales + envío.

    Importante: se llama DESPUÉS de crear los items, porque recorre
    order.items (los items ya tienen que existir en la base).

    Notar que el precio del adicional se multiplica por la cantidad del item:
    si pediste 2 hamburguesas con bacon, pagás 2 bacons.
    """
    total = 0
    for item in order.items.all():          # items.all() funciona por el related_name='items'
        total += item.precio_unitario * item.cantidad
        for addon in item.adicionales.all():  # idem, related_name='adicionales'
            total += addon.precio * item.cantidad
    total += order.costo_envio
    return total


@transaction.atomic
def descontar_stock(order):
    """
    Descuenta del inventario los ingredientes que consume un pedido.

    Se dispara cuando el pedido pasa a "En preparación" (o sea, cuando
    la cocina realmente lo empieza a hacer y gasta los insumos).

    Funciona en DOS PASADAS a propósito:
      1ª pasada: verifica que alcance el stock de TODOS los ingredientes.
      2ª pasada: recién ahí descuenta.
    Si verificara y descontara en el mismo loop, un pedido podría quedar
    a medio descontar cuando falta el último ingrediente.

    El decorador @transaction.atomic envuelve todo en una transacción:
    si algo falla a la mitad, la base vuelve atrás como si nada hubiera pasado.

    Lanza ValueError si falta stock; la vista lo captura y lo muestra como mensaje.
    """

    # --- PASADA 1: solo verificar, no tocar nada ---
    for item in order.items.all():
        # La receta dice qué ingredientes lleva esta hamburguesa y cuánto de cada uno.
        # Se busca por tipo + id porque Recipe sirve tanto para hamburguesas como adicionales.
        recetas = Recipe.objects.filter(
            producto_tipo='hamburger',
            producto_id=item.hamburguesa.id
        )
        for receta in recetas:
            # Si la receta lleva 0.2 kg de carne y el cliente pidió 3, hacen falta 0.6 kg.
            cantidad_total = receta.cantidad_requerida * item.cantidad
            if receta.ingrediente.stock_actual < cantidad_total:
                raise ValueError(
                    f'Stock insuficiente: {receta.ingrediente.nombre}. '
                    f'Requerido: {cantidad_total} {receta.ingrediente.unidad}, '
                    f'Disponible: {receta.ingrediente.stock_actual} {receta.ingrediente.unidad}'
                )

    # --- PASADA 2: ahora sí, descontar ---
    # OJO: entre la pasada 1 y la 2 no hay bloqueo de filas (falta select_for_update).
    # Si dos pedidos se procesan al mismo tiempo, ambos pueden pasar la verificación
    # y descontar los dos, dejando el stock en negativo.
    for item in order.items.all():
        recetas = Recipe.objects.filter(
            producto_tipo='hamburger',
            producto_id=item.hamburguesa.id
        )
        for receta in recetas:
            cantidad_total = receta.cantidad_requerida * item.cantidad

            # Se registra el movimiento (para tener la traza de qué se consumió y por qué)...
            InventoryMovement.objects.create(
                ingrediente=receta.ingrediente,
                tipo='salida',
                cantidad=cantidad_total,
                motivo=f'Descuento automático - Pedido #{order.id}',
                pedido_relacionado=order  # así después se puede revertir si se cancela
            )
            # ...y además se actualiza el stock del ingrediente.
            # El stock se guarda duplicado (en Ingredient.stock_actual) en vez de
            # recalcularlo sumando movimientos, porque leerlo es mucho más rápido.
            receta.ingrediente.stock_actual -= cantidad_total
            receta.ingrediente.save()


@transaction.atomic
def devolver_stock(order):
    """
    Revierte el descuento de stock cuando se cancela un pedido.

    En vez de borrar los movimientos de salida (lo que rompería la auditoría),
    crea movimientos de ENTRADA equivalentes. Así el historial queda completo:
    se ve que salió y se ve que volvió.

    Se llama solo si el operador marca "devolver stock" al cancelar; si la comida
    ya se cocinó, el stock no vuelve y se registra como pérdida.
    """
    # Busca todas las salidas que generó este pedido.
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
