from django.core.management.base import BaseCommand
from apps.menu.models import Hamburger, Addon
from apps.inventory.models import Ingredient, Recipe
from apps.config.models import SystemConfig


class Command(BaseCommand):
    help = 'Seed initial data for Entre Brasas'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos iniciales...')

        # Hamburguesas
        hamburgers_data = [
            ('Clasica', 'Pan, carne, lechuga, tomate, cebolla', 2500, True),
            ('Especial', 'Doble carne, bacon, cheddar, cebolla caramelizada', 3200, False),
            ('Veggie', 'Medallon de verduras, palta, lechuga', 2800, True),
            ('Doble Bacon', 'Doble carne, doble bacon, cheddar, BBQ', 3800, False),
            ('Pollo Crispy', 'Pechuga de pollo empanizada, lechuga, mayonesa', 2700, True),
            ('BBQ', 'Carne, bacon, cebolla crispy, salsa BBQ', 3100, False),
            ('Hawaiana', 'Carne, jamon, pina, queso', 2900, True),
        ]

        hamburgers = {}
        for nombre, desc, precio, papas in hamburgers_data:
            h, _ = Hamburger.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': desc, 'precio_base': precio, 'incluye_papas': papas}
            )
            hamburgers[nombre] = h
            self.stdout.write(f'  Hamburguesa: {nombre}')

        # Ingredientes
        ingredients_data = [
            ('Carne molida', 15, 'kg', 5, 1600),
            ('Pan de hamburguesa', 50, 'unidades', 10, 80),
            ('Lechuga', 2, 'kg', 3, 800),
            ('Tomate', 8, 'unidades', 5, 30),
            ('Cebolla', 6, 'unidades', 4, 20),
            ('Bacon', 3, 'kg', 2, 3200),
            ('Cheddar', 2, 'kg', 1, 2800),
            ('Palta', 5, 'unidades', 3, 200),
            ('Pollo (pechuga)', 8, 'kg', 3, 2200),
            ('Mayonesa', 2, 'L', 1, 1200),
            ('Salsa BBQ', 1.5, 'L', 0.5, 1500),
            ('Cebolla crispy', 1, 'kg', 0.5, 2000),
            ('Jamon', 2, 'kg', 1, 1800),
            ('Pina', 4, 'unidades', 2, 150),
            ('Huevo', 30, 'unidades', 12, 25),
            ('Medallon de verduras', 10, 'unidades', 5, 350),
            ('Queso', 3, 'kg', 1.5, 2400),
        ]

        ingredients = {}
        for nombre, stock, unidad, minimo, precio in ingredients_data:
            i, _ = Ingredient.objects.get_or_create(
                nombre=nombre,
                defaults={'stock_actual': stock, 'unidad': unidad, 'stock_minimo': minimo, 'precio_compra': precio}
            )
            ingredients[nombre] = i
            self.stdout.write(f'  Ingrediente: {nombre}')

        # Adicionales
        addons_data = [
            ('Bacon Extra', 500, ['Clasica', 'Especial', 'Doble Bacon', 'BBQ']),
            ('Guacamole', 400, ['Clasica', 'Veggie', 'Pollo Crispy']),
            ('Doble Carne', 800, ['Clasica', 'Veggie', 'Pollo Crispy', 'Hawaiana']),
            ('Cheddar Extra', 300, ['Clasica', 'Especial', 'Veggie', 'Doble Bacon', 'Pollo Crispy', 'BBQ', 'Hawaiana']),
            ('Huevo Frito', 250, ['Clasica', 'Especial', 'Doble Bacon', 'BBQ']),
        ]

        for nombre, precio, hamb_names in addons_data:
            addon, _ = Addon.objects.get_or_create(
                nombre=nombre,
                defaults={'precio': precio}
            )
            for h_name in hamb_names:
                addon.productos.add(hamburgers[h_name])
            self.stdout.write(f'  Adicional: {nombre}')

        # Recetas - Clasica
        recetas_clasica = [
            ('Carne molida', 0.200),
            ('Pan de hamburguesa', 1),
            ('Lechuga', 0.050),
            ('Tomate', 2),
            ('Cebolla', 1),
        ]
        for ingrediente_nombre, cantidad in recetas_clasica:
            Recipe.objects.get_or_create(
                producto_tipo='hamburger',
                producto_id=hamburgers['Clasica'].id,
                ingrediente=ingredients[ingrediente_nombre],
                defaults={'cantidad_requerida': cantidad}
            )

        # Recetas - Especial
        recetas_especial = [
            ('Carne molida', 0.400),
            ('Pan de hamburguesa', 1),
            ('Bacon', 0.050),
            ('Cheddar', 0.050),
            ('Cebolla', 1),
        ]
        for ingrediente_nombre, cantidad in recetas_especial:
            Recipe.objects.get_or_create(
                producto_tipo='hamburger',
                producto_id=hamburgers['Especial'].id,
                ingrediente=ingredients[ingrediente_nombre],
                defaults={'cantidad_requerida': cantidad}
            )

        # Recetas - Veggie
        recetas_veggie = [
            ('Medallon de verduras', 2),
            ('Pan de hamburguesa', 1),
            ('Lechuga', 0.050),
            ('Palta', 1),
        ]
        for ingrediente_nombre, cantidad in recetas_veggie:
            Recipe.objects.get_or_create(
                producto_tipo='hamburger',
                producto_id=hamburgers['Veggie'].id,
                ingrediente=ingredients[ingrediente_nombre],
                defaults={'cantidad_requerida': cantidad}
            )

        # Recetas - Doble Bacon
        recetas_doble_bacon = [
            ('Carne molida', 0.400),
            ('Pan de hamburguesa', 1),
            ('Bacon', 0.100),
            ('Cheddar', 0.080),
            ('Salsa BBQ', 0.030),
        ]
        for ingrediente_nombre, cantidad in recetas_doble_bacon:
            Recipe.objects.get_or_create(
                producto_tipo='hamburger',
                producto_id=hamburgers['Doble Bacon'].id,
                ingrediente=ingredients[ingrediente_nombre],
                defaults={'cantidad_requerida': cantidad}
            )

        # Recetas - Pollo Crispy
        recetas_pollo = [
            ('Pollo (pechuga)', 0.200),
            ('Pan de hamburguesa', 1),
            ('Lechuga', 0.050),
            ('Mayonesa', 0.020),
        ]
        for ingrediente_nombre, cantidad in recetas_pollo:
            Recipe.objects.get_or_create(
                producto_tipo='hamburger',
                producto_id=hamburgers['Pollo Crispy'].id,
                ingrediente=ingredients[ingrediente_nombre],
                defaults={'cantidad_requerida': cantidad}
            )

        # Recetas - BBQ
        recetas_bbq = [
            ('Carne molida', 0.200),
            ('Pan de hamburguesa', 1),
            ('Bacon', 0.050),
            ('Cebolla crispy', 0.030),
            ('Salsa BBQ', 0.030),
        ]
        for ingrediente_nombre, cantidad in recetas_bbq:
            Recipe.objects.get_or_create(
                producto_tipo='hamburger',
                producto_id=hamburgers['BBQ'].id,
                ingrediente=ingredients[ingrediente_nombre],
                defaults={'cantidad_requerida': cantidad}
            )

        # Recetas - Hawaiana
        recetas_hawaiana = [
            ('Carne molida', 0.200),
            ('Pan de hamburguesa', 1),
            ('Jamon', 0.050),
            ('Pina', 2),
            ('Queso', 0.030),
        ]
        for ingrediente_nombre, cantidad in recetas_hawaiana:
            Recipe.objects.get_or_create(
                producto_tipo='hamburger',
                producto_id=hamburgers['Hawaiana'].id,
                ingrediente=ingredients[ingrediente_nombre],
                defaults={'cantidad_requerida': cantidad}
            )

        # Configuracion
        SystemConfig.objects.get_or_create(
            pk=1,
            defaults={
                'tarifa_km': 500,
                'distancia_minima': 1,
                'costo_minimo_envio': 1000,
                'costo_hora_mano_obra': 2500,
            }
        )

        self.stdout.write(self.style.SUCCESS('Datos iniciales creados exitosamente'))
