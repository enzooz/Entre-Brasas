"""
Direcciones principales del proyecto.

Django recorre esta lista de arriba hacia abajo y usa la PRIMERA que coincida
con lo que pidio el navegador. include() le pasa el resto de la direccion al
archivo urls.py de esa app.

Ejemplo: el navegador pide /pedidos/5/avanzar/
    coincide con 'pedidos/' y le manda "5/avanzar/" a pedidos/urls.py
"""
from django.urls import path, include

from . import views

urlpatterns = [
    # La direccion raiz del sitio (entrar a "/" a secas).
    path('', views.inicio, name='inicio'),
    path('sistema/apagar/', views.apagar_sistema, name='apagar_sistema'),
    path('sistema/estado/', views.estado_sistema, name='estado_sistema'),

    path('pedidos/', include('pedidos.urls')),
    path('menu/', include('menu.urls')),
    path('inventario/', include('inventario.urls')),
    path('reportes/', include('reportes.urls')),
    path('costos/', include('costos.urls')),
    path('configuracion/', include('config.urls')),
]
