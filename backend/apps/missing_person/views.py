from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import MissingPersonReport
from .serializers import MissingPersonReportSerializer


class MissingPersonReportViewSet(viewsets.ModelViewSet):
    serializer_class = MissingPersonReportSerializer

    def get_permissions(self):
        # Anyone can create or list; only auth users can update/delete
        if self.action in ['create', 'list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return MissingPersonReport.objects.filter(
            status='Searching'
        ).order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(reporter=user)
