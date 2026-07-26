from rest_framework import serializers
from .models import PilgrimProfile, FamilyGroup, EmergencyContact

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
