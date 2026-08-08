"""Medical URLs"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicalCampViewSet, PatientViewSet

app_name = 'medical'

router = DefaultRouter()
router.register(r'camps', MedicalCampViewSet, basename='camp')
router.register(r'patients', PatientViewSet, basename='patient')

urlpatterns = [
    path('', include(router.urls)),
]
