from rest_framework import serializers
from .models import Resource, Inventory, Distribution, Donation

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'

class DistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribution
        fields = '__all__'

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = '__all__'
