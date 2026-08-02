from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import LostFoundItem
from .serializers import LostFoundItemSerializer


class LostFoundItemViewSet(viewsets.ModelViewSet):
    queryset = LostFoundItem.objects.all().order_by('-created_at')
    serializer_class = LostFoundItemSerializer

    def get_permissions(self):
        return [AllowAny()]

    def perform_create(self, serializer):
        import secrets, string
        code = 'WM-LF-' + ''.join(secrets.choice(string.digits) for _ in range(5))
        serializer.save(qr_claim_code=code)

