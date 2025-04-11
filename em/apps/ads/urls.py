# em/apps/ads/urls.py  
from django.urls import path
from .views import (
    ad_list,
    ad_detail,
    create_ad,
    edit_ad, 
    signup,
    user_login,
    user_logout
)


urlpatterns = [
    path('', ad_list, name='ad_list'),
    path('ad/<int:ad_id>/', ad_detail, name='ad_detail'),
    path('create/', create_ad, name='create_ad'),
    path('edit/<int:ad_id>/', edit_ad, name='edit_ad'),

    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]
