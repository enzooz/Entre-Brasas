"""
Vista general del proyecto.
"""
from django.shortcuts import redirect


def inicio(request):
    """
    Atiende la direccion raiz del sitio.

    No muestra nada propio: manda directo a la pantalla de crear pedido,
    que es la que mas se usa en el local.
    """
    return redirect('pedidos:crear_pedido')
