from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import PoliceStation, PatrolUnit, RoadBlock
from .serializers import PoliceStationSerializer, PatrolUnitSerializer, RoadBlockSerializer

class PoliceStationViewSet(viewsets.ModelViewSet):
    queryset = PoliceStation.objects.all()
    serializer_class = PoliceStationSerializer
    permission_classes = [IsAuthenticated]

class PatrolUnitViewSet(viewsets.ModelViewSet):
    queryset = PatrolUnit.objects.all()
    serializer_class = PatrolUnitSerializer
    permission_classes = [IsAuthenticated]

class RoadBlockViewSet(viewsets.ModelViewSet):
    queryset = RoadBlock.objects.all()
    serializer_class = RoadBlockSerializer
    permission_classes = [IsAuthenticated]
