import 'package:flutter/services.dart';
import 'package:geolocator/geolocator.dart';
import 'api_service.dart';

class LocationService {
  static const MethodChannel _batteryChannel = MethodChannel('plugins.flutter.io/battery');
  static int _cachedBatteryLevel = 85;

  /// Rounds a double coordinate to specified decimal places (default 6).
  static double roundCoordinate(double value, [int places = 6]) {
    return double.parse(value.toStringAsFixed(places));
  }

  /// Gets device battery level (0-100%).
  static Future<int> getBatteryLevel() async {
    try {
      final int? result = await _batteryChannel.invokeMethod<int>('getBatteryLevel');
      if (result != null && result >= 0 && result <= 100) {
        _cachedBatteryLevel = result;
        return result;
      }
    } catch (_) {
      // Channel fallback
    }
    return _cachedBatteryLevel;
  }

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

  /// Updates the backend with the user's current location and battery percentage.
  /// Silently fails if location is unavailable.
  static Future<void> updateBackendLocation({int? batteryLevel}) async {
    final pos = await getCurrentPosition();
    if (pos == null) return;

    final battery = batteryLevel ?? await getBatteryLevel();

    try {
      await ApiService.dio.post('/pilgrims/update-location/', data: {
        'latitude': roundCoordinate(pos.latitude),
        'longitude': roundCoordinate(pos.longitude),
        'battery_level': battery,
      });
    } catch (_) {
      // Silent fail — location update is best-effort
    }
  }
}

