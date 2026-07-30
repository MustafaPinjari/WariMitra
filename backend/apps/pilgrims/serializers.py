from rest_framework import serializers
from .models import PilgrimProfile, FamilyGroup, EmergencyContact, LiveLocation


class PilgrimProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PilgrimProfile
        fields = '__all__'


class FamilyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyGroup
        fields = '__all__'


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = '__all__'


class LiveLocationSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LiveLocation
        fields = ['user', 'username', 'full_name', 'latitude', 'longitude', 'updated_at', 'battery_level']
        read_only_fields = ['user', 'username', 'full_name', 'updated_at']

    def get_username(self, obj):
        return obj.user.username

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class UpdateLocationSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    battery_level = serializers.IntegerField(required=False, min_value=0, max_value=100)
