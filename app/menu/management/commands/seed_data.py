"""
Comando para cargar los datos iniciales del sistema.

Se corre asi:
    python manage.py seed_data

Esto es un "comando de Django". Para crear uno hay que respetar esta
estructura de carpetas exacta:
    <app>/management/commands/<nombre_del_comando>.py
Django las busca solo, y el nombre del archivo pasa a ser el nombre del
comando. Por eso estan los archivos __init__.py vacios: sin ellos Python
no reconoce las carpetas.

Sirve para dejar la base lista para usar (menu, insumos, recetas y
configuracion) sin tener que cargar todo a mano desde las pantallas.

Todo usa get_or_create, asi que se puede correr varias veces sin que se
dupliquen los datos: si el registro ya existe, lo reutiliza.
"""
from django.core.management.base import BaseCommand

from menu.models import Hamburguesa, Adicional
from inventario.models import Ingrediente, Receta
from config.models import Configuracion


class Command(BaseCommand):
    help = 'Carga los datos iniciales de Entre Brasas'

    def add_arguments(self, parser):
        """Opciones extra que acepta el comando."""
        # instalar.bat lo corre con esta opcion. Asi, si el cliente vuelve a
        # correr la instalacion para actualizar, no le reaparecen productos
        # que el haya renombrado o desactivado.
        parser.add_argument(
            '--si-esta-vacia',
            action='store_true',
            help='Solo carga los datos si todavia no hay hamburguesas cargadas',
        )

    def handle(self, *args, **options):
        """Django ejecuta este metodo cuando se corre el comando."""
        if options['si_esta_vacia'] and Hamburguesa.objects.exists():
            self.stdout.write('La base ya tiene datos: no se carga nada.')
            return

        # Usamos self.stdout.write en vez de print para que Django pueda
        # manejar la salida y los colores de la consola.
        self.stdout.write('Cargando datos iniciales...')

        hamburguesas = self.cargar_hamburguesas()
        ingredientes = self.cargar_ingredientes()
        self.cargar_adicionales(hamburguesas)
        self.cargar_recetas(hamburguesas, ingredientes)
        self.cargar_configuracion()

        # self.style.SUCCESS pinta el texto de verde en la terminal.
        self.stdout.write(self.style.SUCCESS('Listo: datos iniciales cargados'))

    def cargar_hamburguesas(self):
        """
        Carga el menu de hamburguesas.

        Cada linea de la lista es (nombre, descripcion, precio, incluye papas).
        Devuelve un diccionario {nombre: objeto} para poder usarlo despues
        al armar las recetas y los adicionales.
        """
        datos = [
            ('Clasica', 'Pan, carne, lechuga, tomate y cebolla', 2500, True),
            ('Especial', 'Doble carne, bacon, cheddar y cebolla caramelizada', 3200, False),
            ('Veggie', 'Medallon de verduras, palta y lechuga', 2800, True),
            ('Doble Bacon', 'Doble carne, doble bacon, cheddar y salsa BBQ', 3800, False),
            ('Pollo Crispy', 'Pechuga de pollo rebozada, lechuga y mayonesa', 2700, True),
            ('BBQ', 'Carne, bacon, cebolla crocante y salsa BBQ', 3100, False),
            ('Hawaiana', 'Carne, jamon, ananá y queso', 2900, True),
        ]

        hamburguesas = {}

        for nombre, descripcion, precio, papas in datos:
            # get_or_create busca por nombre. Si no lo encuentra, crea el
            # registro con los valores que estan en "defaults".
            # Devuelve dos cosas: el objeto y si lo tuvo que crear.
            hamburguesa, creada = Hamburguesa.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': descripcion,
                    'precio': precio,
                    'incluye_papas': papas,
                }
            )
            hamburguesas[nombre] = hamburguesa
            self.stdout.write(f'  Hamburguesa: {nombre}')

        return hamburguesas

    def cargar_ingredientes(self):
        """
        Carga los insumos de la cocina.

        Cada linea es (nombre, stock inicial, unidad, stock minimo, precio de compra).
        """
        datos = [
            ('Carne molida', 15, 'kg', 5, 1600),
            ('Pan de hamburguesa', 50, 'unidades', 10, 80),
            ('Lechuga', 2, 'kg', 1, 800),
            ('Tomate', 8, 'unidades', 5, 30),
            ('Cebolla', 6, 'unidades', 4, 20),
            ('Bacon', 3, 'kg', 1, 3200),
            ('Cheddar', 2, 'kg', 1, 2800),
            ('Palta', 5, 'unidades', 3, 200),
            ('Pechuga de pollo', 8, 'kg', 3, 2200),
            ('Mayonesa', 2, 'L', 1, 1200),
            ('Salsa BBQ', 1.5, 'L', 0.5, 1500),
            ('Cebolla crocante', 1, 'kg', 0.5, 2000),
            ('Jamon', 2, 'kg', 1, 1800),
            ('Anana', 4, 'unidades', 2, 150),
            ('Huevo', 30, 'unidades', 12, 25),
            ('Medallon de verduras', 10, 'unidades', 5, 350),
            ('Queso', 3, 'kg', 1.5, 2400),
        ]

        ingredientes = {}

        for nombre, stock, unidad, minimo, precio in datos:
            ingrediente, creado = Ingrediente.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'stock_actual': stock,
                    'unidad': unidad,
                    'stock_minimo': minimo,
                    'precio_compra': precio,
                }
            )
            ingredientes[nombre] = ingrediente
            self.stdout.write(f'  Ingrediente: {nombre}')

        return ingredientes

    def cargar_adicionales(self, hamburguesas):
        """
        Carga los adicionales y los asocia a las hamburguesas donde se ofrecen.

        Cada linea es (nombre, precio, lista de hamburguesas).
        """
        datos = [
            ('Bacon Extra', 500, ['Clasica', 'Especial', 'Doble Bacon', 'BBQ']),
            ('Guacamole', 400, ['Clasica', 'Veggie', 'Pollo Crispy']),
            ('Doble Carne', 800, ['Clasica', 'Veggie', 'Pollo Crispy', 'Hawaiana']),
            ('Cheddar Extra', 300, ['Clasica', 'Especial', 'Veggie', 'Doble Bacon',
                                    'Pollo Crispy', 'BBQ', 'Hawaiana']),
            ('Huevo Frito', 250, ['Clasica', 'Especial', 'Doble Bacon', 'BBQ']),
        ]

        for nombre, precio, nombres_hamburguesas in datos:
            adicional, creado = Adicional.objects.get_or_create(
                nombre=nombre,
                defaults={'precio': precio}
            )

            # .add() crea el vinculo en la relacion de muchos a muchos.
            for nombre_hamburguesa in nombres_hamburguesas:
                adicional.hamburguesas.add(hamburguesas[nombre_hamburguesa])

            self.stdout.write(f'  Adicional: {nombre}')

    def cargar_recetas(self, hamburguesas, ingredientes):
        """
        Carga la receta de cada hamburguesa.

        Las cantidades van en la unidad del ingrediente: 0.200 de carne son
        200 gramos porque la carne se mide en kilos, y 2 de tomate son
        2 unidades.

        Esto es lo que despues lee descontar_stock() en pedidos/calculos.py
        para saber cuanto bajar del inventario por cada hamburguesa vendida.
        """
        recetas = {
            'Clasica': [
                ('Carne molida', 0.200),
                ('Pan de hamburguesa', 1),
                ('Lechuga', 0.050),
                ('Tomate', 2),
                ('Cebolla', 1),
            ],
            'Especial': [
                ('Carne molida', 0.400),
                ('Pan de hamburguesa', 1),
                ('Bacon', 0.050),
                ('Cheddar', 0.050),
                ('Cebolla', 1),
            ],
            'Veggie': [
                ('Medallon de verduras', 2),
                ('Pan de hamburguesa', 1),
                ('Lechuga', 0.050),
                ('Palta', 1),
            ],
            'Doble Bacon': [
                ('Carne molida', 0.400),
                ('Pan de hamburguesa', 1),
                ('Bacon', 0.100),
                ('Cheddar', 0.080),
                ('Salsa BBQ', 0.030),
            ],
            'Pollo Crispy': [
                ('Pechuga de pollo', 0.200),
                ('Pan de hamburguesa', 1),
                ('Lechuga', 0.050),
                ('Mayonesa', 0.020),
            ],
            'BBQ': [
                ('Carne molida', 0.200),
                ('Pan de hamburguesa', 1),
                ('Bacon', 0.050),
                ('Cebolla crocante', 0.030),
                ('Salsa BBQ', 0.030),
            ],
            'Hawaiana': [
                ('Carne molida', 0.200),
                ('Pan de hamburguesa', 1),
                ('Jamon', 0.050),
                ('Anana', 2),
                ('Queso', 0.030),
            ],
        }

        for nombre_hamburguesa in recetas:
            hamburguesa = hamburguesas[nombre_hamburguesa]

            for nombre_ingrediente, cantidad in recetas[nombre_hamburguesa]:
                Receta.objects.get_or_create(
                    hamburguesa=hamburguesa,
                    ingrediente=ingredientes[nombre_ingrediente],
                    defaults={'cantidad_requerida': cantidad}
                )

            self.stdout.write(f'  Receta de: {nombre_hamburguesa}')

    def cargar_configuracion(self):
        """
        Crea la configuracion del sistema si todavia no existe.

        Siempre es la fila numero 1: hay una sola configuracion.
        """
        Configuracion.objects.get_or_create(
            pk=1,
            defaults={
                'tarifa_km': 500,
                'distancia_minima': 1,
                'costo_minimo_envio': 1000,
                'costo_hora_mano_obra': 2500,
            }
        )
        self.stdout.write('  Configuracion del sistema')
