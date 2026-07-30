from rest_framework import serializers
from .models import MissingPersonReport


class MissingPersonReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MissingPersonReport
        fields = [
            'id', 'name', 'age', 'category', 'description',
            'photo_url', 'last_seen_location', 'latitude', 'longitude',
            'status', 'contact_mobile', 'reporter_name', 'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'reporter_name']

    def get_reporter_name(self, obj):
        if obj.reporter:
            return obj.reporter.get_full_name() or obj.reporter.username
        return 'Anonymous'
