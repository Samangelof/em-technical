# em/apps/ads/services.py
"""Бизнес-Логика"""
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
#! (см. apps/core/models.py)
from core.models import Ad, ExchangeProposal


class AdService:
    @staticmethod
    def create_ad(user: User, title: str, description: str, image_url: str, category: str, condition: str) -> Ad:
        ad = Ad.objects.create(
            user=user,
            title=title,
            description=description,
            image_url=image_url,
            category=category,
            condition=condition,
        )
        return ad

    @staticmethod
    def update_ad(ad: Ad, title: str, description: str, image_url: str, category: str, condition: str) -> Ad:
        ad.title = title
        ad.description = description
        ad.image_url = image_url
        ad.category = category
        ad.condition = condition
        ad.save()
        return ad

    @staticmethod
    def delete_ad(ad: Ad) -> None:
        ad.delete()

    @staticmethod
    def search_ads(query: str, category: str = None, condition: str = None):
        ads = Ad.objects.filter(Q(title__icontains=query)
                                | Q(description__icontains=query))
        if category:
            ads = ads.filter(category=category)
        if condition:
            ads = ads.filter(condition=condition)
        return ads


class ExchangeProposalService:
    @staticmethod
    def create_proposal(ad_sender: Ad, ad_receiver: Ad, comment: str = "") -> ExchangeProposal:
        if ad_sender.user == ad_receiver.user:
            raise ValidationError("Нельзя предложить обмен самому себе")

        if ExchangeProposal.objects.filter(ad_sender=ad_sender, ad_receiver=ad_receiver).exists():
            raise ValidationError("Вы уже предложили этот обмен")

        if ExchangeProposal.objects.filter(ad_sender=ad_sender, ad_receiver=ad_receiver, status='pending').exists():
            raise ValidationError("Предложение уже существует")
        
        return ExchangeProposal.objects.create(
            ad_sender=ad_sender,
            ad_receiver=ad_receiver,
            comment=comment,
            status='pending'
        )

    @staticmethod
    def update_proposal_status(proposal: ExchangeProposal, status: str, user: User) -> ExchangeProposal:
        if proposal.ad_receiver.user != user:
            raise PermissionDenied("Вы не можете изменить статус этого предложения.")
        proposal.status = status
        proposal.save()
        return proposal

    @staticmethod
    def filter_by_status(user: User, status: str):
        return ExchangeProposal.objects.filter(
            status=status
        ).filter(Q(ad_sender__user=user) | Q(ad_receiver__user=user))