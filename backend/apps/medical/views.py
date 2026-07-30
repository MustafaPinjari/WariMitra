from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Hospital, MedicalCamp, Ambulance, MedicalCase
from .serializers import HospitalSerializer, MedicalCampSerializer, AmbulanceSerializer, MedicalCaseSerializer


class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]


class MedicalCampViewSet(viewsets.ModelViewSet):
    queryset = MedicalCamp.objects.all()
    serializer_class = MedicalCampSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]


class AmbulanceViewSet(viewsets.ModelViewSet):
    queryset = Ambulance.objects.all()
    serializer_class = AmbulanceSerializer
    permission_classes = [IsAuthenticated]


class MedicalCaseViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalCaseSerializer
    permission_classes = [IsAuthenticated]
    # Needed for drf-spectacular schema generation — avoids AnonymousUser crash
    queryset = MedicalCase.objects.none()

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) in ['MEDICAL_STAFF', 'GOVERNMENT_ADMIN', 'SUPER_ADMIN']:
            return MedicalCase.objects.all()
        return MedicalCase.objects.filter(patient=user)
