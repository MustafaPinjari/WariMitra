from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmergencyIncidentViewSet
from .gis_views import NearbyRespondersSpatialAPIView, ViewportIncidentsSpatialAPIView

router = DefaultRouter()
router.register(r'', EmergencyIncidentViewSet, basename='sos')

urlpatterns = [
    path('spatial/nearby-responders/', NearbyRespondersSpatialAPIView.as_view(), name='spatial-nearby-responders'),
    path('spatial/viewport-incidents/', ViewportIncidentsSpatialAPIView.as_view(), name='spatial-viewport-incidents'),
    path('', include(router.urls)),
]
