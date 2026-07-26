from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.common.spatial_utils import haversine_distance, is_within_radius
from apps.sos.models import EmergencyIncident
from apps.medical.models import Ambulance
from apps.police.models import PatrolUnit

class NearbyRespondersSpatialAPIView(APIView):
    """
    PostGIS-Ready Spatial API Endpoint:
    Finds nearest police units, ambulances, and medical camps within a given radius_km.
    """
    def get(self, request):
        try:
            lat = float(request.query_params.get('lat', 18.3444))
            lng = float(request.query_params.get('lng', 74.0305))
            radius_km = float(request.query_params.get('radius_km', 5.0))
        except (ValueError, TypeError):
            return Response({'error': 'Invalid lat, lng or radius_km parameters'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Nearby Ambulances
        ambulances = Ambulance.objects.all()
        nearby_ambulances = []
        for amb in ambulances:
            dist = haversine_distance(lat, lng, float(amb.current_latitude or 18.3444), float(amb.current_longitude or 74.0305))
            if dist <= radius_km:
                nearby_ambulances.append({
                    'id': amb.id,
                    'vehicle_number': amb.vehicle_number,
                    'status': amb.status,
                    'latitude': float(amb.current_latitude or 18.3444),
                    'longitude': float(amb.current_longitude or 74.0305),
                    'distance_km': round(dist, 2),
                    'eta_mins': max(1, math.round(dist * 2) if 'math' in globals() else int(dist * 2)),
                })

        # Sort by distance
        nearby_ambulances.sort(key=lambda x: x['distance_km'])

        # 2. Nearby Police Patrol Units
        patrols = PatrolUnit.objects.all()
        nearby_patrols = []
        for p in patrols:
            dist = haversine_distance(lat, lng, float(p.current_latitude or 18.3444), float(p.current_longitude or 74.0305))
            if dist <= radius_km:
                nearby_patrols.append({
                    'id': p.id,
                    'badge_number': p.unit_number,
                    'status': p.status,
                    'latitude': float(p.current_latitude or 18.3444),
                    'longitude': float(p.current_longitude or 74.0305),
                    'distance_km': round(dist, 2),
                })

        nearby_patrols.sort(key=lambda x: x['distance_km'])

        return Response({
            'center': {'lat': lat, 'lng': lng},
            'radius_km': radius_km,
            'nearby_ambulances': nearby_ambulances,
            'nearby_police_units': nearby_patrols,
            'total_responders_count': len(nearby_ambulances) + len(nearby_patrols),
        }, status=status.HTTP_200_OK)


class ViewportIncidentsSpatialAPIView(APIView):
    """
    PostGIS-Ready Bounding Box Spatial API Endpoint:
    Returns active emergency incidents falling inside map viewport (min_lat, min_lng, max_lat, max_lng).
    """
    def get(self, request):
        try:
            min_lat = float(request.query_params.get('min_lat', 17.5))
            min_lng = float(request.query_params.get('min_lng', 73.5))
            max_lat = float(request.query_params.get('max_lat', 19.0))
            max_lng = float(request.query_params.get('max_lng', 76.0))
        except (ValueError, TypeError):
            return Response({'error': 'Invalid bounding box parameters'}, status=status.HTTP_400_BAD_REQUEST)

        incidents = EmergencyIncident.objects.filter(
            latitude__gte=min_lat,
            latitude__lte=max_lat,
            longitude__gte=min_lng,
            longitude__lte=max_lng
        )

        data = [{
            'id': str(inc.id),
            'incident_type': inc.incident_type,
            'status': inc.status,
            'latitude': float(inc.latitude),
            'longitude': float(inc.longitude),
            'description': inc.description,
            'created_at': inc.created_at.isoformat(),
        } for inc in incidents]

        return Response({
            'bounding_box': {'min_lat': min_lat, 'min_lng': min_lng, 'max_lat': max_lat, 'max_lng': max_lng},
            'incidents_count': len(data),
            'incidents': data,
        }, status=status.HTTP_200_OK)
