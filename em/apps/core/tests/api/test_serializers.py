# em/apps/ads/tests/test_serializers.py
import pytest
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from core.models import Ad, ExchangeProposal
from api.serializers import AdSerializer, ProposalSerializer


@pytest.mark.django_db
class TestAdSerializer:

    def test_valid_ad_serializer(self):
        user = User.objects.create_user(username="user", password="pass")
        data = {
            "title": "Test Ad",
            "description": "Some description",
            "image_url": "https://img.com/ad.png",
            "category": "tech",
            "condition": "new"
        }

        factory = APIRequestFactory()
        request = factory.post("/fake-url/")
        request.user = user

        serializer = AdSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        ad = serializer.save(user=user)
        assert ad.title == "Test Ad"
        assert ad.user == user


    def test_invalid_condition(self):
        user = User.objects.create_user(username="user", password="pass")
        data = {
            "title": "Title",
            "description": "desc",
            "image_url": "https://img.com",
            "category": "cat",
            "condition": "broken"
        }

        # Мок реквеста для второго теста тоже
        factory = APIRequestFactory()
        request = factory.post("/fake-url/")
        request.user = user

        serializer = AdSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "condition" in serializer.errors

@pytest.mark.django_db
class TestProposalSerializer:

    def setup_method(self):
        self.user1 = User.objects.create_user(username="u1", password="pass")
        self.user2 = User.objects.create_user(username="u2", password="pass")
        self.ad1 = Ad.objects.create(user=self.user1, title="Ad1", description="desc", image_url="http://img", category="c", condition="new")
        self.ad2 = Ad.objects.create(user=self.user2, title="Ad2", description="desc", image_url="http://img", category="c", condition="used")

    def test_valid_proposal_serializer(self):
        data = {
            "ad_sender": self.ad1.id,
            "ad_receiver": self.ad2.id,
            "comment": "Want to exchange?"
        }
        request = type('Request', (), {'method': 'POST', 'user': self.user1})
        serializer = ProposalSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        
        # Явно передаём объекты при сохранении
        proposal = serializer.save(ad_sender=self.ad1, ad_receiver=self.ad2)
        
        assert proposal.ad_sender == self.ad1
        assert proposal.ad_receiver == self.ad2
        assert proposal.comment == "Want to exchange?"

    def test_invalid_same_ad(self):
        data = {
            "sender_ad_id": self.ad1.id,
            "receiver_ad_id": self.ad1.id,
            "comment": "Self deal?"
        }
        serializer = ProposalSerializer(data=data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_duplicate_proposal(self):
        ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment="First try"
        )
        data = {
            "sender_ad_id": self.ad1.id,
            "receiver_ad_id": self.ad2.id,
            "comment": "Duplicate"
        }
        serializer = ProposalSerializer(data=data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
