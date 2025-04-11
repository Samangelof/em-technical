# em/apps/api/urls.py
# ------------------------------------------------
#* Локация для юрлов не включается, 
#* поэтому передаю координаты для сервера
# ------------------------------------------------
from django.urls import path
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
    # Объявления
    path('api/create/', AdCreateView.as_view(), name='api_create_ad'),
    path('api/<int:ad_id>/update/', AdUpdateView.as_view(), name='api_update_ad'),
    path('api/<int:ad_id>/delete/', AdDeleteView.as_view(), name='api_delete_ad'),
    path('api/search/', AdSearchView.as_view(), name='api_search_ads'),

    # Регистрация
    path('auth/register/', RegisterUserView.as_view(), name='api_register_user'),
    path('auth/login/', LoginUserView.as_view(), name='api_login_user'),

    # Предложения обмена
    path('proposals/', ExchangeProposalCreateView.as_view(), name='api_exchange_proposal_create'),
    path('proposals/<int:proposal_id>/status/', ExchangeProposalUpdateStatusView.as_view(), name='api_exchange_proposal_update_status'),
    path('proposals/list/', ExchangeProposalListView.as_view(), name='api_exchange_proposal_list'),
]
