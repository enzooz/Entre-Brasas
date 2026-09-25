"""
Direcciones de la app Menu. Cuelgan de /menu/

Se repite el mismo juego de cuatro direcciones para hamburguesas y para
adicionales: listar, crear, editar y activar/desactivar.
"""
from django.urls import path

from . import views

app_name = 'menu'

urlpatterns = [
    path('hamburguesas/', views.listar_hamburguesas, name='listar_hamburguesas'),
    path('hamburguesas/nueva/', views.crear_hamburguesa, name='crear_hamburguesa'),
    path('hamburguesas/<int:hamburguesa_id>/editar/', views.editar_hamburguesa, name='editar_hamburguesa'),
    path('hamburguesas/<int:hamburguesa_id>/activar/', views.activar_hamburguesa, name='activar_hamburguesa'),

    path('adicionales/', views.listar_adicionales, name='listar_adicionales'),
    path('adicionales/nuevo/', views.crear_adicional, name='crear_adicional'),
    path('adicionales/<int:adicional_id>/editar/', views.editar_adicional, name='editar_adicional'),
    path('adicionales/<int:adicional_id>/activar/', views.activar_adicional, name='activar_adicional'),
]
