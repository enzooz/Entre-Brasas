"""URLs del app "reports", colgadas del prefijo /reportes/. Una sola pantalla."""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.sales_reports, name='sales_reports'),
]
