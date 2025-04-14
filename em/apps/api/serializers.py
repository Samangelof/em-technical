# em/apps/ads/serializers.py
"""Serializers"""
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from core.models import Ad, ExchangeProposal


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())])

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
    

class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class AdSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # На всякий случай, лишним не будет
    condition = serializers.ChoiceField(
        choices=Ad.CONDITION_CHOICES,
        help_text="Допустимые значения: new (новое), used (б/у)"
    )
    # Запрет на запись, как удобнее
    # user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Ad
        fields = ['id', 'user', 'title', 'description', 'image_url', 'category', 'condition', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_image_url(self, value):
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("URL изображения должен начинаться с 'http://' или 'https://'")
        return value



class ProposalSerializer(serializers.ModelSerializer):
    ad_receiver = serializers.PrimaryKeyRelatedField(
        queryset=Ad.objects.all(),
        write_only=True,
        pk_field=serializers.IntegerField()  
    )
    comment = serializers.CharField(required=True) 
    
    class Meta:
        model = ExchangeProposal
        fields = ['id', 'ad_sender', 'ad_receiver', 'comment', 'status', 'created_at']
        read_only_fields = ['id', 'ad_sender', 'status', 'created_at']
    
    def validate(self, data):
        if data['ad_receiver'].user == self.context['request'].user:
            raise serializers.ValidationError({"ad_receiver": "Нельзя предложить обмен самому себе"})
        return data
    
    
class ExchangeProposalUpdateStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ExchangeProposal.STATUS_CHOICES)

    def validate_status(self, value):
        if value == ExchangeProposal.PENDING:
            raise serializers.ValidationError("Нельзя вернуть статус 'ожидает'")
        return value