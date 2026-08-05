from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_view, name='inventory_view'),
    path('movimiento/', views.register_movement, name='register_movement'),
    path('ingredientes/', views.manage_ingredients, name='manage_ingredients'),
    path('ingredientes/crear/', views.create_ingredient, name='create_ingredient'),
    path('ingredientes/<int:pk>/editar/', views.edit_ingredient, name='edit_ingredient'),
    path('ingredientes/<int:pk>/toggle/', views.toggle_ingredient, name='toggle_ingredient'),
    path('recetas/', views.recipes, name='recipes'),
    path('recetas/agregar/', views.add_recipe_item, name='add_recipe_item'),
    path('recetas/<int:pk>/eliminar/', views.delete_recipe_item, name='delete_recipe_item'),
]
