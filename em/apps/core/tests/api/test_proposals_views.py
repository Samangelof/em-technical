from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from core.models import Ad, ExchangeProposal
from django.contrib.auth.models import User


class TestExchangeProposalViews(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword")
        # Объявления для тестов
        self.ad1 = Ad.objects.create(user=self.user1, title="Ad 1", description="Test ad 1", category="electronics", condition="new")
        self.ad2 = Ad.objects.create(user=self.user2, title="Ad 2", description="Test ad 2", category="electronics", condition="new")
        
        # Аутентификация пользователя для тестов
        self.client.login(username="testuser1", password="testpassword")

    def test_create_proposal_success(self):
        """Тест успешного создания предложения обмена между объявлениями разных пользователей"""
        url = reverse("_proposal-create", args=[self.ad1.id])
        data = {
            "ad_receiver": self.ad2.id,
            "comment": "Interested in your ad"
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExchangeProposal.objects.count(), 1)

        proposal = ExchangeProposal.objects.first()
        self.assertEqual(proposal.ad_sender, self.ad1)
        self.assertEqual(proposal.ad_receiver, self.ad2)
        self.assertEqual(proposal.comment, "Interested in your ad")
        self.assertEqual(proposal.status, "pending")

    def test_create_proposal_own_ads(self):
        """Тест попытки создания предложения между своими же объявлениями"""
        ad3 = Ad.objects.create(user=self.user1, title="Ad 3", description="Test ad 3", category="electronics", condition="new")
        
        url = reverse("_proposal-create", args=[self.ad1.id])
        data = {
            "ad_receiver": ad3.id,
            "comment": "Trading with myself"
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ExchangeProposal.objects.count(), 0)
        
    def test_create_proposal_nonexistent_ad(self):
        """Тест попытки создания предложения с несуществующим объявлением"""
        url = reverse("_proposal-create", args=[self.ad1.id])
        data = {
            "ad_receiver": 9999,
            "comment": "This won't work"
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(ExchangeProposal.objects.count(), 0)
        
    def test_create_proposal_unauthorized_ad(self):
        """Тест попытки создания предложения с объявлением не принадлежащим пользователю"""
        self.client.logout()
        self.client.login(username="testuser2", password="testpassword")
        
        url = reverse("_proposal-create", args=[self.ad1.id])
        data = {
            "ad_receiver": self.ad2.id,
            "comment": "This won't work"
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(ExchangeProposal.objects.count(), 0)

    def test_list_proposals(self):
        """Тест получения списка предложений обмена для текущего пользователя"""
        ExchangeProposal.objects.all().delete()

        self.client.force_authenticate(user=self.user1)

        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment="Test proposal",
            status="pending"
        )

        url = reverse("_proposal-list")
        response = self.client.get(url)

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == proposal.id


    def test_update_proposal_status(self):
        """Тест обновления статуса предложения"""
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment="Test proposal",
            status="pending"
        )
        self.client.force_authenticate(user=self.ad2.user)

        url = reverse("_proposal-status", kwargs={"proposal_id": proposal.id})
        data = {"status": "accepted"}
        
        response = self.client.put(url, data)
        print(response.data)
        print(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, "accepted")
