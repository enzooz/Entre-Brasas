"""
Configuracion del proyecto Entre Brasas.

Django lee este archivo al arrancar. Todo lo que este escrito en MAYUSCULAS
es una opcion que Django busca por nombre.
"""
import os
from pathlib import Path

# La carpeta donde esta el proyecto ("Desarrollo App").
# __file__ es este archivo, .resolve() lo convierte en ruta completa,
# y cada .parent sube una carpeta.
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave que Django usa para firmar las cookies y los formularios.
# En un sistema de verdad tendria que salir de una variable de entorno.
SECRET_KEY = 'django-insecure-entre-brasas-clave-de-desarrollo'

# Con DEBUG en True, si hay un error Django muestra el detalle en pantalla.
# Sirve mientras desarrollamos.
DEBUG = True

# Desde que direcciones se puede entrar al sistema.
# Vacio funciona porque DEBUG esta en True (Django asume que es local).
ALLOWED_HOSTS = []

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
            ],
        },
    },
]

WSGI_APPLICATION = 'entre_brasas.wsgi.application'

# Base de datos: un archivo llamado db.sqlite3 dentro de la carpeta del proyecto.
# SQLite no necesita instalar ni configurar nada: es un solo archivo.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

# Tipo de numero que usa Django para el id automatico de cada tabla.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
