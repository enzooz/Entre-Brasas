"""Direcciones de la app Reportes. Cuelgan de /reportes/"""
from django.urls import path

from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.reportes_ventas, name='reportes_ventas'),
]
