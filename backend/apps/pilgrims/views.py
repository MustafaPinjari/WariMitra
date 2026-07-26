from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import PilgrimProfile, FamilyGroup, EmergencyContact
from .serializers import PilgrimProfileSerializer, FamilyGroupSerializer, EmergencyContactSerializer

class PilgrimProfileViewSet(viewsets.ModelViewSet):
    serializer_class = PilgrimProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PilgrimProfile.objects.filter(user=self.request.user)

class FamilyGroupViewSet(viewsets.ModelViewSet):
    serializer_class = FamilyGroupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FamilyGroup.objects.filter(members=self.request.user)

class EmergencyContactViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyContactSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EmergencyContact.objects.filter(pilgrim=self.request.user)
