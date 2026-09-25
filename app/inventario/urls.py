"""
Direcciones de la app Inventario. Cuelgan de /inventario/
"""
from django.urls import path

from . import views

app_name = 'inventario'

urlpatterns = [
    # Direccion vacia = /inventario/ a secas.
    path('', views.ver_inventario, name='ver_inventario'),
    path('movimiento/', views.registrar_movimiento, name='registrar_movimiento'),

    path('ingredientes/', views.listar_ingredientes, name='listar_ingredientes'),
    path('ingredientes/nuevo/', views.crear_ingrediente, name='crear_ingrediente'),
    path('ingredientes/<int:ingrediente_id>/editar/', views.editar_ingrediente, name='editar_ingrediente'),
    path('ingredientes/<int:ingrediente_id>/activar/', views.activar_ingrediente, name='activar_ingrediente'),

    path('recetas/', views.ver_recetas, name='ver_recetas'),
    path('recetas/agregar/', views.agregar_a_receta, name='agregar_a_receta'),
    path('recetas/<int:receta_id>/borrar/', views.borrar_de_receta, name='borrar_de_receta'),
]
