# em/settings/urls.py
"""URL конфигурация проекта"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from settings.config import ADMIN_SITE_URL


urlpatterns = [
    path(ADMIN_SITE_URL, admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/docs/', include('settings.urls_docs')),

    path('', include('ads.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)