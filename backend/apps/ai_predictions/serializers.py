from rest_framework import serializers
from .models import QueuePrediction, CrowdForecast, RiskScore

class QueuePredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueuePrediction
        fields = '__all__'

class CrowdForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrowdForecast
        fields = '__all__'

class RiskScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskScore
        fields = '__all__'
