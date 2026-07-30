from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import LostFoundItem
from .serializers import LostFoundItemSerializer


class LostFoundItemViewSet(viewsets.ModelViewSet):
    queryset = LostFoundItem.objects.all().order_by('-created_at')
    serializer_class = LostFoundItemSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [AllowAny()]
        return [IsAuthenticated()]
