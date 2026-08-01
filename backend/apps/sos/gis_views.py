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
        lat_param = request.query_params.get('lat')
        lng_param = request.query_params.get('lng')

        if not lat_param or not lng_param:
            return Response(
                {'error': 'Missing required location parameters: lat and lng'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lat = float(lat_param)
            lng = float(lng_param)
            radius_km = float(request.query_params.get('radius_km', 5.0))
        except (ValueError, TypeError):
            return Response({'error': 'Invalid lat, lng or radius_km parameters'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Nearby Ambulances
        ambulances = Ambulance.objects.exclude(current_latitude__isnull=True).exclude(current_longitude__isnull=True)
        nearby_ambulances = []
        for amb in ambulances:
            amb_lat = float(amb.current_latitude)
            amb_lng = float(amb.current_longitude)
            dist = haversine_distance(lat, lng, amb_lat, amb_lng)
            if dist <= radius_km:
                nearby_ambulances.append({
                    'id': amb.id,
                    'vehicle_number': amb.vehicle_number,
                    'status': amb.status,
                    'latitude': amb_lat,
                    'longitude': amb_lng,
                    'distance_km': round(dist, 2),
                    'eta_mins': max(1, int(dist * 2)),
                })

        # Sort by distance
        nearby_ambulances.sort(key=lambda x: x['distance_km'])

        # 2. Nearby Police Patrol Units
        patrols = PatrolUnit.objects.exclude(current_latitude__isnull=True).exclude(current_longitude__isnull=True)
        nearby_patrols = []
        for p in patrols:
            p_lat = float(p.current_latitude)
            p_lng = float(p.current_longitude)
            dist = haversine_distance(lat, lng, p_lat, p_lng)
            if dist <= radius_km:
                nearby_patrols.append({
                    'id': p.id,
                    'badge_number': p.unit_number,
                    'status': p.status,
                    'latitude': p_lat,
                    'longitude': p_lng,
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
