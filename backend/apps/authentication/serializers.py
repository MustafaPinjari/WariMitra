from rest_framework import serializers

class OTPRequestSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)

class OTPVerifySerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)
    
class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.DictField()

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    mobile = serializers.CharField(max_length=15)
    password = serializers.CharField(min_length=6, write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    email = serializers.EmailField(required=False, allow_blank=True, default='')
    role = serializers.CharField(default='PILGRIM')

