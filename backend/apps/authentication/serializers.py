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
