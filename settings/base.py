# em/settings/base.py
# ------------------------------------------------
#! Приложение собрано в подземном бункере.
#! Все совпадения с реальностью — просто хорошая архитектура.
#! Разработал @Samangelof
# ------------------------------------------------
from pathlib import Path
import os
import sys
from datetime import timedelta
from .config import DEBUG, SECRET_KEY


# ------------------------------------------------
# Path and hosts
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'apps'))

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# ------------------------------------------------
# Apps
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'drf_spectacular',
    'rest_framework',
    'rest_framework_simplejwt',   # For Frontend JWT Auth
    'ads.apps.AdsConfig', 
    'api.apps.ApiConfig',
    'core.apps.CoreConfig',
]

# ------------------------------------------------
# CORS
CORS_ORIGIN_ALLOW_ALL = DEBUG 
CORS_ALLOW_ALL_ORIGINS = DEBUG 
CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
# CORS Production
# CORS_ALLOWED_ORIGINS = [
#     "https://devunlimited.tech",
# ] if not DEBUG else []

# ------------------------------------------------
# Middleware | Templates | Validators
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',    #! Для тестов на swagger, закомментировать - '.CsrfViewMiddleware'
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'deploy.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# ------------------------------------------------
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
} if not DEBUG else {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ------------------------------------------------
# Documentation
# settings.py
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Type in the *\'Bearer\'* prefix followed by space and JWT token. Example: "Bearer abcde12345"'
        }
    },
    'USE_SESSION_AUTH': False,
    'DEFAULT_MODEL_RENDERING': 'example'
    # 'LOGIN_URL': 'admin:login',
    # 'LOGOUT_URL': 'admin:logout',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'API Documentation',
    'DESCRIPTION': 'API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'AUTHENTICATION_WHITELIST': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'SCHEMA_PATH_PREFIX': r'/api/',
}
# ------------------------------------------------
# logging
LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "simple": {
            "format": "[%(levelname)s] %(message)s"
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            # "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple"
        },
        "production_file": {
            "level": "WARNING",
            "filters": ["require_debug_false"],
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "production.log"),
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "debug_file": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "debug.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "errors_file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "errors.log"),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django.server": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django": {
            "handlers": ["console", "debug_file", "production_file", "errors_file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["debug_file"] if DEBUG else [],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["production_file", "errors_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "ads": {
            "handlers": ["console", "debug_file", "production_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


# ------------------------------------------------
# UI Admin
# https://django-jazzmin.readthedocs.io/configuration/
JAZZMIN_SETTINGS = {
    "site_title": "Обмен Вещами",
    "site_header": "Админка Обмена Вещами",
    "site_brand": "Обмен Вещами",
    "site_icon": "images/icon.png",
    "welcome_sign": "Добро пожаловать в админку обмена вещами",
    "search_model": "auth.User",


    "show_ui_builder": True,
    "default_site": "admin",
    

    "topmenu_links": [
        {"name": "Главная", "url": "/", "permissions": ["auth.view_user"]},
        {"name": "Объявления", "url": "admin:ads_ad_changelist", "permissions": ["ads.view_ad"]},
        {"name": "Предложения обмена", "url": "admin:ads_exchangeproposal_changelist", "permissions": ["ads.view_exchangeproposal"]},
    ],
    
    "icons": {
        "auth.User": "fas fa-users",
        "ads.Ad": "fas fa-clipboard-list",
        "ads.ExchangeProposal": "fas fa-exchange-alt",
    },
    
    "show_sidebar": True,
    "show_navigation": True,
    "show_recent_actions": False,
}


# ------------------------------------------------
# Simple JWT
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}


# ------------------------------------------------
# REST Framework settings
REST_FRAMEWORK = {
    # Аутентификация
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    
    # Права доступа
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.AllowAny',
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {
        'user': '5/minute'
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # Пагинация
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # Валидация
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    # Брутфорс
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    # Форматы дат
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
}

# ------------------------------------------------
# Other
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


# ------------------------------------------------
# Security settings
# MIME-sniffing и clickjacking
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# ------------------------------------------------
# Custom User Model
# AUTH_USER_MODEL = "auths.CustomUser"


# Уроню, если не будет переменных окружения
if not DEBUG:
    required_env_vars = ['DB_NAME', 'DB_HOST', 'SECRET_KEY']
    for var in required_env_vars:
        if not os.getenv(var):
            raise ValueError(f"Не задана env-переменная: {var}")