from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

Player = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'name', 'email', 'unique_code', 'organization', 'location')
        read_only_fields = ('id', 'unique_code')

    def create(self, validated_data):
        player = Player.objects.create_user(**validated_data)
        return player


class CodeLoginSerializer(serializers.Serializer):
    unique_code = serializers.CharField(max_length=12)

    def validate_unique_code(self, value: str) -> str:
        if not Player.objects.filter(unique_code=value.upper(), is_active=True).exists():
            raise serializers.ValidationError('Invalid or inactive code supplied.')
        return value.upper()

    def save(self, **kwargs):
        unique_code = self.validated_data['unique_code']
        return Player.objects.get(unique_code=unique_code)


class PlayerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'name', 'email', 'unique_code', 'organization', 'location', 'is_staff', 'created_at')
        read_only_fields = fields


class LoginResponseSerializer(serializers.Serializer):
    """Serializer for login response documentation in Swagger"""
    access = serializers.CharField(help_text="JWT access token for authentication")
    refresh = serializers.CharField(help_text="JWT refresh token for obtaining new access tokens")
    player = PlayerProfileSerializer(help_text="Authenticated player profile information")
