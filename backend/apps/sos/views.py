from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import EmergencyIncident, EmergencyResponder, EmergencyLog
from .serializers import EmergencyIncidentSerializer

class EmergencyIncidentViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyIncidentSerializer
    permission_classes = [AllowAny] # Changed to AllowAny for MVP testing

    def get_queryset(self):
        user = self.request.user
        if user.role in ['PILGRIM']:
            return EmergencyIncident.objects.filter(user=user)
        return EmergencyIncident.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated:
            from users.models import User
            user = User.objects.first() # Fallback for MVP testing
            
        incident = serializer.save(user=user)
        EmergencyLog.objects.create(
            incident=incident,
            action="SOS request created",
            performed_by=user
        )
        # Broadcast to WebSocket
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'sos_alerts',
            {
                'type': 'sos_alert',
                'message': {
                    'id': str(incident.id),
                    'incident_type': incident.incident_type,
                    'severity': incident.severity,
                    'latitude': str(incident.latitude),
                    'longitude': str(incident.longitude),
                }
            }
        )

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        incident = self.get_object()
        eta = request.data.get('eta_minutes', None)
        
        responder = EmergencyResponder.objects.create(
            incident=incident,
            responder=request.user,
            responder_type=request.user.role,
            eta_minutes=eta
        )
        incident.status = 'Responder_Assigned'
        incident.save()
        
        EmergencyLog.objects.create(
            incident=incident,
            action=f"Incident accepted by {request.user.role}",
            performed_by=request.user
        )
        return Response({"message": "Incident accepted successfully", "eta": eta}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        incident = self.get_object()
        incident.status = 'Closed'
        incident.save()
        
        EmergencyLog.objects.create(
            incident=incident,
            action="Incident closed",
            performed_by=request.user
        )
        return Response({"message": "Incident closed successfully"}, status=status.HTTP_200_OK)
