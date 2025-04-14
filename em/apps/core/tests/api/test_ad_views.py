# em/apps/ads/tests/test_ads_views.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import Ad


@pytest.mark.django_db
class TestAdViews:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="u1", password="pass")
        self.client.force_authenticate(user=self.user)

    def test_create_ad(self):
        url = reverse("_ad-create")
        payload = {
            "title": "Ad test",
            "description": "test desc",
            "image_url": "http://img.com",
            "category": "books",
            "condition": "used"
        }
        response = self.client.post(url, payload, format="json")
        assert response.status_code == 201
        assert Ad.objects.filter(title="Ad test", user=self.user).exists()

    def test_search_ads(self):
        Ad.objects.create(user=self.user, title="T1", description="d", image_url="http://img", category="cat", condition="new")
        Ad.objects.create(user=self.user, title="T2", description="d", image_url="http://img", category="cat", condition="new")

        url = reverse("_ad-search")
        response = self.client.get(url)

        assert response.status_code == 200
        assert isinstance(response.data["results"], list)  # Обращаемся к 'results'
        assert len(response.data["results"]) == 2  # Проверяем количество элементов

        # Добавляем сортировку
        ads = Ad.objects.all().order_by("id")  # или любое другое поле для сортировки

        # Проверяем порядок
        assert response.data["results"][0]["id"] == ads[0].id
        assert response.data["results"][1]["id"] == ads[1].id


    def test_update_ad(self):
        ad = Ad.objects.create(user=self.user, title="T", description="d", image_url="https://example.com/img", category="cat", condition="new")

        url = reverse("_ad-update", kwargs={"ad_id": ad.id})
        data = {
            "title": "Updated",
            "description": ad.description,
            "image_url": ad.image_url,
            "category": ad.category,
            "condition": ad.condition
        }
        response = self.client.put(url, data, format="json")
        assert response.status_code == 200
        ad.refresh_from_db()
        assert ad.title == "Updated"


    def test_delete_ad(self):
        ad = Ad.objects.create(user=self.user, title="T", description="d", image_url="img", category="cat", condition="new")
        url = reverse("_ad-delete", kwargs={"ad_id": ad.id})
        response = self.client.delete(url)
        assert response.status_code == 204
        assert not Ad.objects.filter(id=ad.id).exists()
