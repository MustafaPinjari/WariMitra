"""Medical serializers"""
from rest_framework import serializers
from .models import MedicalCamp, Patient


class MedicalCampSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalCamp
        fields = ['id', 'name', 'latitude', 'longitude', 'capacity', 'current_patients']
        read_only_fields = ['id']


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'medical_camp', 'first_name', 'last_name', 'age', 'condition', 'created_at']
        read_only_fields = ['id', 'created_at']
