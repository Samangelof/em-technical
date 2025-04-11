# em/apps/api/views.py
"""Views"""
# ------------------------------------------------
# Автор кода не несет ответственности за сломанные F5
# ------------------------------------------------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from api.serializers import AdSerializer, ExchangeProposalSerializer, RegisterUserSerializer
from core.models import Ad, ExchangeProposal
from .services import AdService, ExchangeProposalService


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(TokenObtainPairView):
    permission_classes = [AllowAny]


class AdCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get('title')
        description = request.data.get('description')
        image_url = request.data.get('image_url', None)
        category = request.data.get('category')
        condition = request.data.get('condition')

        ad = AdService.create_ad(
            user=request.user,
            title=title,
            description=description,
            image_url=image_url,
            category=category,
            condition=condition
        )

        serializer = AdSerializer(ad)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AdUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, ad_id):
        ad = Ad.objects.get(id=ad_id, user=request.user)
        title = request.data.get('title')
        description = request.data.get('description')
        image_url = request.data.get('image_url', None)
        category = request.data.get('category')
        condition = request.data.get('condition')

        ad = AdService.update_ad(
            ad=ad,
            title=title,
            description=description,
            image_url=image_url,
            category=category,
            condition=condition
        )

        serializer = AdSerializer(ad)
        return Response(serializer.data)

class AdDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, ad_id):
        ad = Ad.objects.get(id=ad_id, user=request.user)
        AdService.delete_ad(ad)
        return Response(status=status.HTTP_204_NO_CONTENT)

class AdSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        category = request.query_params.get('category', None)
        condition = request.query_params.get('condition', None)

        ads = AdService.search_ads(query, category, condition)
        serializer = AdSerializer(ads, many=True)
        return Response(serializer.data)

class ExchangeProposalCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ad_id):
        ad_sender = request.user.ads.get(id=ad_id)
        ad_receiver_id = request.data.get('ad_receiver_id')
        ad_receiver = Ad.objects.get(id=ad_receiver_id)
        comment = request.data.get('comment')

        proposal = ExchangeProposalService.create_proposal(ad_sender, ad_receiver, comment)

        serializer = ExchangeProposalSerializer(proposal)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ExchangeProposalUpdateStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, proposal_id):
        proposal = ExchangeProposal.objects.get(id=proposal_id)
        status = request.data.get('status')

        proposal = ExchangeProposalService.update_proposal_status(proposal, status)

        serializer = ExchangeProposalSerializer(proposal)
        return Response(serializer.data)

class ExchangeProposalListView(APIView):
    def get(self, request):
        status = request.query_params.get('status', None)

        proposals = ExchangeProposalService.filter_by_status(status)
        serializer = ExchangeProposalSerializer(proposals, many=True)
        return Response(serializer.data)
