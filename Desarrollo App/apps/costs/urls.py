from django.urls import path
from . import views

app_name = 'costs'

urlpatterns = [
    path('', views.costs_view, name='costs_view'),
]
