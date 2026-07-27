from rest_framework import viewsets
from .models import LostFoundItem
from .serializers import LostFoundItemSerializer

class LostFoundItemViewSet(viewsets.ModelViewSet):
    queryset = LostFoundItem.objects.all().order_by('-created_at')
    serializer_class = LostFoundItemSerializer
