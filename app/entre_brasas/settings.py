"""
Configuracion del proyecto Entre Brasas.

Django lee este archivo al arrancar. Todo lo que este escrito en MAYUSCULAS
es una opcion que Django busca por nombre.
"""
import os
from pathlib import Path

# La carpeta donde esta el proyecto ("app").
# __file__ es este archivo, .resolve() lo convierte en ruta completa,
# y cada .parent sube una carpeta.
BASE_DIR = Path(__file__).resolve().parent.parent

# El sistema funciona de dos formas:
#
#   - Desarrollo (lo normal): lo que usamos nosotros con "runserver".
#   - Local del cliente: la instalacion en la compu del local. La activan
#     instalar.bat e iniciar.bat poniendo ENTRE_BRASAS_PRODUCCION=1.
#
# La diferencia principal es donde se guardan los datos. En la compu del
# cliente van a una carpeta aparte (fuera de la del programa), asi al
# instalar una version nueva se reemplaza el programa sin tocar los pedidos.
PRODUCCION = os.environ.get('ENTRE_BRASAS_PRODUCCION') == '1'

if PRODUCCION:
    # C:/Users/<usuario>/AppData/Local/EntreBrasas
    DATOS_DIR = Path(os.environ['LOCALAPPDATA']) / 'EntreBrasas'
    # Las copias de seguridad van a Documentos, donde el cliente las encuentra.
    COPIAS_DIR = Path.home() / 'Documents' / 'Entre Brasas - Copias de seguridad'
else:
    DATOS_DIR = BASE_DIR
    COPIAS_DIR = BASE_DIR / 'copias_de_seguridad'

DATOS_DIR.mkdir(parents=True, exist_ok=True)

# Clave que Django usa para firmar las cookies y los formularios.
# En desarrollo da igual cual sea. En la compu del cliente se genera una al
# azar la primera vez y se guarda en la carpeta de datos.
if PRODUCCION:
    archivo_clave = DATOS_DIR / 'clave_secreta.txt'
    if not archivo_clave.exists():
        from django.core.management.utils import get_random_secret_key
        archivo_clave.write_text(get_random_secret_key())
    SECRET_KEY = archivo_clave.read_text().strip()
else:
    SECRET_KEY = 'django-insecure-entre-brasas-clave-de-desarrollo'

# Con DEBUG en True, si hay un error Django muestra el detalle en pantalla.
# Sirve mientras desarrollamos, pero al cliente le tiene que aparecer un
# mensaje normal, no una pantalla llena de codigo.
DEBUG = not PRODUCCION

# Desde que direcciones se puede entrar al sistema. En la compu del cliente
# solo desde esa misma compu.
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Las aplicaciones que carga Django al arrancar.
INSTALLED_APPS = [
    # Las que vienen con Django:
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Las nuestras, una por cada parte del negocio:
    'pedidos',      # los pedidos de los clientes
    'menu',         # hamburguesas y adicionales
    'inventario',   # ingredientes, stock y recetas
    'reportes',     # reportes de ventas
    'costos',       # costos y ganancia por producto
    'config',       # tarifas y parametros del sistema
]

# Cada pedido del navegador pasa por esta lista de arriba hacia abajo.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'entre_brasas.middleware.BloqueoDuranteApagadoMiddleware',
    # Sirve el CSS. Con DEBUG en False Django deja de hacerlo solo.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',          # protege los formularios
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Donde empieza Django a buscar las direcciones.
ROOT_URLCONF = 'entre_brasas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # La carpeta donde estan nuestras pantallas HTML.
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            # Estos le agregan variables a TODAS las pantallas sin que la
            # vista tenga que pasarlas una por una.
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'entre_brasas.context_processors.navegacion',
            ],
        },
    },
]

WSGI_APPLICATION = 'entre_brasas.wsgi.application'

# Base de datos: un archivo llamado db.sqlite3. En desarrollo esta dentro de
# la carpeta del proyecto; en la compu del cliente, en la carpeta de datos.
# SQLite no necesita instalar ni configurar nada: es un solo archivo.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATOS_DIR / 'db.sqlite3',
    }
}

# Idioma y zona horaria.
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
# Las fechas se guardan en horario universal y se muestran en el nuestro.
USE_TZ = True

# Archivos de estilo (el CSS).
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# WhiteNoise sirve el CSS directo desde la carpeta static, sin tener que
# copiarlo antes a otro lado con collectstatic.
WHITENOISE_USE_FINDERS = True

# Tipo de numero que usa Django para el id automatico de cada tabla.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Consultas repetidas no gastan créditos. Archivos locales, nunca publicados.
CACHES = {
    'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
    'mapas': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': DATOS_DIR / 'cache_mapas',
        'OPTIONS': {'MAX_ENTRIES': 2000},
    },
    'mapas_control': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': DATOS_DIR / 'cache_mapas' / 'control',
        'OPTIONS': {'MAX_ENTRIES': 1000},
    },
}
MAPAS_LIMITE_DIARIO = 2000  # Créditos preventivos de esta instalación; no saldo real del proveedor.
MAPAS_TILE_URL = os.environ.get('ENTRE_BRASAS_MAPAS_TILE_URL', '/pedidos/mapas/mosaicos/{z}/{x}/{y}.png')
MAPAS_TILE_ATTRIBUTION = os.environ.get('ENTRE_BRASAS_MAPAS_TILE_ATTRIBUTION', '© OpenStreetMap contributors · Geoapify')

# En la compu del cliente los errores no se muestran en pantalla (DEBUG esta
# apagado), asi que se anotan en un archivo para poder revisarlos despues:
# C:/Users/<usuario>/AppData/Local/EntreBrasas/errores.log
if PRODUCCION:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'archivo': {
                'class': 'logging.FileHandler',
                'filename': DATOS_DIR / 'errores.log',
                'level': 'ERROR',
                'encoding': 'utf-8',
            },
        },
        'loggers': {
            'django': {'handlers': ['archivo'], 'level': 'ERROR'},
        },
    }
