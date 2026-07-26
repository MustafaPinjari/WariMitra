import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth (in kilometers)
    using the Haversine formula (PostGIS spatial distance compatibility layer).
    """
    R = 6371.0  # Earth's radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def is_within_radius(center_lat: float, center_lng: float, target_lat: float, target_lng: float, radius_km: float) -> bool:
    """
    Determine whether a target point falls within radius_km of the center point (PostGIS ST_DWithin simulation).
    """
    return haversine_distance(center_lat, center_lng, target_lat, target_lng) <= radius_km

def get_bounding_box(lat: float, lng: float, radius_km: float):
    """
    Generate min_lat, min_lng, max_lat, max_lng bounding box for spatial index filtering.
    """
    lat_delta = radius_km / 111.0  # 1 degree lat ~ 111 km
    lng_delta = radius_km / (111.0 * math.cos(math.radians(lat)))

    return {
        'min_lat': lat - lat_delta,
        'max_lat': lat + lat_delta,
        'min_lng': lng - lng_delta,
        'max_lng': lng + lng_delta,
    }
