import 'dart:async';
import 'dart:io';
import 'dart:typed_data';
import 'package:crypto/crypto.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Device Fingerprinting Service for Android and iOS
///
/// Generates a unique, stable device fingerprint using platform-specific identifiers:
/// - **Android:** ANDROID_ID, Build.FINGERPRINT, Build.MODEL
/// - **iOS:** IDFV (Identifier for Vendor), device model, system version
/// 
/// Components are combined and hashed using SHA256 to produce a 64-character hex string.
/// 
/// The fingerprint is stored securely in:
/// - **Android:** EncryptedSharedPreferences
/// - **iOS:** iOS Keychain (via platform channel)
/// 
/// The fingerprint persists across app restarts and survives uninstall/reinstall on iOS
/// (IDFV is vendor-scoped), but will regenerate on Android if secure storage is cleared.
///
/// **Fingerprint Format:** 64-character hexadecimal string (SHA256 hash)
///
/// **Usage:**
/// ```dart
/// final service = DeviceFingerprintService();
/// final fingerprint = await service.getFingerprint();
/// ```
class DeviceFingerprintService {
  /// Storage key for device fingerprint
  static const String _fingerprintStorageKey = 'device_fingerprint';

  /// Platform channel for native iOS operations
  static const platform =
      MethodChannel('com.warimitra.device_fingerprint/channel');

  /// The secure storage instance
  final FlutterSecureStorage _secureStorage;

  /// DeviceInfo plugin instance
  final DeviceInfoPlugin _deviceInfo;

  /// Cache for the fingerprint to avoid repeated storage reads
  String? _cachedFingerprint;

  /// Constructor
  DeviceFingerprintService({
    FlutterSecureStorage? secureStorage,
    DeviceInfoPlugin? deviceInfo,
  })  : _secureStorage = secureStorage ?? const FlutterSecureStorage(),
        _deviceInfo = deviceInfo ?? DeviceInfoPlugin();

  /// Gets the device fingerprint, generating and storing it if necessary.
  ///
  /// The fingerprint is generated once and cached. Subsequent calls will return
  /// the stored fingerprint from secure storage without regeneration.
  ///
  /// **Platform-specific behavior:**
  /// - **Android:** Uses EncryptedSharedPreferences for secure storage
  /// - **iOS:** Uses Keychain for secure storage (vendor-scoped, survives uninstall/reinstall)
  ///
  /// **Returns:**
  /// A 64-character hexadecimal string representing the device fingerprint.
  ///
  /// **Throws:**
  /// - [FingerprintException] if fingerprint generation fails.
  /// - [FingerprintStorageException] if secure storage operations fail.
  ///
  /// **Example:**
  /// ```dart
  /// try {
  ///   final fingerprint = await service.getFingerprint();
  ///   print('Device fingerprint: $fingerprint');
  /// } catch (e) {
  ///   print('Failed to get fingerprint: $e');
  /// }
  /// ```
  Future<String> getFingerprint() async {
    // Return cached fingerprint if available
    if (_cachedFingerprint != null) {
      return _cachedFingerprint!;
    }

    try {
      // Try to retrieve existing fingerprint from secure storage
      String? storedFingerprint;
      
      if (Platform.isIOS) {
        storedFingerprint = await _getFromKeychain();
      } else if (Platform.isAndroid) {
        storedFingerprint =
            await _secureStorage.read(key: _fingerprintStorageKey);
      }

      if (storedFingerprint != null && storedFingerprint.isNotEmpty) {
        _cachedFingerprint = storedFingerprint;
        return storedFingerprint;
      }

      // Generate new fingerprint
      final newFingerprint = await _generateFingerprint();

      // Store it securely
      if (Platform.isIOS) {
        await _storeInKeychain(newFingerprint);
      } else if (Platform.isAndroid) {
        await _secureStorage.write(
          key: _fingerprintStorageKey,
          value: newFingerprint,
        );
      }

      _cachedFingerprint = newFingerprint;
      return newFingerprint;
    } on FingerprintStorageException {
      rethrow;
    } on FingerprintException {
      rethrow;
    } catch (e) {
      throw FingerprintStorageException(
        'Failed to read/write device fingerprint: $e',
      );
    }
  }

  /// Generates a new device fingerprint from device identifiers.
  ///
  /// **Android components:**
  /// 1. ANDROID_ID (device-specific identifier)
  /// 2. Build.FINGERPRINT (build-specific identifier)
  /// 3. Build.MODEL (device model)
  ///
  /// **iOS components:**
  /// 1. IDFV (Identifier for Vendor) - vendor-scoped, survives uninstall/reinstall
  /// 2. Device model (e.g., "iPhone13,1")
  /// 3. System version (e.g., "17.2")
  ///
  /// Components are concatenated and hashed using SHA256 to produce
  /// a 64-character hexadecimal string.
  ///
  /// **Returns:**
  /// A 64-character hexadecimal SHA256 hash.
  ///
  /// **Throws:**
  /// - [FingerprintException] if device info retrieval fails.
  ///
  /// **Note:**
  /// This is an internal method. Use [getFingerprint] to get the persisted fingerprint.
  Future<String> _generateFingerprint() async {
    try {
      String components = '';

      if (Platform.isAndroid) {
        // Android fingerprinting
        final androidInfo = await _deviceInfo.androidInfo;

        // Extract fingerprint components
        final androidId = androidInfo.id; // ANDROID_ID
        final buildFingerprint = androidInfo.fingerprint; // Build.FINGERPRINT
        final model = androidInfo.model; // Build.MODEL

        // Validate that we have the required components
        if (androidId.isEmpty) {
          throw FingerprintException(
            'Failed to retrieve ANDROID_ID from device',
          );
        }

        components = '$androidId:$buildFingerprint:$model';
      } else if (Platform.isIOS) {
        // iOS fingerprinting via platform channel
        try {
          final idfv =
              await platform.invokeMethod<String>('getIDFV') ?? 'unknown';
          final iosInfo = await _deviceInfo.iosInfo;
          final model = iosInfo.model;
          final systemVersion = iosInfo.systemVersion;

          if (idfv == 'unknown' || idfv.isEmpty) {
            throw FingerprintException(
              'Failed to retrieve IDFV (Identifier for Vendor) from device',
            );
          }

          components = '$idfv:$model:$systemVersion';
        } on PlatformException catch (e) {
          throw FingerprintException(
            'Platform error retrieving IDFV: ${e.message}',
          );
        }
      } else {
        throw FingerprintException(
          'Unsupported platform for device fingerprinting',
        );
      }

      // Hash with SHA256 to get 64-char hex string
      final hash = sha256.convert(components.codeUnits);
      final hashHex = hash.toString();

      // Validate format (SHA256 produces 64-char hex string)
      if (hashHex.length != 64) {
        throw FingerprintException(
          'Invalid fingerprint format: expected 64 chars, got ${hashHex.length}',
        );
      }

      return hashHex;
    } catch (e) {
      if (e is FingerprintException) {
        rethrow;
      }
      throw FingerprintException(
        'Failed to generate device fingerprint: $e',
      );
    }
  }

  /// Retrieves the fingerprint from iOS Keychain via platform channel.
  ///
  /// **Returns:**
  /// The stored fingerprint string, or null if not found.
  ///
  /// **Throws:**
  /// - [FingerprintStorageException] if Keychain access fails.
  ///
  /// **Note:**
  /// iOS Keychain is vendor-scoped, so the fingerprint survives app uninstall/reinstall.
  Future<String?> _getFromKeychain() async {
    try {
      final fingerprint =
          await platform.invokeMethod<String>('getFingerprint');
      return fingerprint;
    } on PlatformException catch (e) {
      throw FingerprintStorageException(
        'Failed to retrieve fingerprint from Keychain: ${e.message}',
      );
    } catch (e) {
      throw FingerprintStorageException(
        'Failed to access iOS Keychain: $e',
      );
    }
  }

  /// Stores the fingerprint in iOS Keychain via platform channel.
  ///
  /// **Parameters:**
  /// - `fingerprint`: The 64-character hex string to store
  ///
  /// **Throws:**
  /// - [FingerprintStorageException] if Keychain write fails.
  ///
  /// **Note:**
  /// iOS Keychain stores data in an encrypted, vendor-scoped manner.
  /// The fingerprint will persist across app uninstall/reinstall.
  Future<void> _storeInKeychain(String fingerprint) async {
    try {
      await platform.invokeMethod<void>(
        'storeFingerprint',
        {'fingerprint': fingerprint},
      );
    } on PlatformException catch (e) {
      throw FingerprintStorageException(
        'Failed to store fingerprint in Keychain: ${e.message}',
      );
    } catch (e) {
      throw FingerprintStorageException(
        'Failed to access iOS Keychain: $e',
      );
    }
  }

  /// Clears the fingerprint from iOS Keychain via platform channel.
  ///
  /// **Throws:**
  /// - [FingerprintStorageException] if Keychain delete fails.
  ///
  /// **Note:**
  /// This is intended for testing purposes only.
  Future<void> _clearFromKeychain() async {
    try {
      await platform.invokeMethod<void>('clearFingerprint');
    } on PlatformException catch (e) {
      throw FingerprintStorageException(
        'Failed to clear fingerprint from Keychain: ${e.message}',
      );
    } catch (e) {
      throw FingerprintStorageException(
        'Failed to access iOS Keychain: $e',
      );
    }
  }

  /// Clears the cached fingerprint and resets secure storage.
  ///
  /// This method is primarily used for testing. In production, the fingerprint
  /// should persist across app restarts.
  ///
  /// **Platform-specific behavior:**
  /// - **Android:** Clears from EncryptedSharedPreferences
  /// - **iOS:** Clears from Keychain
  ///
  /// **Throws:**
  /// - [FingerprintStorageException] if secure storage operation fails.
  ///
  /// **Note:**
  /// This is intended for testing purposes only.
  Future<void> clearFingerprint() async {
    try {
      _cachedFingerprint = null;
      if (Platform.isIOS) {
        await _clearFromKeychain();
      } else if (Platform.isAndroid) {
        await _secureStorage.delete(key: _fingerprintStorageKey);
      }
    } catch (e) {
      if (e is FingerprintStorageException) {
        rethrow;
      }
      throw FingerprintStorageException(
        'Failed to clear fingerprint: $e',
      );
    }
  }

  /// Validates that a fingerprint string is in the correct format.
  ///
  /// **Validation Rules:**
  /// - Must be exactly 64 characters
  /// - Must be a valid hexadecimal string (0-9, a-f)
  ///
  /// **Returns:**
  /// `true` if the fingerprint is valid, `false` otherwise.
  ///
  /// **Example:**
  /// ```dart
  /// final valid = service.validateFingerprintFormat(
  ///   'a' * 64,  // Valid: 64 hex chars
  /// );
  /// assert(valid == true);
  /// ```
  static bool validateFingerprintFormat(String fingerprint) {
    // Must be exactly 64 characters
    if (fingerprint.length != 64) {
      return false;
    }

    // Must be valid hexadecimal (0-9, a-f, A-F)
    return RegExp(r'^[a-fA-F0-9]{64}$').hasMatch(fingerprint);
  }
}

/// Exception thrown when fingerprint generation fails.
class FingerprintException implements Exception {
  /// Error message describing the failure
  final String message;

  /// Constructor
  FingerprintException(this.message);

  @override
  String toString() => 'FingerprintException: $message';
}

/// Exception thrown when secure storage operations fail.
class FingerprintStorageException implements Exception {
  /// Error message describing the storage failure
  final String message;

  /// Constructor
  FingerprintStorageException(this.message);

  @override
  String toString() => 'FingerprintStorageException: $message';
}
