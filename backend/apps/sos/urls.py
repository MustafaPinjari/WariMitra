from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmergencyIncidentViewSet

router = DefaultRouter()
router.register(r'', EmergencyIncidentViewSet, basename='sos')

urlpatterns = [
    path('', include(router.urls)),
]
