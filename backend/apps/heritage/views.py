from rest_framework import viewsets, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Saint, Abhang, PilgrimageMilestone
from .serializers import SaintSerializer, AbhangSerializer, PilgrimageMilestoneSerializer
from .s3_service import upload_file_to_s3

class SaintViewSet(viewsets.ModelViewSet):
    queryset = Saint.objects.all().order_by('name')
    serializer_class = SaintSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'marathi_name', 'biography']

class AbhangViewSet(viewsets.ModelViewSet):
    queryset = Abhang.objects.all().select_related('saint').order_by('-created_at', 'id')
    serializer_class = AbhangSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['saint', 'category']
    search_fields = ['title', 'marathi_title', 'lyrics', 'artist']
    ordering_fields = ['created_at', 'title']

class PilgrimageMilestoneViewSet(viewsets.ModelViewSet):
    queryset = PilgrimageMilestone.objects.all().order_by('day_number')
    serializer_class = PilgrimageMilestoneSerializer
    permission_classes = [permissions.AllowAny]

class HeritageAudioUploadView(APIView):
    """
    API View to upload audio files or saint images to AWS S3 storage.
    If AWS credentials are missing or fail, automatically falls back to Django local storage.
    Returns: JSON response with the file URL.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided in request'}, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.FILES['file']
        folder = request.data.get('folder', 'heritage/audio')
        
        try:
            file_url = upload_file_to_s3(file_obj, folder=folder)
            
            # Make sure relative media URLs have the request domain prefix for app compatibility
            if file_url.startswith('/'):
                file_url = request.build_absolute_uri(file_url)

            return Response({
                'message': 'File uploaded successfully',
                'url': file_url,
                'filename': file_obj.name
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Failed to upload file: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
