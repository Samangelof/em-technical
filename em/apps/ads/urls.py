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
    create_exchange_proposal,
    update_exchange_proposal_status,
    my_exchanges
)


# Сахар
urlpatterns = [
    path('auth/', include([ 
        path('signup/', signup, name='signup'),
        path('login/', user_login, name='login'),
        path('logout/', user_logout, name='logout'),
    ])),

    path('ads/', include([  #! На самом деле , это не нужно, 
        #! но для удобства можно оставить, чтобы не путаться в юрлах
        path('', ad_list, name='ad_list'),
        path('create/', create_ad, name='create_ad'),
        path('detail/<int:ad_id>/', ad_detail, name='ad_detail'),
        path('edit/<int:ad_id>/edit/', edit_ad, name='edit_ad'),
        path('delete/<int:ad_id>/delete/', delete_ad, name='delete_ad'),
    ])),

    path('proposals/', include([
        path('ad/<int:ad_id>/exchange/', create_exchange_proposal, name='create_exchange_proposal'),
        path('exchange/<int:proposal_id>/status/<str:new_status>/', update_exchange_proposal_status, name='update_exchange_proposal_status')
    ])),

    path('me/', include([
        path('my-exchanges/', my_exchanges, name='my_exchanges'),
        path('exchange/<int:proposal_id>/<str:new_status>/', update_exchange_proposal_status, name='update_exchange_status'),
    ])),
]
