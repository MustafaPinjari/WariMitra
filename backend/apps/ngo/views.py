from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Resource, Inventory, Distribution, Donation
from .serializers import ResourceSerializer, InventorySerializer, DistributionSerializer, DonationSerializer

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

class DistributionViewSet(viewsets.ModelViewSet):
    queryset = Distribution.objects.all()
    serializer_class = DistributionSerializer
    permission_classes = [IsAuthenticated]

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]
