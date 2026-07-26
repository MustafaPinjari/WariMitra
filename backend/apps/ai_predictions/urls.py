from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QueuePredictionViewSet,
    CrowdForecastViewSet,
    RiskScoreViewSet,
    crowd_surge_prediction_api,
    queue_wait_time_api,
    heatstroke_risk_api,
    reporter_trust_score_api,
)

router = DefaultRouter()
router.register(r'queue-predictions', QueuePredictionViewSet)
router.register(r'crowd-forecasts', CrowdForecastViewSet)
router.register(r'risk-scores', RiskScoreViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('crowd-surge/', crowd_surge_prediction_api, name='ai-crowd-surge'),
    path('queue-wait/', queue_wait_time_api, name='ai-queue-wait'),
    path('heatstroke-risk/', heatstroke_risk_api, name='ai-heatstroke-risk'),
    path('reporter-trust/', reporter_trust_score_api, name='ai-reporter-trust'),
]
