# em/settings/urls.py
"""URL конфигурация проекта"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from settings.config import ADMIN_SITE_URL

handler404 = 'ads.views.custom_404_view'

urlpatterns = [
    path(ADMIN_SITE_URL, admin.site.urls),
    # path('api-auth/', include('rest_framework.urls')),    # Канонический путь для DRF
    path('docs/api/', include('settings.urls_docs')),   # Docs

    path('ads/', include('ads.urls')),  # MVC
    path('api/', include('api.urls')),  # REST API
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)