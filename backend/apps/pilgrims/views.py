from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
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

    def get_queryset(self):
        return FamilyGroup.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        group = serializer.save(owner=self.request.user)
        group.members.add(self.request.user)

    @action(detail=False, methods=['post'], url_path='join')
    def join_group(self, request):
        invite_code = request.data.get('invite_code', '').strip().upper()
        if not invite_code:
            return Response({'error': 'Invite code is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            group = FamilyGroup.objects.get(invite_code__iexact=invite_code)
        except FamilyGroup.DoesNotExist:
            return Response({'error': 'Invalid invite code. No family group found.'}, status=status.HTTP_404_NOT_FOUND)

        group.members.add(request.user)
        serializer = self.get_serializer(group)
        return Response({
            'message': f'Successfully joined {group.name}!',
            'group': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='leave')
    def leave_group(self, request, pk=None):
        group = self.get_object()
        group.members.remove(request.user)
        return Response({'message': f'Successfully left {group.name}'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='add-member')
    def add_member(self, request, pk=None):
        group = self.get_object()
        identifier = request.data.get('username') or request.data.get('phone') or request.data.get('identifier', '').strip()
        if not identifier:
            return Response({'error': 'Username or phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.users.models import User
        target_user = User.objects.filter(models.Q(username=identifier) | models.Q(phone_number=identifier)).first()
        if not target_user:
            return Response({'error': f'User "{identifier}" not found.'}, status=status.HTTP_404_NOT_FOUND)

        group.members.add(target_user)
        return Response({'message': f'Added {target_user.username} to {group.name}'}, status=status.HTTP_200_OK)


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
