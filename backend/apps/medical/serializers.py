from rest_framework import serializers
from .models import Hospital, MedicalCamp, Ambulance, MedicalCase

class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'

class MedicalCampSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalCamp
        fields = '__all__'

class AmbulanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambulance
        fields = '__all__'

class MedicalCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalCase
        fields = '__all__'
