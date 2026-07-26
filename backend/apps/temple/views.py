from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import TempleQueue, DarshanSlot, QueueMovement
from .serializers import TempleQueueSerializer, DarshanSlotSerializer, QueueMovementSerializer

class TempleQueueViewSet(viewsets.ModelViewSet):
    queryset = TempleQueue.objects.all()
    serializer_class = TempleQueueSerializer
    permission_classes = [IsAuthenticated]

class DarshanSlotViewSet(viewsets.ModelViewSet):
    queryset = DarshanSlot.objects.all()
    serializer_class = DarshanSlotSerializer
    permission_classes = [IsAuthenticated]

class QueueMovementViewSet(viewsets.ModelViewSet):
    queryset = QueueMovement.objects.all()
    serializer_class = QueueMovementSerializer
    permission_classes = [IsAuthenticated]
