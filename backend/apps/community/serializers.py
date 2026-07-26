from rest_framework import serializers
from .models import CommunityReport, ReportVerification, ReporterTrust

class CommunityReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityReport
        fields = '__all__'
        read_only_fields = ('id', 'reporter', 'confidence_score', 'verification_status', 'status', 'created_at', 'updated_at')

class ReportVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportVerification
        fields = '__all__'
