"""
La comanda: el mensaje que se le manda a la cocina por WhatsApp.

Imita el formato que el local ya usaba a mano, asi la cocina no tiene que
acostumbrarse a nada nuevo:

    #12 - Agostina
    1 La Pepi
    1 Crispy doble
       Nota: dip de alioli
    RETIRA

En los envios se agregan la direccion, el telefono, el pago y el total,
que le sirven al cadete.
"""

# Como se llama una hamburguesa segun cuantos medallones extra lleva.
NOMBRE_SEGUN_MEDALLONES = {
    1: 'doble',
    2: 'triple',
}


def formatear_precio(precio):
    """30000 -> "30.000", con punto de miles como se escribe aca."""
    return f'{precio:,}'.replace(',', '.')


def describir_item(item):
    """
    Arma la linea de una hamburguesa: "1 Crispy doble + Panceta".

    Los medallones extra no se listan como adicional: cambian el nombre
    ("doble", "triple"), que es como lo dicen en la cocina.
    """
    medallones_extra = 0
    otros_adicionales = []

    for adicional_del_item in item.adicionales.all():
        if adicional_del_item.adicional.es_medallon_extra:
            medallones_extra = medallones_extra + 1
        else:
            otros_adicionales.append(adicional_del_item.adicional.nombre)

    linea = f'{item.cantidad} {item.hamburguesa.nombre}'

    if medallones_extra in NOMBRE_SEGUN_MEDALLONES:
        linea = linea + ' ' + NOMBRE_SEGUN_MEDALLONES[medallones_extra]
    elif medallones_extra > 0:
        linea = linea + f' + {medallones_extra} medallones extra'

    for nombre in otros_adicionales:
        linea = linea + ' + ' + nombre

    return linea


def armar_comanda(pedido):
    """Devuelve el texto de la comanda del pedido, listo para copiar."""
    lineas = [f'#{pedido.pk} - {pedido.cliente_nombre}']

    for item in pedido.items.all():
        lineas.append(describir_item(item))

        if item.nota:
            lineas.append(f'   Nota: {item.nota}')

    if pedido.observaciones:
        lineas.append(f'({pedido.observaciones})')

    if pedido.retiro_local:
        lineas.append('RETIRA')
    else:
        lineas.append(f'ENVIO: {pedido.cliente_direccion}')

        if pedido.cliente_telefono:
            lineas.append(f'Tel: {pedido.cliente_telefono}')

        lineas.append(f'{pedido.get_metodo_pago_display()} - Total ${formatear_precio(pedido.total)}')

    # WhatsApp respeta los saltos de linea del texto.
    return '\n'.join(lineas)
