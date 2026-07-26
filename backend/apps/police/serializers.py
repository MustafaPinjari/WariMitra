from rest_framework import serializers
from .models import PoliceStation, PatrolUnit, RoadBlock

class PoliceStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceStation
        fields = '__all__'

class PatrolUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatrolUnit
        fields = '__all__'

class RoadBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadBlock
        fields = '__all__'
