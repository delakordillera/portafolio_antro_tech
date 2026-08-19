"""
Django settings for core project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY: nunca lo escribas en texto plano aquí. Se lee de una variable
# de entorno DJANGO_SECRET_KEY (configúrala en PythonAnywhere: pestaña Web >
# Environment variables, o dentro del archivo WSGI antes del import de la
# app). El valor de más abajo es SOLO un fallback para correr localmente y
# no sirve para producción — si el key anterior (el que estaba hardcodeado
# y quedó público en GitHub) sigue siendo el que usa el sitio en vivo,
# cámbialo por este nuevo antes de desplegar:
# __1*8ch5+p7-^jhbkk96g=dd8v3cy3l_3z@@v=_zk$@ao^a##7
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-local-dev-only-do-not-use-in-production-3fj28x',
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['delakordillera.pythonanywhere.com']
if DEBUG:
    ALLOWED_HOSTS += ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'comunidad',
    'main',
    'ecommerce',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'comunidad.context_processors.notificaciones_pendientes',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = '.'
NUMBER_GROUPING = 3

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'muro'
LOGOUT_REDIRECT_URL = 'muro'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------- Seguridad en producción ----------
# PythonAnywhere termina TLS en su proxy y reenvía la petición por HTTP,
# indicando el protocolo original en este header. Sin esto, Django nunca
# detecta que la conexión es HTTPS y SECURE_SSL_REDIRECT/cookies "secure"
# provocarían un loop de redirects.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    # HSTS: empieza bajo (1 día) y solo lo subes a 1 año una vez que
    # confirmes que todo el sitio carga bien por HTTPS.
    SECURE_HSTS_SECONDS = 86400
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
