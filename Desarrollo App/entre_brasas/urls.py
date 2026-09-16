"""
Mapa principal de URLs del proyecto.

Django recorre esta lista de arriba hacia abajo y usa la PRIMERA que matchee
con la URL que pidió el navegador. Cada include() delega el resto de la ruta
al urls.py de esa app.

Ejemplo: el navegador pide /pedidos/5/avanzar/
  -> matchea 'pedidos/' y le pasa "5/avanzar/" a apps/orders/urls.py
"""

from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    # La raíz del sitio no tiene vista propia: redirige directo a "crear pedido",
    # que es la pantalla principal del sistema.
    # El lambda es una vista mínima escrita en una línea (r = request).
    path('', lambda r: redirect('orders:create_order')),

    # Cada app maneja su propio prefijo de URL.
    path('pedidos/', include('apps.orders.urls')),
    path('menu/', include('apps.menu.urls')),
    path('inventario/', include('apps.inventory.urls')),
    path('reportes/', include('apps.reports.urls')),
    path('costos/', include('apps.costs.urls')),
    path('config/', include('apps.config.urls')),
]
