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
        self.cargar_adicionales(hamburguesas, ingredientes)
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

        Es el menu real del local, sacado de https://entrebrasas.onrender.com/
        (septiembre 2026).
        """
        datos = [
            ('Sagrada', 'Pan brioche, 3 medallones, cheddar y aderezo de la casa.', 16500, True),
            ('Full', 'Pan brioche, 2 medallones, cheddar, panceta, huevo, cebolla caramelizada y aderezo alioli.', 15500, True),
            ('La Pepi', 'Pan brioche, 2 medallones, cheddar, cebolla en brunoise, pepinillos y aderezo de la casa.', 14000, True),
            ('Crispy', 'Pan brioche, 1 medallón, cheddar, panceta, cebolla crispy y aderezo alioli.', 13500, True),
            ('Freskita', 'Pan brioche, 1 medallón, cheddar, lechuga, tomate, cebolla morada y aderezo de la casa.', 11500, True),
            ('Baconera', 'Pan brioche, 2 medallones, cheddar, panceta y aderezo de la casa.', 13500, True),
            ('Tradi', 'Pan brioche, 1 medallón, queso tybo, jamón, tomate, lechuga y mayonesa.', 11500, True),
            ('Cheese', 'Pan brioche, 1 medallón, cheddar y aderezo de la casa.', 10500, True),
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

        Cada linea es (nombre, unidad, stock minimo, precio de compra).

        Los insumos salen de las descripciones del menu.

        El stock arranca en 0 a proposito: no sabemos cuanto hay en la cocina
        y un numero inventado confunde. El sistema no frena pedidos por falta
        de stock (ver descontar_stock en pedidos/calculos.py), asi que el
        local puede trabajar desde el primer dia. El stock va quedando en
        negativo con lo que se usa, y cuando cuenten lo que hay lo cargan con
        Inventario > Registrar movimiento > Conteo.

        El precio de compra va en 0 porque no lo sabemos: hay que cargarlo
        desde Ingredientes para que la pantalla de Costos calcule bien.
        """
        datos = [
            ('Pan brioche', 'unidades', 20, 0),
            ('Medallón de carne', 'unidades', 40, 0),
            ('Cheddar (fetas)', 'unidades', 50, 0),
            ('Queso tybo (fetas)', 'unidades', 10, 0),
            ('Panceta', 'kg', 1, 0),
            ('Jamón', 'kg', 0.3, 0),
            ('Huevo', 'unidades', 12, 0),
            ('Lechuga', 'kg', 0.3, 0),
            ('Tomate', 'kg', 0.5, 0),
            ('Cebolla', 'kg', 0.3, 0),
            ('Cebolla morada', 'kg', 0.3, 0),
            ('Cebolla caramelizada', 'kg', 0.3, 0),
            ('Cebolla crispy', 'kg', 0.3, 0),
            ('Pepinillos', 'kg', 0.3, 0),
            ('Aderezo de la casa', 'L', 0.5, 0),
            ('Aderezo alioli', 'L', 0.3, 0),
            ('Mayonesa', 'L', 0.3, 0),
            ('Papas', 'kg', 5, 0),
        ]

        ingredientes = {}

        for nombre, unidad, minimo, precio in datos:
            ingrediente, creado = Ingrediente.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'stock_actual': 0,
                    'unidad': unidad,
                    'stock_minimo': minimo,
                    'precio_compra': precio,
                }
            )
            ingredientes[nombre] = ingrediente
            self.stdout.write(f'  Ingrediente: {nombre}')

        return ingredientes

    def cargar_adicionales(self, hamburguesas, ingredientes):
        """
        Carga los adicionales, con su receta, y los asocia a las hamburguesas.

        Cada linea es (nombre, precio, receta). En el menu dice "Suma a
        cualquier hamburguesa", asi que cada adicional se ofrece en todas.
        La receta es lo que descuenta del stock cada vez que se pide.
        """
        datos = [
            ('Medallón extra', 2500, [('Medallón de carne', 1), ('Cheddar (fetas)', 1)]),
            ('Cheddar extra', 1000, [('Cheddar (fetas)', 2)]),
            ('Panceta', 2000, [('Panceta', 0.04)]),
            ('Huevo', 1000, [('Huevo', 1)]),
            ('Papas fritas', 2000, [('Papas', 0.25)]),
        ]

        for nombre, precio, receta in datos:
            adicional, creado = Adicional.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'precio': precio,
                    # El medallon extra es el que hace "doble" a una hamburguesa.
                    'es_medallon_extra': nombre == 'Medallón extra',
                }
            )

            # .add() crea el vinculo en la relacion de muchos a muchos.
            for hamburguesa in hamburguesas.values():
                adicional.hamburguesas.add(hamburguesa)

            for nombre_ingrediente, cantidad in receta:
                Receta.objects.get_or_create(
                    adicional=adicional,
                    ingrediente=ingredientes[nombre_ingrediente],
                    defaults={'cantidad_requerida': cantidad}
                )

            self.stdout.write(f'  Adicional: {nombre}')

    def cargar_recetas(self, hamburguesas, ingredientes):
        """
        Carga la receta de cada hamburguesa.

        Las cantidades van en la unidad del ingrediente: 0.200 de carne son
        200 gramos porque la carne se mide en kilos, y 2 de tomate son
        2 unidades.

        Esto es lo que despues lee descontar_stock() en pedidos/calculos.py
        para saber cuanto bajar del inventario por cada hamburguesa vendida.

        El pan, los medallones y el queso salen del menu (una feta por
        medallon). El resto de las cantidades son estimaciones: hay que
        confirmarlas con el local y corregirlas desde la pantalla Recetas.
        Todas incluyen papas, por eso todas llevan una porcion.
        """
        recetas = {
            'Sagrada': [
                ('Pan brioche', 1),
                ('Medallón de carne', 3),
                ('Cheddar (fetas)', 3),
                ('Aderezo de la casa', 0.03),
                ('Papas', 0.25),
            ],
            'Full': [
                ('Pan brioche', 1),
                ('Medallón de carne', 2),
                ('Cheddar (fetas)', 2),
                ('Panceta', 0.04),
                ('Huevo', 1),
                ('Cebolla caramelizada', 0.04),
                ('Aderezo alioli', 0.03),
                ('Papas', 0.25),
            ],
            'La Pepi': [
                ('Pan brioche', 1),
                ('Medallón de carne', 2),
                ('Cheddar (fetas)', 2),
                ('Cebolla', 0.03),
                ('Pepinillos', 0.03),
                ('Aderezo de la casa', 0.03),
                ('Papas', 0.25),
            ],
            'Crispy': [
                ('Pan brioche', 1),
                ('Medallón de carne', 1),
                ('Cheddar (fetas)', 1),
                ('Panceta', 0.04),
                ('Cebolla crispy', 0.03),
                ('Aderezo alioli', 0.03),
                ('Papas', 0.25),
            ],
            'Freskita': [
                ('Pan brioche', 1),
                ('Medallón de carne', 1),
                ('Cheddar (fetas)', 1),
                ('Lechuga', 0.03),
                ('Tomate', 0.05),
                ('Cebolla morada', 0.03),
                ('Aderezo de la casa', 0.03),
                ('Papas', 0.25),
            ],
            'Baconera': [
                ('Pan brioche', 1),
                ('Medallón de carne', 2),
                ('Cheddar (fetas)', 2),
                ('Panceta', 0.06),
                ('Aderezo de la casa', 0.03),
                ('Papas', 0.25),
            ],
            'Tradi': [
                ('Pan brioche', 1),
                ('Medallón de carne', 1),
                ('Queso tybo (fetas)', 1),
                ('Jamón', 0.03),
                ('Tomate', 0.05),
                ('Lechuga', 0.03),
                ('Mayonesa', 0.02),
                ('Papas', 0.25),
            ],
            'Cheese': [
                ('Pan brioche', 1),
                ('Medallón de carne', 1),
                ('Cheddar (fetas)', 1),
                ('Aderezo de la casa', 0.03),
                ('Papas', 0.25),
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
