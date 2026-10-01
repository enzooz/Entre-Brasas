"""
Direcciones de la app Pedidos. Cuelgan de /pedidos/

Cada path() tiene tres partes:
    path(como es la direccion, que vista la atiende, name=un apodo)

El apodo sirve para no escribir las direcciones a mano en las pantallas:
    {% url 'pedidos:detalle_pedido' 5 %}
Si manana cambiamos la direccion, las pantallas siguen funcionando.
"""
from django.urls import path

from . import views

# Este nombre es el que va adelante del apodo: 'pedidos:cola_pedidos'.
# Sirve para que no se mezclen dos apps que tengan una direccion con el mismo apodo.
app_name = 'pedidos'

urlpatterns = [
    path('nuevo/', views.crear_pedido, name='crear_pedido'),
    # Lo usa el boton "Completar desde el mensaje" de Nuevo pedido.
    path('nuevo/interpretar/', views.interpretar_mensaje_view, name='interpretar_mensaje'),
    path('cola/', views.cola_pedidos, name='cola_pedidos'),
    path('historial/', views.historial_pedidos, name='historial_pedidos'),

    # int:pedido_id agarra un numero de la direccion y se lo pasa a la vista.
    # Si entramos a /pedidos/5/ se llama a detalle_pedido(request, pedido_id=5)
    path('<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('<int:pedido_id>/avanzar/', views.avanzar_pedido, name='avanzar_pedido'),
    path('<int:pedido_id>/cancelar/', views.cancelar_pedido, name='cancelar_pedido'),
]
