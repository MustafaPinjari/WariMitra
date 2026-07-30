import 'package:geolocator/geolocator.dart';
import 'api_service.dart';

class LocationService {
  /// Requests permission and returns current position.
  /// Returns null if permission denied.
  static Future<Position?> getCurrentPosition() async {
    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.deniedForever ||
          permission == LocationPermission.denied) {
        return null;
      }

      return await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          timeLimit: Duration(seconds: 10),
        ),
      );
    } catch (_) {
      return null;
    }
  }

  /// Updates the backend with the user's current location.
  /// Silently fails if location is unavailable.
  static Future<void> updateBackendLocation({int? batteryLevel}) async {
    final pos = await getCurrentPosition();
    if (pos == null) return;
    try {
      await ApiService.dio.post('/pilgrims/update-location/', data: {
        'latitude': pos.latitude,
        'longitude': pos.longitude,
        if (batteryLevel != null) 'battery_level': batteryLevel,
      });
    } catch (_) {
      // Silent fail — location update is best-effort
    }
  }
}
