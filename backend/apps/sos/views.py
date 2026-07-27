from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import EmergencyIncident, EmergencyResponder, EmergencyLog
from .serializers import EmergencyIncidentSerializer

class EmergencyIncidentViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyIncidentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        if user and user.is_authenticated and getattr(user, 'role', '') == 'PILGRIM':
            return EmergencyIncident.objects.filter(user=user)
        return EmergencyIncident.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if not user or not user.is_authenticated:
            from apps.users.models import User
            user = User.objects.first()
            
        incident = serializer.save(user=user)
        EmergencyLog.objects.create(
            incident=incident,
            action="SOS request created",
            performed_by=user
        )
        # Broadcast to WebSocket if layer is present
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    'sos_alerts',
                    {
                        'type': 'sos_alert',
                        'message': {
                            'id': str(incident.id),
                            'incident_type': getattr(incident, 'incident_type', 'SOS'),
                            'severity': getattr(incident, 'priority', 'High'),
                            'latitude': str(incident.latitude),
                            'longitude': str(incident.longitude),
                        }
                    }
                )
        except Exception:
            pass

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        incident = self.get_object()
        eta = request.data.get('eta_minutes', None)
        user = request.user if request.user and request.user.is_authenticated else None
        
        EmergencyResponder.objects.create(
            incident=incident,
            responder=user,
            responder_type=getattr(user, 'role', 'VOLUNTEER') if user else 'VOLUNTEER',
            eta_minutes=eta
        )
        incident.status = 'Responder_Assigned'
        incident.save()
        
        if user:
            EmergencyLog.objects.create(
                incident=incident,
                action=f"Incident accepted by {getattr(user, 'role', 'Responder')}",
                performed_by=user
            )
        return Response({"message": "Incident accepted successfully", "eta": eta}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        incident = self.get_object()
        incident.status = 'Closed'
        incident.save()
        
        user = request.user if request.user and request.user.is_authenticated else None
        if user:
            EmergencyLog.objects.create(
                incident=incident,
                action="Incident closed",
                performed_by=user
            )
        return Response({"message": "Incident closed successfully"}, status=status.HTTP_200_OK)
