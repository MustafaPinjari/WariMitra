import Foundation
import UIKit
import Security

/// Swift implementation for device fingerprinting on iOS
/// 
/// This file handles communication between the Dart code and native iOS APIs.
/// It provides methods to:
/// 1. Get IDFV (Identifier for Vendor) from UIDevice
/// 2. Store the fingerprint securely in Keychain
/// 3. Retrieve the fingerprint from Keychain
/// 4. Clear the fingerprint from Keychain
/// 
/// The platform channel name is: `com.warimitra.device_fingerprint/channel`

class DeviceFingerprintChannel {
    /// Keychain service identifier
    static let keychainService = "com.warimitra.device_fingerprint"
    
    /// Keychain account identifier
    static let keychainAccount = "device_fingerprint"
    
    /// Gets the IDFV (Identifier for Vendor) from the device
    /// 
    /// - Returns: The IDFV string, or "unknown" if unavailable
    /// - Note: IDFV is vendor-scoped and survives app uninstall/reinstall
    static func getIDFV() -> String {
        if let idfv = UIDevice.current.identifierForVendor?.uuidString {
            return idfv
        }
        return "unknown"
    }
    
    /// Gets the device model (e.g., "iPhone13,1")
    /// 
    /// - Returns: The device model identifier
    static func getDeviceModel() -> String {
        var systemInfo = utsname()
        uname(&systemInfo)
        let machineMirror = Mirror(reflecting: systemInfo.machine)
        let identifier = machineMirror.children.reduce("") { identifier, element in
            guard let value = element.value as? Int8, value != 0 else { return identifier }
            return identifier + String(UnicodeScalar(UInt8(value)))
        }
        return identifier
    }
    
    /// Gets the system version (e.g., "17.2")
    /// 
    /// - Returns: The iOS system version
    static func getSystemVersion() -> String {
        return UIDevice.current.systemVersion
    }
    
    /// Stores the fingerprint in iOS Keychain
    /// 
    /// - Parameters:
    ///   - fingerprint: The 64-character hex string to store
    /// - Returns: `true` if storage succeeded, `false` otherwise
    /// - Note: Keychain data is encrypted and vendor-scoped
    static func storeFingerprint(_ fingerprint: String) -> Bool {
        guard let data = fingerprint.data(using: .utf8) else {
            return false
        }
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: keychainAccount,
            kSecValueData as String: data,
        ]
        
        // Delete existing fingerprint first
        SecItemDelete(query as CFDictionary)
        
        // Add new fingerprint
        let status = SecItemAdd(query as CFDictionary, nil)
        return status == errSecSuccess
    }
    
    /// Retrieves the fingerprint from iOS Keychain
    /// 
    /// - Returns: The stored fingerprint, or nil if not found
    static func getFingerprint() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: keychainAccount,
            kSecReturnData as String: true,
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        guard status == errSecSuccess,
              let data = result as? Data,
              let fingerprint = String(data: data, encoding: .utf8) else {
            return nil
        }
        
        return fingerprint
    }
    
    /// Clears the fingerprint from iOS Keychain
    /// 
    /// - Returns: `true` if deletion succeeded, `false` otherwise
    static func clearFingerprint() -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: keychainAccount,
        ]
        
        let status = SecItemDelete(query as CFDictionary)
        return status == errSecSuccess || status == errSecItemNotFound
    }
}

/// Extension to GeneratedPluginRegistrant to handle platform channel calls
/// 
/// This should be added to the GeneratedPluginRegistrant or manually
/// configured in the ViewController.swift
/// 
/// Example setup in main.swift or ViewController.swift:
/// ```swift
/// let controller = self.window?.rootViewController as! FlutterViewController
/// let deviceFingerprintChannel = FlutterMethodChannel(
///     name: "com.warimitra.device_fingerprint/channel",
///     binaryMessenger: controller.binaryMessenger
/// )
/// 
/// deviceFingerprintChannel.setMethodCallHandler { (call: FlutterMethodCall, result: @escaping FlutterResult) in
///     switch call.method {
///     case "getIDFV":
///         result(DeviceFingerprintChannel.getIDFV())
///     case "getFingerprint":
///         result(DeviceFingerprintChannel.getFingerprint())
///     case "storeFingerprint":
///         if let args = call.arguments as? [String: Any],
///            let fingerprint = args["fingerprint"] as? String {
///             let success = DeviceFingerprintChannel.storeFingerprint(fingerprint)
///             result(success)
///         } else {
///             result(FlutterError(code: "INVALID_ARGS", message: "Missing fingerprint argument", details: nil))
///         }
///     case "clearFingerprint":
///         let success = DeviceFingerprintChannel.clearFingerprint()
///         result(success)
///     default:
///         result(FlutterMethodNotImplemented)
///     }
/// }
/// ```
