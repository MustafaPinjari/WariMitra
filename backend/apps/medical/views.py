"""Medical views - Phase 1.4: Object-level RBAC will be applied here"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import MedicalCamp, Patient
from .serializers import MedicalCampSerializer, PatientSerializer


class MedicalCampViewSet(viewsets.ModelViewSet):
    """Medical camp viewset - Phase 1.4: Add camp boundary check"""
    queryset = MedicalCamp.objects.filter(is_active=True)
    serializer_class = MedicalCampSerializer
    permission_classes = [IsAuthenticated]


class PatientViewSet(viewsets.ModelViewSet):
    """Patient viewset - Phase 1.4: Add camp isolation RBAC"""
    queryset = Patient.objects.filter(is_active=True)
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
