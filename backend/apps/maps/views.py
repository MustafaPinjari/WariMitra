import math
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import ServicePoint
from .serializers import ServicePointSerializer

class ServicePointViewSet(viewsets.ModelViewSet):
    queryset = ServicePoint.objects.all()
    serializer_class = ServicePointSerializer
    permission_classes = [permissions.AllowAny] # Allow viewing and adding points for all users
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['name', 'details', 'address']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        queryset = super().get_queryset()
        lat_param = self.request.query_params.get('lat')
        lng_param = self.request.query_params.get('lng')

        if lat_param and lng_param:
            try:
                user_lat = float(lat_param)
                user_lng = float(lng_param)
                
                # Sort in-memory by distance (Haversine)
                def calc_distance(sp):
                    p = 0.017453292519943295
                    a = 0.5 - math.cos((sp.latitude - user_lat) * p)/2 + \
                        math.cos(user_lat * p) * math.cos(sp.latitude * p) * (1 - math.cos((sp.longitude - user_lng) * p))/2
                    return 12742 * math.asin(math.sqrt(a))
                
                points = list(queryset)
                points.sort(key=calc_distance)
                return points
            except ValueError:
                pass

        return queryset
