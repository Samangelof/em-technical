# em/apps/ads/models.py  
"""Models"""
# ------------------------------------------------
# Модели кусаются только при неправильных миграциях
# ------------------------------------------------
from django.db import models
from django.contrib.auth.models import User


class Ad(models.Model):
    NEW = 'new'
    USED = 'used'
    CONDITION_CHOICES = [
        (NEW, 'Новый'),
        (USED, 'Б/У'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор объявления")
    title = models.CharField(max_length=255, verbose_name="Заголовок объявления")
    description = models.TextField(verbose_name="Описание товара")
    image_url = models.URLField(blank=True, null=True, verbose_name="URL изображения")
    category = models.CharField(max_length=255, verbose_name="Категория товара")
    condition = models.CharField(
        max_length=4,
        choices=CONDITION_CHOICES,
        default=USED,
        verbose_name="Состояние товара"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"


class ExchangeProposal(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Ожидает'),
        (ACCEPTED, 'Принято'),
        (REJECTED, 'Отклонено'),
    ]

    id = models.AutoField(primary_key=True)
    ad_sender = models.ForeignKey(Ad, related_name='sent_proposals', on_delete=models.CASCADE, verbose_name="Отправитель объявления")
    ad_receiver = models.ForeignKey(Ad, related_name='received_proposals', on_delete=models.CASCADE, verbose_name="Получатель объявления")
    comment = models.TextField(verbose_name="Комментарий")
    status = models.CharField(
        max_length=8,
        choices=STATUS_CHOICES,
        default=PENDING,
        verbose_name="Статус предложения"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Предложение от {self.ad_sender.title} к {self.ad_receiver.title} - {self.status}"

    class Meta:
        verbose_name = "Предложение обмена"
        verbose_name_plural = "Предложения обмена"
