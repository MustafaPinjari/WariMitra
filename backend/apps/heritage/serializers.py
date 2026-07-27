from rest_framework import serializers
from .models import Saint, Abhang, PilgrimageMilestone

class AbhangSerializer(serializers.ModelSerializer):
    saint_name = serializers.CharField(source='saint.name', read_only=True)
    class Meta:
        model = Abhang
        fields = '__all__'

class SaintSerializer(serializers.ModelSerializer):
    abhangs = AbhangSerializer(many=True, read_only=True)
    class Meta:
        model = Saint
        fields = '__all__'

class PilgrimageMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = PilgrimageMilestone
        fields = '__all__'
