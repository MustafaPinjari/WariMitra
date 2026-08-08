"""SOS URLs"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SosAlertViewSet

app_name = 'sos'

router = DefaultRouter()
router.register(r'alerts', SosAlertViewSet, basename='alert')

urlpatterns = [
    path('', include(router.urls)),
]
