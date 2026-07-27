from rest_framework import viewsets
from .models import PublicToilet, WasteReport
from .serializers import PublicToiletSerializer, WasteReportSerializer

class PublicToiletViewSet(viewsets.ModelViewSet):
    queryset = PublicToilet.objects.all()
    serializer_class = PublicToiletSerializer

class WasteReportViewSet(viewsets.ModelViewSet):
    queryset = WasteReport.objects.all().order_by('-created_at')
    serializer_class = WasteReportSerializer
