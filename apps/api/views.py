# em/apps/api/views.py
"""Views"""
# ------------------------------------------------
# Автор кода не несет ответственности за сломанные F5
# ------------------------------------------------
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    CreateAPIView, 
    UpdateAPIView,
    DestroyAPIView,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from api.serializers import (
    RegisterUserSerializer,
    LoginUserSerializer,
    AdSerializer,
    ExchangeProposalSerializer,
    ExchangeProposalUpdateStatusSerializer
)
from core.models import Ad, ExchangeProposal
from .services import AdService, ExchangeProposalService


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema(
    request=RegisterUserSerializer,
    responses={
        201: OpenApiResponse(description="Пользователь успешно создан"),
        400: OpenApiResponse(response=ValidationError, description="Ошибка валидации")
    },
    description="Регистрация нового пользователя"
)
class RegisterUserView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)
        
@extend_schema(
    request=LoginUserSerializer,
    responses={200: TokenObtainPairSerializer},
    description="Авторизация по email и паролю"
)
class LoginUserView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginUserSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        user = authenticate(username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        
        return Response({"error": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)



@extend_schema(
    request=AdSerializer,
    responses={
        201: AdSerializer,
        400: OpenApiResponse(description="Ошибка валидации"),
        403: OpenApiResponse(description="Не авторизован")
    },
    description="Создание нового объявления"
)
class AdCreateView(CreateAPIView):
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@extend_schema(
    request=AdSerializer,
    responses={
        200: AdSerializer, 
        404: OpenApiResponse(description="Объявление не найдено")
    },
    description="Обновление объявления по ID"
)
class AdUpdateView(UpdateAPIView):
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'ad_id'

    def get_queryset(self):
        return Ad.objects.filter(user=self.request.user)


@extend_schema(
    responses={
        204: OpenApiResponse(description="Объявление удалено"), 
        404: OpenApiResponse(description="Не найдено")
    },
    description="Удаление своего объявления по ID"
)
class AdDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'ad_id'

    def get_queryset(self):
        return Ad.objects.filter(user=self.request.user)



@extend_schema(
    parameters=[
        OpenApiParameter(name='q', description='Поисковый запрос', required=False, type=str),
        OpenApiParameter(name='category', description='Фильтр по категории', required=False, type=str),
        OpenApiParameter(name='condition', description='Фильтр по состоянию', required=False, type=str),
    ],
    responses={200: AdSerializer(many=True)},
    description="Поиск объявлений по тексту, категории и состоянию"
)
class AdSearchView(ListAPIView):
    serializer_class = AdSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        category = self.request.query_params.get('category')
        condition = self.request.query_params.get('condition')

        filters = Q(title__icontains=query) | Q(description__icontains=query)
        if category:
            filters &= Q(category=category)
        if condition:
            filters &= Q(condition=condition)

        return Ad.objects.filter(filters)



@extend_schema(
    request=ExchangeProposalSerializer,
    responses={
        201: ExchangeProposalSerializer, 
        400: OpenApiResponse(description="Ошибка валидации")
    },
    description="Создание предложения обмена"
)
class ExchangeProposalCreateView(CreateAPIView):
    serializer_class = ExchangeProposalSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            ad_sender_id = self.kwargs['ad_id']
            ad_sender = Ad.objects.get(id=ad_sender_id, user=request.user)

            ad_receiver_id = self.request.data.get('ad_receiver')
            ad_receiver = Ad.objects.get(id=ad_receiver_id, user=request.user)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            ad_receiver = serializer.validated_data['ad_receiver']
            
            proposal = ExchangeProposal.objects.create(
                ad_sender=ad_sender,
                ad_receiver=ad_receiver,
                comment=serializer.validated_data['comment'],
                status='pending'
            )

        
            return Response(ExchangeProposalSerializer(proposal).data, status=status.HTTP_201_CREATED)
            
        except Ad.DoesNotExist:
            return Response({"detail": "Одно из объявлений не найдено или вам не принадлежит"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    request=ExchangeProposalUpdateStatusSerializer,
    responses={
        200: ExchangeProposalSerializer, 
        404: OpenApiResponse(description="Не найдено")
    },
    description="Обновление статуса предложения обмена (accepted/rejected)"
)
class ExchangeProposalUpdateStatusView(GenericAPIView):
    serializer_class = ExchangeProposalUpdateStatusSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        proposal = get_object_or_404(ExchangeProposal, id=self.kwargs['proposal_id'])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_proposal = ExchangeProposalService.update_proposal_status(
                proposal=proposal,
                status=serializer.validated_data['status'],
                user=request.user
            )
            return Response(ExchangeProposalSerializer(updated_proposal).data)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

class ExchangeProposalListView(ListAPIView):
    serializer_class = ExchangeProposalSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return ExchangeProposal.objects.filter(
            Q(ad_receiver__user=self.request.user) | 
            Q(ad_sender__user=self.request.user)
        ).select_related(
            'ad_sender', 
            'ad_receiver'
        ).order_by('-created_at')