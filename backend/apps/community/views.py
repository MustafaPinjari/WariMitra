from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CommunityReport, ReportVerification, ReporterTrust
from .serializers import CommunityReportSerializer, ReportVerificationSerializer

class CommunityReportViewSet(viewsets.ModelViewSet):
    serializer_class = CommunityReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CommunityReport.objects.all()

    def perform_create(self, serializer):
        # AI Logic to assign confidence_score would go here
        serializer.save(reporter=self.request.user)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        report = self.get_object()
        is_valid = request.data.get('is_valid', True)
        remarks = request.data.get('remarks', '')
        
        ReportVerification.objects.create(
            report=report,
            verifier=request.user,
            verifier_role=request.user.role,
            is_valid=is_valid,
            remarks=remarks
        )
        
        # Simple trust score adjustment
        if is_valid:
            report.confidence_score = min(report.confidence_score + 10, 100)
            if report.confidence_score >= 80:
                report.verification_status = 'Verified'
        else:
            report.confidence_score = max(report.confidence_score - 20, 0)
            if report.confidence_score <= 20:
                report.verification_status = 'False Report'
                report.status = 'Closed'
                
        report.save()
        return Response({"message": "Verification submitted", "new_confidence_score": report.confidence_score}, status=status.HTTP_200_OK)
