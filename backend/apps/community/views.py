from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CommunityReport, ReportVerification, ReporterTrust
from .serializers import CommunityReportSerializer, ReportVerificationSerializer


class CommunityReportViewSet(viewsets.ModelViewSet):
    serializer_class = CommunityReportSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return CommunityReport.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(reporter=user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def verify(self, request, pk=None):
        report = self.get_object()
        is_valid = request.data.get('is_valid', True)
        remarks = request.data.get('remarks', '')

        ReportVerification.objects.create(
            report=report,
            verifier=request.user,
            verifier_role=getattr(request.user, 'role', 'PILGRIM'),
            is_valid=is_valid,
            remarks=remarks,
        )

        # Adjust confidence score
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
        return Response({
            'message': 'Verification submitted',
            'new_confidence_score': report.confidence_score,
        }, status=status.HTTP_200_OK)
