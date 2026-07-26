from rest_framework import serializers
from .models import TempleQueue, DarshanSlot, QueueMovement

class TempleQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempleQueue
        fields = '__all__'

class DarshanSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = DarshanSlot
        fields = '__all__'

class QueueMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueueMovement
        fields = '__all__'
