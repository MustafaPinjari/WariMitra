"""SOS serializers"""
from rest_framework import serializers
from .models import SosAlert, DeviceFingerprint


class SosAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = SosAlert
        fields = ['id', 'user', 'status', 'latitude', 'longitude', 'description', 'severity', 'created_at']
        read_only_fields = ['id', 'created_at']


class DeviceFingerprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceFingerprint
        fields = ['id', 'device_id', 'device_model', 'os_type', 'os_version', 'ip_address']
