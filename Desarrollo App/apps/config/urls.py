from django.urls import path
from . import views

app_name = 'config'

urlpatterns = [
    path('', views.admin_panel, name='admin_panel'),
]
