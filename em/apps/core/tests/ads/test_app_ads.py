from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from core.models import Ad, ExchangeProposal


class AdViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_create_ad_view(self):
        """Тестируем создание объявления"""
        url = reverse('create_ad')
        data = {
            'title': 'Test Ad',
            'description': 'Description of test ad',
            'category': 'Test Category',
            'condition': 'new',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ad.objects.filter(title='Test Ad').exists())

    def test_create_ad_unauthenticated(self):
        """Тестируем создание объявления для неавторизованного пользователя"""
        self.client.logout()
        url = reverse('create_ad')
        expected_redirect = f"{settings.LOGIN_URL}?next={url}"
        response = self.client.get(url)
        self.assertRedirects(response, expected_redirect)

    def test_edit_ad_view(self):
        """Тестируем редактирование объявления"""
        ad = Ad.objects.create(user=self.user, title='Old Title', description='Old description', category='Test', condition='used')
        url = reverse('edit_ad', args=[ad.id])
        data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'category': 'Updated Category',
            'condition': 'new',
        }
        response = self.client.post(url, data)
        ad.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ad.title, 'Updated Title')

    def test_edit_ad_permission(self):
        """Тестируем права доступа при редактировании объявления"""
        another_user = User.objects.create_user(username='anotheruser', password='password')
        ad = Ad.objects.create(user=self.user, title='Title', description='Description', category='Category', condition='used')
        url = reverse('edit_ad', args=[ad.id])
        self.client.login(username='anotheruser', password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_delete_ad_view(self):
        """Тестируем удаление объявления"""
        ad = Ad.objects.create(user=self.user, title='Test Ad', description='Description', category='Test', condition='used')
        url = reverse('delete_ad', args=[ad.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ad.objects.filter(id=ad.id).exists())

    def test_delete_ad_permission(self):
        """Тестируем права доступа при удалении объявления"""
        another_user = User.objects.create_user(username='anotheruser', password='password')
        ad = Ad.objects.create(user=self.user, title='Test Ad', description='Description', category='Test', condition='used')
        url = reverse('delete_ad', args=[ad.id])
        self.client.login(username='anotheruser', password='password')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_create_exchange_proposal(self):
        """Тестируем создание предложения обмена"""
        logged_in = self.client.login(username=self.user.username, password='password')
        self.assertTrue(logged_in, "Не удалось залогиниться")
        receiver_user = User.objects.create_user(username='receiver', password='password')
        ad_sender = Ad.objects.create(user=self.user, title='Sender Ad', description='Sender Description', category='Test', condition='used')
        ad_receiver = Ad.objects.create(user=receiver_user, title='Receiver Ad', description='Receiver Description', category='Test', condition='new')
        url = reverse('create_exchange_proposal', args=[ad_receiver.id])
        data = {
            'ad_receiver': ad_receiver.id,
            'comment': 'I want to exchange!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


    def test_create_exchange_proposal_to_self(self):
        """Тестируем запрет предложения обмена самому себе"""
        ad_sender = Ad.objects.create(user=self.user, title='Sender Ad', description='Sender Description', category='Test', condition='used')
        url = reverse('create_exchange_proposal', args=[ad_sender.id])
        data = {
            'ad_receiver': ad_sender.id,
            'comment': 'I want to exchange!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)

    def test_update_exchange_proposal_status(self):
        """Тестируем изменение статуса предложения обмена"""
        ad_sender = Ad.objects.create(user=self.user, title='Sender Ad', description='Sender Description', category='Test', condition='used')
        ad_receiver = User.objects.create_user(username='receiver', password='password')
        ad_receiver_ad = Ad.objects.create(user=ad_receiver, title='Receiver Ad', description='Receiver Description', category='Test', condition='new')
        
        proposal = ExchangeProposal.objects.create(ad_sender=ad_sender, ad_receiver=ad_receiver_ad, status=ExchangeProposal.PENDING, comment='Test')
        self.client.login(username='receiver', password='password')
        url = reverse('update_exchange_proposal_status', args=[proposal.id, ExchangeProposal.ACCEPTED])
        response = self.client.post(url)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, ExchangeProposal.ACCEPTED)