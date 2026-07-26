from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QueuePredictionViewSet, CrowdForecastViewSet, RiskScoreViewSet

router = DefaultRouter()
router.register(r'queue-predictions', QueuePredictionViewSet)
router.register(r'crowd-forecasts', CrowdForecastViewSet)
router.register(r'risk-scores', RiskScoreViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
