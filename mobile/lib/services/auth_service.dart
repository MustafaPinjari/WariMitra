import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'api_service.dart';

class AuthService {
  static const _storage = FlutterSecureStorage();

  /// Login with username + password. Returns user data map on success.
  /// Throws String error message on failure.
  static Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await ApiService.dio.post(
        '/auth/login/',
        data: {'username': username, 'password': password},
      );

      final access = response.data['access'] as String;
      final refresh = response.data['refresh'] as String;

      await _storage.write(key: 'access_token', value: access);
      await _storage.write(key: 'refresh_token', value: refresh);

      // Store user info
      final user = response.data['user'] as Map<String, dynamic>? ?? {};
      await _storage.write(key: 'user_role', value: user['role']?.toString() ?? 'PILGRIM');
      await _storage.write(key: 'username', value: user['username']?.toString() ?? username);
      await _storage.write(key: 'user_id', value: user['id']?.toString() ?? '');

      return user;
    } catch (e) {
      throw ApiService.errorMessage(e);
    }
  }

  /// Register new user account. Returns user data map on success.
  /// Throws String error message on failure.
  static Future<Map<String, dynamic>> register(Map<String, dynamic> data) async {
    try {
      final response = await ApiService.dio.post(
        '/auth/register/',
        data: data,
      );

      final access = response.data['access'] as String;
      final refresh = response.data['refresh'] as String;

      await _storage.write(key: 'access_token', value: access);
      await _storage.write(key: 'refresh_token', value: refresh);

      // Store user info
      final user = response.data['user'] as Map<String, dynamic>? ?? {};
      await _storage.write(key: 'user_role', value: user['role']?.toString() ?? 'PILGRIM');
      await _storage.write(key: 'username', value: user['username']?.toString() ?? data['username']?.toString() ?? '');
      await _storage.write(key: 'user_id', value: user['id']?.toString() ?? '');

      return user;
    } catch (e) {
      throw ApiService.errorMessage(e);
    }
  }

  static Future<void> logout() async {
    await _storage.deleteAll();
    ApiService.resetDio(); // Reset dio so interceptor clears
  }

  static Future<bool> isLoggedIn() async {
    final token = await _storage.read(key: 'access_token');
    return token != null;
  }

  static Future<String> getRole() async {
    return await _storage.read(key: 'user_role') ?? 'PILGRIM';
  }

  static Future<String> getUsername() async {
    return await _storage.read(key: 'username') ?? '';
  }
}
