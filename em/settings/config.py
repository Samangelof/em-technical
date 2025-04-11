# em/settings/config.py
"""Config"""
# ------------------------------------------------
# Здесь даже комментарии не нужны
# ------------------------------------------------
from . import get_env_variable


DEBUG = get_env_variable('DEBUG', cast=bool)
ADMIN_SITE_URL = get_env_variable('ADMIN_SITE_URL')
SECRET_KEY = get_env_variable('SECRET_KEY')