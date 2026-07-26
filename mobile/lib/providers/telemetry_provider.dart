import 'package:flutter_riverpod/flutter_riverpod.dart';

class LiveTelemetryState {
  final double latitude;
  final double longitude;
  final String activeEmergencyStatus;
  final bool isSosTriggered;

  const LiveTelemetryState({
    required this.latitude,
    required this.longitude,
    required this.activeEmergencyStatus,
    required this.isSosTriggered,
  });

  LiveTelemetryState copyWith({
    double? latitude,
    double? longitude,
    String? activeEmergencyStatus,
    bool? isSosTriggered,
  }) {
    return LiveTelemetryState(
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      activeEmergencyStatus: activeEmergencyStatus ?? this.activeEmergencyStatus,
      isSosTriggered: isSosTriggered ?? this.isSosTriggered,
    );
  }
}

class TelemetryNotifier extends StateNotifier<LiveTelemetryState> {
  TelemetryNotifier()
      : super(const LiveTelemetryState(
          latitude: 18.3444,
          longitude: 74.0305,
          activeEmergencyStatus: 'Normal',
          isSosTriggered: false,
        ));

  void updateGPS(double lat, double lng) {
    state = state.copyWith(latitude: lat, longitude: lng);
  }

  void triggerSos() {
    state = state.copyWith(isSosTriggered: true, activeEmergencyStatus: 'CRITICAL_DISPATCH');
  }

  void cancelSos() {
    state = state.copyWith(isSosTriggered: false, activeEmergencyStatus: 'Normal');
  }
}

final telemetryProvider = StateNotifierProvider<TelemetryNotifier, LiveTelemetryState>((ref) {
  return TelemetryNotifier();
});
