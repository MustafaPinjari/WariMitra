from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Hospital, MedicalCamp, Ambulance, MedicalCase
from .serializers import HospitalSerializer, MedicalCampSerializer, AmbulanceSerializer, MedicalCaseSerializer

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [IsAuthenticated]

class MedicalCampViewSet(viewsets.ModelViewSet):
    queryset = MedicalCamp.objects.all()
    serializer_class = MedicalCampSerializer
    permission_classes = [IsAuthenticated]

class AmbulanceViewSet(viewsets.ModelViewSet):
    queryset = Ambulance.objects.all()
    serializer_class = AmbulanceSerializer
    permission_classes = [IsAuthenticated]

class MedicalCaseViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalCaseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['MEDICAL_STAFF', 'GOVERNMENT_ADMIN', 'SUPER_ADMIN']:
            return MedicalCase.objects.all()
        return MedicalCase.objects.filter(patient=user)
