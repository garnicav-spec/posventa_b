import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret Key (en producción, siempre debe estar en variables de entorno)
SECRET_KEY = os.environ['MY_SECRET_KEY']

DEBUG = False

#CORS_ALLOWED_ORIGINS = ['https://systema-pos-b-dhgsetd9dcfxadew.chilecentral-01.azurewebsites.net']  # Asegúrate de configurar esta variable en Azure,
ALLOWED_HOSTS = [
    'djangowebappbckxz-bmd0g0eqdpbgg9a5.chilecentral-01.azurewebsites.net',
    'www.djangowebappbckxz-bmd0g0eqdpbgg9a5.chilecentral-01.azurewebsites.net',
]

CORS_ALLOWED_ORIGINS = [
    'https://', 
]

#aqui tambien va frontend
CSRF_TRUSTED_ORIGINS = [
    'https://djangowebappbckxz-bmd0g0eqdpbgg9a5.chilecentral-01.azurewebsites.net',
]

#add the next middleware for whitenoise
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
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

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',  # Asegura que la conexión sea segura (SSL)
        },
    }
}
# Static files settings (Para producción, usar WhiteNoise para servir archivos estáticos)
STATIC_ROOT = BASE_DIR / 'staticfiles'
