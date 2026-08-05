from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('nuevo/', views.create_order, name='create_order'),
    path('cola/', views.order_queue, name='order_queue'),
    path('historial/', views.order_history, name='order_history'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('<int:order_id>/avanzar/', views.advance_order, name='advance_order'),
    path('<int:order_id>/cancelar/', views.cancel_order, name='cancel_order'),
]
