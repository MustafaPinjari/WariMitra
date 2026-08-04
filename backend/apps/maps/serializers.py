from rest_framework import serializers
from .models import ServicePoint

class ServicePointSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = ServicePoint
        fields = [
            'id',
            'name',
            'category',
            'details',
            'latitude',
            'longitude',
            'address',
            'contact_number',
            'status',
            'capacity_info',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        user = self.context['request'].user
        if user and user.is_authenticated:
            validated_data['created_by'] = user
        return super().create(validated_data)
