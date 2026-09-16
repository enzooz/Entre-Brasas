"""
Configuración global del proyecto Django "Entre Brasas".

Este archivo es el que Django lee al arrancar. Define qué apps existen,
cómo se conecta a la base de datos, dónde están los templates, etc.
Todo lo que esté acá en MAYÚSCULAS es una "setting" que Django busca por nombre.
"""

import os
from pathlib import Path

# BASE_DIR = la carpeta "Desarrollo App" (la raíz del proyecto).
# __file__ es este archivo -> .resolve() lo vuelve ruta absoluta
# -> .parent es la carpeta entre_brasas/ -> .parent otra vez es "Desarrollo App".
# Se usa más abajo para armar rutas sin escribirlas a mano.
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave que Django usa para firmar cookies de sesión, tokens CSRF y passwords.
# OJO: está escrita directamente acá y commiteada al repo. En producción esto
# tiene que salir de una variable de entorno (os.environ['SECRET_KEY']).
SECRET_KEY = 'django-insecure-av(4#p+t()pwb(-8w&lptzj3ubr%jesj^mrh9hzj1-sd%hcxvo'

# DEBUG=True hace que los errores muestren el stacktrace completo en el navegador
# y que Django sirva los archivos estáticos solo. Sirve para desarrollar.
# OJO: en producción tiene que ser False, si no se filtra código y configuración.
DEBUG = True

# Lista blanca de dominios desde los que se puede servir la app.
# Vacía funciona solo porque DEBUG=True (Django asume localhost).
# Con DEBUG=False y esta lista vacía, la app no responde a nadie.
ALLOWED_HOSTS = []

# Las apps que Django carga al arrancar. El orden importa poco acá,
# pero la división sí: las primeras son de Django, las últimas son nuestras.
INSTALLED_APPS = [
    'django.contrib.auth',           # sistema de usuarios y permisos (instalado pero sin usar todavía)
    'django.contrib.contenttypes',   # registro interno de modelos, lo necesita auth
    'django.contrib.sessions',       # sesiones por cookie
    'django.contrib.messages',       # los mensajes de "Pedido creado exitosamente"
    'django.contrib.staticfiles',    # manejo de CSS/JS
    # Nuestras apps, una por dominio de negocio:
    'apps.orders',      # pedidos: alta, cola, historial, cambios de estado
    'apps.menu',        # hamburguesas y adicionales
    'apps.inventory',   # ingredientes, stock, recetas, movimientos
    'apps.reports',     # reportes de ventas (hoy renderiza data falsa desde JS)
    'apps.costs',       # costos por producto (idem, hoy es JS con mocks)
    'apps.config',      # configuración del sistema (tarifas de envío, mano de obra)
]

# Cadena de middlewares: cada request pasa por acá de arriba hacia abajo,
# y cada response vuelve de abajo hacia arriba. Es el orden por defecto de Django.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',            # headers de seguridad
    'django.contrib.sessions.middleware.SessionMiddleware',     # carga request.session
    'django.middleware.common.CommonMiddleware',                # normaliza URLs
    'django.middleware.csrf.CsrfViewMiddleware',                # valida el token CSRF en los POST
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # carga request.user
    'django.contrib.messages.middleware.MessageMiddleware',     # habilita messages.success(...)
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   # evita que nos metan en un iframe
]

# Archivo donde Django empieza a buscar las URLs (ver entre_brasas/urls.py).
ROOT_URLCONF = 'entre_brasas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # DIRS = carpeta global de templates ("Desarrollo App/templates").
        'DIRS': [BASE_DIR / 'templates'],
        # APP_DIRS=True hace que además busque en cada app/templates/.
        'APP_DIRS': True,
        'OPTIONS': {
            # Los context processors inyectan variables en TODOS los templates
            # sin que la vista las pase explícitamente.
            'context_processors': [
                'django.template.context_processors.request',   # da {{ request }}
                'django.contrib.auth.context_processors.auth',  # da {{ user }}
                'django.contrib.messages.context_processors.messages',  # da {{ messages }}
            ],
        },
    },
]

WSGI_APPLICATION = 'entre_brasas.wsgi.application'

# --- Base de datos -------------------------------------------------------
# La idea: si existe la variable de entorno DATABASE_URL, usamos PostgreSQL.
# Si no existe, caemos a SQLite (un archivo local, cero configuración).
# Así el mismo código corre en tu máquina y en un servidor sin tocar nada.
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # DATABASE_URL viene con formato: postgres://usuario:password@host:puerto/nombre_db
    # urlparse lo parte en pedazos para poder armar el diccionario de Django.
    import urllib.parse
    url = urllib.parse.urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': url.path[1:],  # el [1:] saca la "/" inicial de la ruta
            'USER': url.username or 'postgres',
            'PASSWORD': url.password or '',
            'HOST': url.hostname or 'localhost',
            'PORT': url.port or '5432',
        }
    }
else:
    # Modo por defecto: un archivo db.sqlite3 en la raíz del proyecto.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Reglas que Django aplica al crear/cambiar contraseñas.
# Están activas pero hoy no se usan porque no hay login en el sistema.
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Localización --------------------------------------------------------
LANGUAGE_CODE = 'es-ar'                            # textos de Django en español argentino
TIME_ZONE = 'America/Argentina/Buenos_Aires'       # zona horaria para mostrar fechas
USE_I18N = True                                    # activa el sistema de traducciones
USE_TZ = True                                      # guarda las fechas en UTC en la DB y las convierte al mostrarlas

# --- Archivos estáticos (CSS/JS) -----------------------------------------
STATIC_URL = 'static/'                    # prefijo de las URLs: /static/js/app.js
STATICFILES_DIRS = [BASE_DIR / 'static']  # carpeta física donde están

# Tipo de columna que Django usa para los IDs automáticos de los modelos.
# BigAutoField = entero de 64 bits (no se queda corto nunca).
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
