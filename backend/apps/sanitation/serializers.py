from rest_framework import serializers
from .models import PublicToilet, WasteReport

class PublicToiletSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicToilet
        fields = '__all__'

class WasteReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteReport
        fields = '__all__'
