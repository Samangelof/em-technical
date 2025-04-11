# em/apps/ads/serializers.py
"""Serializers"""
from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import Ad, ExchangeProposal


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        return user
    
class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ['id', 'user', 'title', 'description', 'image_url', 'category', 'condition', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_image_url(self, value):
        if value and not value.startswith('http'):
            raise serializers.ValidationError("URL изображения должен начинаться с 'http'.")
        return value


class ExchangeProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeProposal
        fields = ['id', 'ad_sender', 'ad_receiver', 'comment', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_status(self, value):
        if value not in ['ожидает', 'принята', 'отклонена']:
            raise serializers.ValidationError("Неверный статус. Допустимые значения: 'ожидает', 'принята', 'отклонена'.")
        return value