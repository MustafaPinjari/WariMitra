import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:fluttertoast/fluttertoast.dart';

/// Central API service. All screens use this for HTTP calls.
/// Base URL uses 10.0.2.2 for Android emulator (maps to localhost).
class ApiService {
  // Uses host PC LAN IP (10.220.49.3) for physical Android devices, 127.0.0.1 for desktop/web
  static String get _baseUrl {
    if (Platform.isAndroid) {
      return 'http://10.220.49.3:8000/api/v1';
    }
    return 'http://127.0.0.1:8000/api/v1';
  }
  static const _storage = FlutterSecureStorage();

  static Dio? _dio;

  /// Call this after logout to clear the cached Dio instance (removes stale tokens).
  static void resetDio() {
    _dio = null;
  }

  static Dio get dio {
    if (_dio != null) return _dio!;

    _dio = Dio(BaseOptions(
      baseUrl: _baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 15),
      headers: {'Content-Type': 'application/json'},
    ));

    // Add token interceptor
    _dio!.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: 'access_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        // Auto-refresh on 401
        if (error.response?.statusCode == 401) {
          final refreshed = await _tryRefreshToken();
          if (refreshed) {
            // Retry original request with new token
            final token = await _storage.read(key: 'access_token');
            error.requestOptions.headers['Authorization'] = 'Bearer $token';
            try {
              final response = await _dio!.fetch(error.requestOptions);
              handler.resolve(response);
              return;
            } catch (_) {}
          }
        }
        
        // Show global toast for any API error
        final errorMsg = errorMessage(error);
        Fluttertoast.showToast(
          msg: "API Error: $errorMsg",
          backgroundColor: Colors.red,
          textColor: Colors.white,
          toastLength: Toast.LENGTH_LONG,
          gravity: ToastGravity.BOTTOM,
        );
        
        handler.next(error);
      },
    ));

    return _dio!;
  }

  static Future<bool> _tryRefreshToken() async {
    try {
      final refresh = await _storage.read(key: 'refresh_token');
      if (refresh == null) return false;

      final response = await Dio().post(
        '$_baseUrl/auth/refresh/',
        data: {'refresh': refresh},
      );
      final newAccess = response.data['access'];
      await _storage.write(key: 'access_token', value: newAccess);
      return true;
    } catch (_) {
      return false;
    }
  }

  /// Convenience method: returns a user-friendly error message from DioException
  static String errorMessage(Object e) {
    if (e is DioException) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        return 'Connection timeout. Check internet connection.';
      }
      if (e.type == DioExceptionType.connectionError) {
        return 'Cannot reach server. Check your network.';
      }
      final data = e.response?.data;
      if (data is Map) {
        // Extract first error message from DRF response
        for (final val in data.values) {
          if (val is List && val.isNotEmpty) return val.first.toString();
          if (val is String) return val;
        }
        return data['detail']?.toString() ?? 'Server error ${e.response?.statusCode}';
      }
      return 'Error ${e.response?.statusCode ?? 'unknown'}';
    }
    return e.toString();
  }
}
