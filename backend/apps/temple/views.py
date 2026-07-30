from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import TempleQueue, DarshanSlot, QueueMovement
from .serializers import TempleQueueSerializer, DarshanSlotSerializer, QueueMovementSerializer


class TempleQueueViewSet(viewsets.ModelViewSet):
    queryset = TempleQueue.objects.all()
    serializer_class = TempleQueueSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]


class DarshanSlotViewSet(viewsets.ModelViewSet):
    queryset = DarshanSlot.objects.all().order_by('start_time')
    serializer_class = DarshanSlotSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def book_slot(self, request, pk=None):
        """Book a darshan slot for the authenticated user."""
        slot = self.get_object()
        if slot.occupied >= slot.capacity:
            return Response({'error': 'This slot is full.'}, status=status.HTTP_400_BAD_REQUEST)
        if slot.status == 'Full':
            return Response({'error': 'Slot is no longer available.'}, status=status.HTTP_400_BAD_REQUEST)

        slot.occupied += 1
        if slot.occupied >= slot.capacity:
            slot.status = 'Full'
        slot.save()

        import random
        token_number = f"WM-{random.randint(1000, 9999)}"
        return Response({
            'token': token_number,
            'slot_start': slot.start_time,
            'slot_end': slot.end_time,
            'message': 'Darshan slot booked successfully!',
        })


class QueueMovementViewSet(viewsets.ModelViewSet):
    queryset = QueueMovement.objects.all()
    serializer_class = QueueMovementSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
