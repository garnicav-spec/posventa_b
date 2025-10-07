# core/deployment_settings.py

import os
import sys
from pathlib import Path
from .settings import *  # hereda configuración base


# 1. Añadir carpeta de aplicaciones al PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Configuración de entorno
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'donboscofrontend.onrender.com').split(',')

import dj_database_url
# Cargar la URL de la base de datos desde las variables de entorno
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),  # Se obtiene desde la variable de entorno
        conn_max_age=600,
        ssl_require=True  # Requiere SSL en Azure
    )
}

STATIC_ROOT = BASE_DIR / 'staticfiles'  # Carpeta donde se almacenarán los archivos estáticos procesados
# Usar el almacenamiento comprimido y optimizado de WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 5. CORS: solo origen de frontend
CORS_ALLOWED_ORIGINS = [
    os.environ.get('FRONTEND_URL', 'http://localhost:5173'),
]
