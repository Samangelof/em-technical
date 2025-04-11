from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Ad, ExchangeProposal


class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'condition', 'created_at')
    list_filter = ('category', 'condition', 'created_at', 'user')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    actions = ['mark_as_used', 'mark_as_new']

    def mark_as_used(self, request, queryset):
        queryset.update(condition=Ad.USED)
    mark_as_used.short_description = _('Отметить как б/у')

    def mark_as_new(self, request, queryset):
        queryset.update(condition=Ad.NEW)
    mark_as_new.short_description = _('Отметить как новый')

# Модель для предложения обмена
class ExchangeProposalAdmin(admin.ModelAdmin):
    list_display = ('ad_sender', 'ad_receiver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('ad_sender__title', 'ad_receiver__title', 'comment')
    ordering = ('-created_at',)
    actions = ['accept_proposals', 'reject_proposals']

    def accept_proposals(self, request, queryset):
        queryset.update(status=ExchangeProposal.ACCEPTED) 
    accept_proposals.short_description = _('Принять выбранные предложения')

    def reject_proposals(self, request, queryset):
        queryset.update(status=ExchangeProposal.REJECTED)
    reject_proposals.short_description = _('Отклонить выбранные предложения')


admin.site.register(Ad, AdAdmin)
admin.site.register(ExchangeProposal, ExchangeProposalAdmin)
