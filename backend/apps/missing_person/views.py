from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import MissingPersonReport
from .serializers import MissingPersonReportSerializer


class MissingPersonReportViewSet(viewsets.ModelViewSet):
    serializer_class = MissingPersonReportSerializer

    def get_permissions(self):
        return [AllowAny()]

    def get_queryset(self):
        return MissingPersonReport.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(reporter=user)

