import os
import sys
from pathlib import Path
from .settings import *  # hereda configuración base

WIBBLE2 = 'Wibble2'

# 1. Añadir carpeta de aplicaciones al PYTHONPATH
#BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Configuración de entorno
#SECRET_KEY = os.environ['SECRET_KEY']
#DEBUG = os.environ.get('DEBUG', 'False') == 'True'
#ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'systema-pos-b-dhgsetd9dcfxadew.chilecentral-01.azurewebsites.net').split(',')

#import dj_database_url
# Cargar la URL de la base de datos desde las variables de entorno
#DATABASES = {
#    'default': dj_database_url.config(
#        default=os.environ.get('DATABASE_URL'),  # Se obtiene desde la variable de entorno
#        conn_max_age=600,
#        ssl_require=True  # Requiere SSL en Azure
#    )
#}

#STATIC_ROOT = BASE_DIR / 'staticfiles'  # Carpeta donde se almacenarán los archivos estáticos procesados

CORS_ALLOWED_ORIGINS = ['https://systema-pos-b-dhgsetd9dcfxadew.chilecentral-01.azurewebsites.net']  # Asegúrate de configurar esta variable en Azure,

#CSRF_TRUSTED_ORIGINS = ['https://*']
CSRF_TRUSTED_ORIGINS = ['https://systema-pos-b-dhgsetd9dcfxadew.chilecentral-01.azurewebsites.net']

#add the next middleware for whitenoise
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Enables whitenoise for serving static files
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
