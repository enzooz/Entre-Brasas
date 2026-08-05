from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda r: redirect('orders:create_order')),
    path('pedidos/', include('apps.orders.urls')),
    path('menu/', include('apps.menu.urls')),
    path('inventario/', include('apps.inventory.urls')),
    path('reportes/', include('apps.reports.urls')),
    path('costos/', include('apps.costs.urls')),
    path('config/', include('apps.config.urls')),
]
