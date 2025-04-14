# em/apps/api/tests/test_services.py
import pytest
from django.contrib.auth.models import User
from core.models import Ad, ExchangeProposal
from api.services import AdService, ExchangeProposalService
from django.core.exceptions import ValidationError, PermissionDenied


@pytest.mark.django_db
class TestAdService:

    def test_create_ad(self):
        user = User.objects.create_user(username="testuser", password="pass")
        ad = AdService.create_ad(
            user=user,
            title="Bike",
            description="Cool bike",
            image_url="https://example.com/image.png",
            category="sports",
            condition="new"
        )
        assert ad.id is not None
        assert ad.title == "Bike"
        assert ad.user == user

    def test_update_ad(self):
        user = User.objects.create_user(username="testuser", password="pass")
        ad = Ad.objects.create(
            user=user,
            title="Old",
            description="Old",
            image_url="http://url.com",
            category="old",
            condition="used"
        )
        updated = AdService.update_ad(
            ad=ad,
            title="New title",
            description="Updated",
            image_url="https://new.com",
            category="new-cat",
            condition="new"
        )
        assert updated.title == "New title"
        assert updated.condition == "new"

    def test_delete_ad(self):
        user = User.objects.create_user(username="user", password="pass")
        ad = AdService.create_ad(user, "t", "d", "https://img", "cat", "used")
        ad_id = ad.id
        AdService.delete_ad(ad)
        assert not Ad.objects.filter(id=ad_id).exists()

    def test_search_ads(self):
        user = User.objects.create_user(username="user", password="pass")
        AdService.create_ad(user, "Bike", "Cool red bike", "http://img", "sports", "used")
        AdService.create_ad(user, "Car", "Fast car", "http://img", "vehicles", "new")
        results = AdService.search_ads("bike")
        assert len(results) == 1
        assert "Bike" in results[0].title


@pytest.mark.django_db
class TestExchangeProposalService:

    def test_create_proposal_success(self):
        u1 = User.objects.create_user(username="u1", password="pass")
        u2 = User.objects.create_user(username="u2", password="pass")
        ad1 = AdService.create_ad(u1, "A1", "d", "https://img", "cat", "new")
        ad2 = AdService.create_ad(u2, "A2", "d", "https://img", "cat", "used")
        proposal = ExchangeProposalService.create_proposal(ad1, ad2, comment="Обмен?")
        assert proposal.id is not None
        assert proposal.status == "pending"

    def test_create_proposal_self_exchange(self):
        user = User.objects.create_user(username="u", password="pass")
        ad1 = AdService.create_ad(user, "A", "d", "https://img", "c", "new")
        with pytest.raises(ValidationError):
            ExchangeProposalService.create_proposal(ad1, ad1)

    def test_create_duplicate_proposal(self):
        u1 = User.objects.create_user(username="u1", password="pass")
        u2 = User.objects.create_user(username="u2", password="pass")
        ad1 = AdService.create_ad(u1, "A1", "d", "https://img", "cat", "new")
        ad2 = AdService.create_ad(u2, "A2", "d", "https://img", "cat", "used")
        ExchangeProposalService.create_proposal(ad1, ad2)
        with pytest.raises(ValidationError):
            ExchangeProposalService.create_proposal(ad1, ad2)

    def test_update_proposal_status_success(self):
        sender = User.objects.create_user(username="sender", password="pass")
        receiver = User.objects.create_user(username="receiver", password="pass")
        ad_sender = AdService.create_ad(sender, "Sender Ad", "desc", "https://img", "cat", "new")
        ad_receiver = AdService.create_ad(receiver, "Receiver Ad", "desc", "https://img", "cat", "used")
        proposal = ExchangeProposalService.create_proposal(ad_sender, ad_receiver)
        updated = ExchangeProposalService.update_proposal_status(proposal, "accepted", receiver)
        assert updated.status == "accepted"

    def test_update_proposal_status_permission_denied(self):
        sender = User.objects.create_user(username="sender", password="pass")
        receiver = User.objects.create_user(username="receiver", password="pass")
        outsider = User.objects.create_user(username="outsider", password="pass")
        ad_sender = AdService.create_ad(sender, "A1", "d", "https://img", "c", "new")
        ad_receiver = AdService.create_ad(receiver, "A2", "d", "https://img", "c", "used")
        proposal = ExchangeProposalService.create_proposal(ad_sender, ad_receiver)
        with pytest.raises(PermissionDenied):
            ExchangeProposalService.update_proposal_status(proposal, "rejected", outsider)
