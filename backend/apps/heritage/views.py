from rest_framework import viewsets
from .models import Saint, Abhang, PilgrimageMilestone
from .serializers import SaintSerializer, AbhangSerializer, PilgrimageMilestoneSerializer

class SaintViewSet(viewsets.ModelViewSet):
    queryset = Saint.objects.all()
    serializer_class = SaintSerializer

class AbhangViewSet(viewsets.ModelViewSet):
    queryset = Abhang.objects.all()
    serializer_class = AbhangSerializer

class PilgrimageMilestoneViewSet(viewsets.ModelViewSet):
    queryset = PilgrimageMilestone.objects.all()
    serializer_class = PilgrimageMilestoneSerializer
