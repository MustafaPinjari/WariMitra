from rest_framework import serializers
from .models import Saint, Abhang, PilgrimageMilestone

class AbhangSerializer(serializers.ModelSerializer):
    saint_name = serializers.CharField(source='saint.name', read_only=True, default='')
    saint_marathi_name = serializers.CharField(source='saint.marathi_name', read_only=True, default='')
    saint_image_url = serializers.CharField(source='saint.image_url', read_only=True, default='')

    class Meta:
        model = Abhang
        fields = [
            'id', 'saint', 'saint_name', 'saint_marathi_name', 'saint_image_url',
            'title', 'marathi_title', 'artist', 'category', 'lyrics',
            'translation', 'audio_url', 'duration', 'created_at', 'updated_at'
        ]

class SaintSerializer(serializers.ModelSerializer):
    abhang_count = serializers.SerializerMethodField()

    class Meta:
        model = Saint
        fields = ['id', 'name', 'marathi_name', 'title', 'era', 'biography', 'image_url', 'abhang_count']

    def get_abhang_count(self, obj):
        return obj.abhangs.count()

class PilgrimageMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = PilgrimageMilestone
        fields = '__all__'
