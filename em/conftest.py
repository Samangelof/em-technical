import os
import sys
import django


def pytest_configure():
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'apps')))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.base')
    django.setup()