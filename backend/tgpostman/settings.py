"""
Django settings
Main configuration for the tgpostman Django project.
"""

# --------------------------------------------------------------------------------
# IMPORTS

import os
from pathlib import Path

from decouple import config
from telebot import TeleBot

# --------------------------------------------------------------------------------
# BASE DIRECTORY

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------------
# SECURITY SETTINGS

DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = [
    '*',  # REPLACE !!!!
]

SECRET_KEY = config('SECRET_KEY')
ADMIN_SWAGGER_LOGIN = config('ADMIN_SWAGGER_LOGIN')
ADMIN_SWAGGER_PASSWORD = config('ADMIN_SWAGGER_PASSWORD')

# --------------------------------------------------------------------------------
# APPLICATION DEFINITION

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_celery_results',
    'django_celery_beat',
    'users',
    'chat_groups',
    'telegram_accounts',
    'scheduled_posts',
    'crispy_forms',
    'crispy_bootstrap5',
    "drf_yasg",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

ROOT_URLCONF = 'tgpostman.urls'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = 'bootstrap5'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tgpostman.wsgi.application'

# --------------------------------------------------------------------------------
# DATABASE SETTINGS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('POSTGRES_HOST'),
        'PORT': config('POSTGRES_PORT'),
    }
}

# --------------------------------------------------------------------------------
# CELERY SETTINGS

CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# --------------------------------------------------------------------------------
# PASSWORD VALIDATION

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------------------------------------------------------------
# INTERNATIONALIZATION

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------------
# STATIC FILES

if DEBUG:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'

# --------------------------------------------------------------------------------
# DEFAULT PRIMARY KEY FIELD TYPE

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------------------------------------
# LOGIN SETTINGS

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

AUTH_USER_MODEL = 'users.User'

# --------------------------------------------------------------------------------
# REST FRAMEWORK

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentication.ApiKeyAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# --------------------------------------------------------------------------------
# LANGUAGE CHOICES

LANG_CHOICES = [
    ('en', 'English'), ('zh', 'Chinese'), ('hi', 'Hindi'), ('es', 'Spanish'),
    ('fr', 'French'), ('ar', 'Arabic'), ('bn', 'Bengali'), ('ru', 'Russian'),
    ('pt', 'Portuguese'), ('ur', 'Urdu'), ('id', 'Indonesian'), ('de', 'German'),
    ('ja', 'Japanese'), ('sw', 'Swahili'), ('mr', 'Marathi'), ('te', 'Telugu'),
    ('ta', 'Tamil'), ('vi', 'Vietnamese'), ('tr', 'Turkish'), ('ko', 'Korean'),
    ('fa', 'Persian'), ('it', 'Italian'), ('pl', 'Polish'), ('pa', 'Punjabi'),
    ('gu', 'Gujarati'), ('ml', 'Malayalam'), ('kn', 'Kannada'), ('my', 'Burmese'),
    ('th', 'Thai'), ('uk', 'Ukrainian'), ('ro', 'Romanian'), ('nl', 'Dutch'),
    ('hu', 'Hungarian'), ('cs', 'Czech'), ('el', 'Greek'), ('sv', 'Swedish'),
    ('fi', 'Finnish'), ('no', 'Norwegian'), ('da', 'Danish'), ('he', 'Hebrew'),
    ('sr', 'Serbian'), ('hr', 'Croatian'), ('bg', 'Bulgarian'), ('sk', 'Slovak'),
    ('sl', 'Slovene'), ('lt', 'Lithuanian'), ('lv', 'Latvian'), ('et', 'Estonian'),
    ('ka', 'Georgian'), ('hy', 'Armenian'), ('az', 'Azerbaijani'), ('kk', 'Kazakh'),
    ('uz', 'Uzbek'), ('tk', 'Turkmen'), ('ne', 'Nepali'), ('si', 'Sinhala'),
    ('lo', 'Lao'), ('km', 'Khmer'), ('mn', 'Mongolian'), ('am', 'Amharic'),
    ('so', 'Somali'), ('yo', 'Yoruba'), ('ig', 'Igbo'), ('ha', 'Hausa'),
    ('zu', 'Zulu'), ('xh', 'Xhosa'), ('rw', 'Kinyarwanda'), ('sn', 'Shona'),
    ('ny', 'Chichewa'), ('tg', 'Tajik'), ('ps', 'Pashto'), ('ky', 'Kyrgyz'),
    ('qu', 'Quechua'), ('ay', 'Aymara'), ('gn', 'Guarani'), ('ht', 'Haitian Creole'),
    ('jw', 'Javanese'), ('su', 'Sundanese'), ('ceb', 'Cebuano'), ('ilo', 'Ilocano'),
    ('mi', 'Maori'), ('sm', 'Samoan'), ('to', 'Tongan'), ('haw', 'Hawaiian'),
    ('la', 'Latin'), ('eo', 'Esperanto'), ('cy', 'Welsh'), ('gd', 'Scottish Gaelic'),
    ('ga', 'Irish'), ('br', 'Breton'), ('co', 'Corsican'), ('eu', 'Basque'),
    ('mt', 'Maltese'), ('bs', 'Bosnian'), ('mk', 'Macedonian'), ('af', 'Afrikaans'),
    ('is', 'Icelandic'), ('sq', 'Albanian'), ('be', 'Belarusian'),
]

# --------------------------------------------------------------------------------
# TELEGRAM BOT INSTANCE

BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
bot = TeleBot(token=BOT_TOKEN)

BOT_USERNAME = None
try:
    BOT_USERNAME = bot.get_me().username
except Exception:
    pass
