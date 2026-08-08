"""Serializers for authentication"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number']
        read_only_fields = ['id']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout endpoint"""
    pass


class RevokeTokensSerializer(serializers.Serializer):
    """Serializer for admin token revocation"""
    reason = serializers.ChoiceField(choices=['logout', 'admin_revoke', 'password_reset', 'security_incident', 'device_lost'])
