from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import QueuePrediction, CrowdForecast, RiskScore
from .serializers import QueuePredictionSerializer, CrowdForecastSerializer, RiskScoreSerializer
from .services import (
    predict_crowd_surge,
    calculate_queue_wait_time,
    predict_heatstroke_risk,
    calculate_reporter_trust
)

class QueuePredictionViewSet(viewsets.ModelViewSet):
    queryset = QueuePrediction.objects.all()
    serializer_class = QueuePredictionSerializer
    permission_classes = [AllowAny]

class CrowdForecastViewSet(viewsets.ModelViewSet):
    queryset = CrowdForecast.objects.all()
    serializer_class = CrowdForecastSerializer
    permission_classes = [AllowAny]

class RiskScoreViewSet(viewsets.ModelViewSet):
    queryset = RiskScore.objects.all()
    serializer_class = RiskScoreSerializer
    permission_classes = [AllowAny]

# ─────────────────────────────────────────────────────────────────────────────
# Real-Time AI & Mathematical API Views
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def crowd_surge_prediction_api(request):
    density = float(request.query_params.get('density', request.data.get('density', 3.2)))
    flow_rate = float(request.query_params.get('flow_rate', request.data.get('flow_rate', 1.5)))
    weather_factor = float(request.query_params.get('weather_factor', request.data.get('weather_factor', 1.0)))
    
    result = predict_crowd_surge(density, flow_rate, weather_factor)
    return Response(result, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def queue_wait_time_api(request):
    queue_count = int(request.query_params.get('queue_count', request.data.get('queue_count', 3200)))
    entry_rate = float(request.query_params.get('entry_rate', request.data.get('entry_rate', 15.0)))
    active_gates = int(request.query_params.get('active_gates', request.data.get('active_gates', 4)))
    
    result = calculate_queue_wait_time(queue_count, entry_rate, active_gates=active_gates)
    return Response(result, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def heatstroke_risk_api(request):
    temp = float(request.query_params.get('temp', request.data.get('temp', 36.5)))
    humidity = float(request.query_params.get('humidity', request.data.get('humidity', 68.0)))
    age = int(request.query_params.get('age', request.data.get('age', 55)))
    distance = float(request.query_params.get('distance', request.data.get('distance', 14.0)))
    
    result = predict_heatstroke_risk(temp, humidity, age, distance)
    return Response(result, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def reporter_trust_score_api(request):
    total = int(request.query_params.get('total', request.data.get('total', 10)))
    verified = int(request.query_params.get('verified', request.data.get('verified', 8)))
    false_rep = int(request.query_params.get('false_rep', request.data.get('false_rep', 1)))
    is_volunteer = request.query_params.get('is_volunteer', 'false').lower() == 'true'
    
    result = calculate_reporter_trust(total, verified, false_rep, is_volunteer)
    return Response(result, status=status.HTTP_200_OK)
