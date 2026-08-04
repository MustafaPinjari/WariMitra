import 'dart:async';
import 'package:flutter/services.dart';
import 'package:geolocator/geolocator.dart';
import 'api_service.dart';
import 'notification_service.dart';

class LocationService {
  static const MethodChannel _batteryChannel = MethodChannel('plugins.flutter.io/battery');
  static int _cachedBatteryLevel = 85;

  static bool _isAutoSharing = false;
  static Timer? _globalAutoShareTimer;

  /// Returns whether global live location auto-sharing is currently active
  static bool get isAutoSharing => _isAutoSharing;

  /// Starts persistent global live location sharing across all pages & app minimization
  static void startAutoSharing({Duration interval = const Duration(seconds: 30)}) {
    _isAutoSharing = true;
    _globalAutoShareTimer?.cancel();

    // Trigger immediate initial upload
    updateBackendLocation();
    NotificationService.showLocationSharingNotification();

    // Set global periodic timer that stays active across all screens
    _globalAutoShareTimer = Timer.periodic(interval, (_) {
      if (_isAutoSharing) {
        updateBackendLocation();
      }
    });
  }

  /// Stops global live location sharing
  static void stopAutoSharing() {
    _isAutoSharing = false;
    _globalAutoShareTimer?.cancel();
    _globalAutoShareTimer = null;
    NotificationService.cancelLocationSharingNotification();
  }

  /// Toggles global live location sharing state
  static void toggleAutoSharing(bool enable) {
    if (enable) {
      startAutoSharing();
    } else {
      stopAutoSharing();
    }
  }

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
