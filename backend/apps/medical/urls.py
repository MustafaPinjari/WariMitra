from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HospitalViewSet, MedicalCampViewSet, AmbulanceViewSet, MedicalCaseViewSet

router = DefaultRouter()
router.register(r'hospitals', HospitalViewSet)
router.register(r'camps', MedicalCampViewSet)
router.register(r'ambulances', AmbulanceViewSet)
router.register(r'cases', MedicalCaseViewSet, basename='medical-case')

urlpatterns = [
    path('', include(router.urls)),
]
