"""Direcciones de la app Config. Cuelgan de /configuracion/"""
from django.urls import path

from . import views

app_name = 'config'

urlpatterns = [
    path('', views.panel_config, name='panel_config'),
]
