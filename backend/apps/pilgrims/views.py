from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import PilgrimProfile, FamilyGroup, EmergencyContact, LiveLocation
from .serializers import (
    PilgrimProfileSerializer, FamilyGroupSerializer,
    EmergencyContactSerializer, LiveLocationSerializer, UpdateLocationSerializer
)


class PilgrimProfileViewSet(viewsets.ModelViewSet):
    serializer_class = PilgrimProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = PilgrimProfile.objects.none()

    def get_queryset(self):
        return PilgrimProfile.objects.filter(user=self.request.user)


class FamilyGroupViewSet(viewsets.ModelViewSet):
    serializer_class = FamilyGroupSerializer
    permission_classes = [IsAuthenticated]
    queryset = FamilyGroup.objects.none()

    def get_queryset(self):
        return FamilyGroup.objects.filter(members=self.request.user)


class EmergencyContactViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyContactSerializer
    permission_classes = [IsAuthenticated]
    queryset = EmergencyContact.objects.none()

    def get_queryset(self):
        return EmergencyContact.objects.filter(pilgrim=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_location(request):
    """Update or create the caller's live GPS location."""
    serializer = UpdateLocationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    LiveLocation.objects.update_or_create(
        user=request.user,
        defaults={
            'latitude': serializer.validated_data['latitude'],
            'longitude': serializer.validated_data['longitude'],
            'battery_level': serializer.validated_data.get('battery_level'),
        }
    )
    return Response({'status': 'location updated'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def family_locations(request):
    """Return live locations for all members of the user's family groups."""
    # Get all family groups this user belongs to
    groups = FamilyGroup.objects.filter(members=request.user)
    if not groups.exists():
        return Response([])

    # Collect unique member user IDs across all groups
    member_ids = set()
    for group in groups:
        member_ids.update(group.members.values_list('id', flat=True))

    locations = LiveLocation.objects.filter(
        user__id__in=member_ids
    ).select_related('user')

    serializer = LiveLocationSerializer(locations, many=True)
    return Response(serializer.data)
