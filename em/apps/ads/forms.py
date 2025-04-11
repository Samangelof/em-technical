# em/apps/ads/forms.py  
"""Forms"""
from django import forms
from core.models import Ad, ExchangeProposal


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['user', 'title', 'description', 'image_url', 'category', 'condition']
        labels = {
            'user': 'Автор объявления',
            'title': 'Заголовок объявления',
            'description': 'Описание товара',
            'image_url': 'URL изображения',
            'category': 'Категория товара',
            'condition': 'Состояние товара',
        }

class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'ad_receiver', 'comment', 'status']
        labels = {
            'ad_sender': 'Отправитель объявления',
            'ad_receiver': 'Получатель объявления',
            'comment': 'Комментарий',
            'status': 'Статус предложения',
        }
