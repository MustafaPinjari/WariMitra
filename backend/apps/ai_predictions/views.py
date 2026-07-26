from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import QueuePrediction, CrowdForecast, RiskScore
from .serializers import QueuePredictionSerializer, CrowdForecastSerializer, RiskScoreSerializer

class QueuePredictionViewSet(viewsets.ModelViewSet):
    queryset = QueuePrediction.objects.all()
    serializer_class = QueuePredictionSerializer
    permission_classes = [IsAuthenticated]

class CrowdForecastViewSet(viewsets.ModelViewSet):
    queryset = CrowdForecast.objects.all()
    serializer_class = CrowdForecastSerializer
    permission_classes = [IsAuthenticated]

class RiskScoreViewSet(viewsets.ModelViewSet):
    queryset = RiskScore.objects.all()
    serializer_class = RiskScoreSerializer
    permission_classes = [IsAuthenticated]
