from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('hamburguesas/', views.manage_hamburgers, name='manage_hamburgers'),
    path('hamburguesas/crear/', views.create_hamburger, name='create_hamburger'),
    path('hamburguesas/<int:pk>/editar/', views.edit_hamburger, name='edit_hamburger'),
    path('hamburguesas/<int:pk>/toggle/', views.toggle_hamburger, name='toggle_hamburger'),
    path('adicionales/', views.manage_addons, name='manage_addons'),
    path('adicionales/crear/', views.create_addon, name='create_addon'),
    path('adicionales/<int:pk>/editar/', views.edit_addon, name='edit_addon'),
    path('adicionales/<int:pk>/toggle/', views.toggle_addon, name='toggle_addon'),
]
