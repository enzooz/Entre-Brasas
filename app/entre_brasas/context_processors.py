"""Información de navegación compartida, sin modificar datos del negocio."""
from django.urls import reverse
from .servidor_local import disponible, estado


PANTALLAS = {
    'inicio': ('Inicio', 'Todo lo que necesitás para trabajar en el local, en un solo lugar.'),
    'apagar_sistema': ('El sistema', 'Control del servidor local de Entre Brasas.'),
    'crear_pedido': ('Pedidos', 'Cliente, hamburguesas, pago y ubicación: un paso a la vez, sin perder lo cargado.'),
    'cola_pedidos': ('Pedidos', 'Seguí cada pedido y avanzalo cuando la cocina o el reparto estén listos.'),
    'detalle_pedido': ('Pedidos', 'Compartí la comanda, revisá los datos y seguí el estado del pedido.'),
    'historial_pedidos': ('Pedidos', 'Consultá los pedidos entregados y cancelados. Buscá por cliente o fecha.'),
    'listar_hamburguesas': ('Menú y recetas', 'Administrá lo que vendés: descripción, precio y disponibilidad.'),
    'listar_adicionales': ('Menú y recetas', 'Definí los extras y en qué hamburguesas se pueden pedir.'),
    'crear_hamburguesa': ('Menú y recetas', 'Completá el producto para sumarlo al menú del local.'),
    'editar_hamburguesa': ('Menú y recetas', 'Actualizá la información y guardá los cambios del producto.'),
    'crear_adicional': ('Menú y recetas', 'Creá un extra y elegí los productos que lo ofrecen.'),
    'editar_adicional': ('Menú y recetas', 'Actualizá el precio y la disponibilidad de este extra.'),
    'ver_recetas': ('Menú y recetas', 'Indicá qué lleva cada producto para descontar stock y calcular sus costos.'),
    'ver_inventario': ('Stock', 'Revisá cuánto queda y registrá compras, pérdidas o conteos de la cocina.'),
    'listar_ingredientes': ('Stock', 'Administrá tus insumos, sus unidades y el mínimo que necesitás tener.'),
    'crear_ingrediente': ('Stock', 'Agregá un insumo con su unidad y el stock mínimo para recibir avisos.'),
    'editar_ingrediente': ('Stock', 'Actualizá los datos del insumo. Para ajustar cantidades, registrá un movimiento.'),
    'registrar_movimiento': ('Stock', 'Elegí el ingrediente y registrá una compra, una salida o lo que contaste.'),
    'reportes_ventas': ('El negocio', 'Conocé tus ventas y los productos más pedidos en el período que elijas.'),
    'ver_costos': ('El negocio', 'Compará el precio de venta con los ingredientes y la mano de obra.'),
    'panel_config': ('El negocio', 'Ajustá las tarifas de envío, la mano de obra y el WhatsApp de cocina.'),
}


def navegacion(request):
    match = request.resolver_match
    actual = match.url_name if match else ''
    grupo, descripcion = PANTALLAS.get(actual, ('Entre Brasas', ''))
    if actual in ('detalle_pedido', 'avanzar_pedido', 'cancelar_pedido'):
        activo = 'cola_pedidos'
    elif actual.endswith('hamburguesa'):
        activo = 'listar_hamburguesas'
    elif actual.endswith('adicional'):
        activo = 'listar_adicionales'
    elif actual.endswith('ingrediente'):
        activo = 'listar_ingredientes'
    elif actual == 'registrar_movimiento':
        activo = 'ver_inventario'
    else:
        activo = actual
    grupos = [
        ('El día a día', [
            ('inicio', 'Inicio', 'home', 'inicio'),
            ('pedidos:crear_pedido', 'Nuevo pedido', 'plus', 'crear_pedido'),
            ('pedidos:cola_pedidos', 'Pedidos en curso', 'ticket', 'cola_pedidos'),
            ('pedidos:historial_pedidos', 'Historial', 'clock', 'historial_pedidos'),
        ]),
        ('Menú y recetas', [
            ('menu:listar_hamburguesas', 'Hamburguesas', 'burger', 'listar_hamburguesas'),
            ('menu:listar_adicionales', 'Adicionales', 'layers', 'listar_adicionales'),
            ('inventario:ver_recetas', 'Recetas', 'book', 'ver_recetas'),
        ]),
        ('Stock', [
            ('inventario:ver_inventario', 'Inventario', 'box', 'ver_inventario'),
            ('inventario:listar_ingredientes', 'Ingredientes', 'leaf', 'listar_ingredientes'),
        ]),
        ('El negocio', [
            ('reportes:reportes_ventas', 'Ventas y reportes', 'chart', 'reportes_ventas'),
            ('costos:ver_costos', 'Costos y ganancias', 'wallet', 'ver_costos'),
            ('config:panel_config', 'Configuración', 'settings', 'panel_config'),
        ]),
    ]
    return {
        'nav_grupos': [
            {'nombre': nombre, 'links': [
                {'url': reverse(url), 'nombre': texto, 'icono': icono, 'activo': clave == activo}
                for url, texto, icono, clave in links
            ]}
            for nombre, links in grupos
        ],
        'page_group': grupo,
        'page_description': descripcion,
        'page_key': actual,
        'puede_apagar_sistema': disponible(),
        'estado_sistema': estado(),
    }
