# em/apps/api/urls.py
# ------------------------------------------------
#* Локация для юрлов не включается, 
#* поэтому передаю координаты для сервера
# ------------------------------------------------
from django.urls import path, include
from .views import (
    AdCreateView,
    AdUpdateView,
    AdDeleteView,
    AdSearchView,
    ExchangeProposalCreateView,
    ExchangeProposalUpdateStatusView,
    ExchangeProposalListView,
    RegisterUserView,
    LoginUserView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('auth/', include([
        path('register/', RegisterUserView.as_view(), name='_register'),
        path('login/', LoginUserView.as_view(), name='_login'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ])),


    #! Лучше бы ads и proposals разнести в отдельные апки
    path('ads/', include([
        path('create/', AdCreateView.as_view(), name='_ad-create'),
        path('update/<int:ad_id>/', AdUpdateView.as_view(), name='_ad-update'),
        path('delete/<int:ad_id>/', AdDeleteView.as_view(), name='_ad-delete'),
        path('search/', AdSearchView.as_view(), name='_ad-search'),
    ])),

    path('proposals/', include([
        path('', ExchangeProposalListView.as_view(), name='_proposal-list'),
        path('create/<int:ad_id>/', ExchangeProposalCreateView.as_view(), name='_proposal-create'),
        path('update/<int:proposal_id>/status/', ExchangeProposalUpdateStatusView.as_view(), name='_proposal-status'),
    ])),
]