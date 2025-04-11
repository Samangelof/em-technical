# em/apps/ads/services.py
"""Бизнес-Логика"""
from django.db.models import Q
from django.utils import timezone
#! (см. apps/core/models.py)
from core.models import Ad, ExchangeProposal


class AdService:
    @staticmethod
    def create_ad(user, title, description, image_url, category, condition):
        ad = Ad.objects.create(
            user=user,
            title=title,
            description=description,
            image_url=image_url,
            category=category,
            condition=condition,
            created_at=timezone.now()
        )
        return ad

    @staticmethod
    def update_ad(ad, title, description, image_url, category, condition):
        ad.title = title
        ad.description = description
        ad.image_url = image_url
        ad.category = category
        ad.condition = condition
        ad.save()
        return ad

    @staticmethod
    def delete_ad(ad):
        ad.delete()

    @staticmethod
    def search_ads(query, category=None, condition=None):
        ads = Ad.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        if category:
            ads = ads.filter(category=category)
        if condition:
            ads = ads.filter(condition=condition)
        return ads

class ExchangeProposalService:
    @staticmethod
    def create_proposal(ad_sender, ad_receiver, comment):
        proposal = ExchangeProposal.objects.create(
            ad_sender=ad_sender,
            ad_receiver=ad_receiver,
            comment=comment,
            status='ожидает',
            created_at=timezone.now()
        )
        return proposal

    @staticmethod
    def update_proposal_status(proposal, status):
        proposal.status = status
        proposal.save()
        return proposal

    @staticmethod
    def filter_by_status(status):
        return ExchangeProposal.objects.filter(status=status)
