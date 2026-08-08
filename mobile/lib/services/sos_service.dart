import 'package:dio/dio.dart';
import 'package:geolocator/geolocator.dart';
import 'package:warimitra/services/device_fingerprint_service.dart';

/// Service for handling SOS (Safety On Scene) requests
///
/// This service manages the creation and submission of SOS alerts to the backend,
/// including device fingerprinting for DDoS protection and per-device rate limiting.
///
/// **Usage:**
/// ```dart
/// final sosService = SOSService(dio: dioInstance);
/// final response = await sosService.sendSOS(
///   latitude: 28.6139,
///   longitude: 77.2090,
///   radius: 100,
/// );
/// ```
class SOSService {
  /// Base URL for SOS API endpoint
  static const String _baseUrl = '/api/v1/sos/create/';

  /// The Dio HTTP client instance
  final Dio _dio;

  /// Device fingerprint service for generating unique device identifiers
  final DeviceFingerprintService _fingerprintService;

  /// Constructor
  ///
  /// **Parameters:**
  /// - `dio`: HTTP client instance (required)
  /// - `fingerprintService`: Device fingerprint service (optional, creates default if not provided)
  SOSService({
    required Dio dio,
    DeviceFingerprintService? fingerprintService,
  })  : _dio = dio,
        _fingerprintService = fingerprintService ?? DeviceFingerprintService();

  /// Sends an SOS alert to the backend
  ///
  /// Creates and submits an SOS request with the device's current location and
  /// a unique device fingerprint for per-device rate limiting on the backend.
  ///
  /// **Parameters:**
  /// - `latitude`: Device's current latitude (required)
  /// - `longitude`: Device's current longitude (required)
  /// - `radius`: Accuracy radius in meters (default: 100)
  ///
  /// **Returns:**
  /// A map containing the API response data with alert ID and status.
  ///
  /// **Throws:**
  /// - [SOSException] if SOS submission fails
  /// - [FingerprintException] if fingerprint generation fails
  ///
  /// **Example:**
  /// ```dart
  /// try {
  ///   final response = await sosService.sendSOS(
  ///     latitude: 28.6139,
  ///     longitude: 77.2090,
  ///     radius: 100,
  ///   );
  ///   print('SOS sent with alert ID: ${response['id']}');
  /// } on SOSException catch (e) {
  ///   print('SOS failed: ${e.message}');
  /// }
  /// ```
  Future<Map<String, dynamic>> sendSOS({
    required double latitude,
    required double longitude,
    int radius = 100,
  }) async {
    try {
      // Generate device fingerprint
      final deviceFingerprint = await _fingerprintService.getFingerprint();

      // Prepare request body
      final requestBody = {
        'latitude': latitude,
        'longitude': longitude,
        'radius': radius,
        'device_fingerprint': deviceFingerprint,
      };

      // Send POST request to backend
      final response = await _dio.post(
        _baseUrl,
        data: requestBody,
      );

      // Handle successful response
      if (response.statusCode == 201) {
        return response.data as Map<String, dynamic>;
      }

      // Handle error responses
      throw SOSException(
        'Unexpected response code: ${response.statusCode}',
        statusCode: response.statusCode,
      );
    } on FingerprintException {
      rethrow;
    } on DioException catch (e) {
      throw SOSException(
        _parseErrorMessage(e),
        statusCode: e.response?.statusCode,
        originalException: e,
      );
    } catch (e) {
      throw SOSException(
        'Failed to send SOS: $e',
        originalException: e,
      );
    }
  }

  /// Parses error message from DioException
  ///
  /// Extracts the most relevant error information from the exception
  /// to provide meaningful error messages to the user.
  ///
  /// **Parameters:**
  /// - `exception`: The DioException to parse
  ///
  /// **Returns:**
  /// A human-readable error message
  String _parseErrorMessage(DioException exception) {
    if (exception.response != null) {
      final statusCode = exception.response!.statusCode;

      // Handle rate limiting
      if (statusCode == 429) {
        final data = exception.response!.data;
        if (data is Map && data.containsKey('message')) {
          return data['message'] as String;
        }
        return 'Too many SOS requests. Please wait before trying again.';
      }

      // Handle validation errors
      if (statusCode == 400) {
        final data = exception.response!.data;
        if (data is Map && data.containsKey('message')) {
          return data['message'] as String;
        }
        return 'Invalid SOS request. Please check your location and try again.';
      }

      // Handle server errors
      if (statusCode! >= 500) {
        return 'Server error. Please try again later.';
      }

      return 'SOS request failed: $statusCode';
    }

    // Handle network errors
    if (exception.type == DioExceptionType.connectionTimeout) {
      return 'Connection timeout. Please check your network connection.';
    }

    if (exception.type == DioExceptionType.receiveTimeout) {
      return 'Request timeout. Please try again.';
    }

    return 'Network error: ${exception.message}';
  }

  /// Gets the stored device fingerprint without triggering a new SOS
  ///
  /// Useful for debugging or displaying device information to the user.
  ///
  /// **Returns:**
  /// The device fingerprint (64-character hex string)
  ///
  /// **Throws:**
  /// - [FingerprintException] if fingerprint retrieval fails
  ///
  /// **Example:**
  /// ```dart
  /// final fingerprint = await sosService.getDeviceFingerprint();
  /// print('Device fingerprint: $fingerprint');
  /// ```
  Future<String> getDeviceFingerprint() async {
    return _fingerprintService.getFingerprint();
  }
}

/// Exception thrown when SOS submission fails
class SOSException implements Exception {
  /// Human-readable error message
  final String message;

  /// HTTP status code (if applicable)
  final int? statusCode;

  /// Original exception (if available)
  final Exception? originalException;

  /// Constructor
  SOSException(
    this.message, {
    this.statusCode,
    this.originalException,
  });

  @override
  String toString() {
    if (statusCode != null) {
      return 'SOSException ($statusCode): $message';
    }
    return 'SOSException: $message';
  }
}
