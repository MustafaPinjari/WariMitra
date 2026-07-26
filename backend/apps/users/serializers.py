from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'role', 'first_name', 'last_name', 'email', 'is_verified')
        read_only_fields = ('id', 'role', 'is_verified')
