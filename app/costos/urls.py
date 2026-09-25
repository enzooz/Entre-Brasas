"""Direcciones de la app Costos. Cuelgan de /costos/"""
from django.urls import path

from . import views

app_name = 'costos'

urlpatterns = [
    path('', views.ver_costos, name='ver_costos'),
]
