from rest_framework import serializers
from .models import EmergencyIncident, EmergencyResponder, EmergencyLog

class EmergencyIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyIncident
        fields = '__all__'
        read_only_fields = ('id', 'user', 'status', 'created_at', 'updated_at')

class EmergencyResponderSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyResponder
        fields = '__all__'

class EmergencyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyLog
        fields = '__all__'
