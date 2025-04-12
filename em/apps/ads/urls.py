# em/apps/ads/urls.py  
from django.urls import path, include
from .views import (
    ad_list,
    ad_detail,
    create_ad,
    edit_ad, 
    signup,
    user_login,
    user_logout,
    delete_ad,
)


urlpatterns = [
    path('ads/', include([  #! На самом деле , это не нужно, 
        #! но для удобства можно оставить, чтобы не путаться в юрлах
        path('', ad_list, name='ad_list'),
        path('create/', create_ad, name='create_ad'),
        path('<int:ad_id>/', ad_detail, name='ad_detail'),
        path('<int:ad_id>/edit/', edit_ad, name='edit_ad'),
        path('<int:ad_id>/delete/', delete_ad, name='delete_ad'),
    ])),

    path('auth/', include([ 
        path('signup/', signup, name='signup'),
        path('login/', user_login, name='login'),
        path('logout/', user_logout, name='logout'),
    ])),
]
