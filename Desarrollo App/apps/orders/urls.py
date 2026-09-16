"""
URLs del app "orders", colgadas del prefijo /pedidos/ (ver entre_brasas/urls.py).

Cada path() tiene tres partes:
    path(patrón, vista, name=apodo)

El "name" es clave: permite escribir en los templates
    {% url 'orders:order_detail' 5 %}
en vez de la URL a mano. Si mañana cambia el patrón, los templates siguen andando.

El prefijo 'orders:' del ejemplo sale de app_name, que sirve para que no choquen
dos apps que tengan una URL con el mismo nombre.
"""

from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('nuevo/', views.create_order, name='create_order'),
    path('cola/', views.order_queue, name='order_queue'),
    path('historial/', views.order_history, name='order_history'),

    # int:order_id captura un número de la URL y se lo pasa a la vista
    # como parámetro llamado order_id. /pedidos/5/ llama a order_detail(request, order_id=5).
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('<int:order_id>/avanzar/', views.advance_order, name='advance_order'),
    path('<int:order_id>/cancelar/', views.cancel_order, name='cancel_order'),
]
