from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import PublicToilet, WasteReport
from .serializers import PublicToiletSerializer, WasteReportSerializer


class PublicToiletViewSet(viewsets.ModelViewSet):
    queryset = PublicToilet.objects.all()
    serializer_class = PublicToiletSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]


class WasteReportViewSet(viewsets.ModelViewSet):
    queryset = WasteReport.objects.all().order_by('-created_at')
    serializer_class = WasteReportSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [AllowAny()]
        return [IsAuthenticated()]
