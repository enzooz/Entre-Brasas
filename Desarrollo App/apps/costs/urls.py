"""URLs del app "costs", colgadas del prefijo /costos/. Una sola pantalla."""

from django.urls import path
from . import views

app_name = 'costs'

urlpatterns = [
    path('', views.costs_view, name='costs_view'),
]
