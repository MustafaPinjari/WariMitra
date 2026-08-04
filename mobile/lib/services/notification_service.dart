import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotificationService {
  static final FlutterLocalNotificationsPlugin _notificationsPlugin =
      FlutterLocalNotificationsPlugin();

  static const int _locationNotificationId = 888;
  static bool _isInitialized = false;

  /// Initializes the local notification plugin for Android.
  static Future<void> init() async {
    if (_isInitialized) return;
    try {
      const AndroidInitializationSettings initializationSettingsAndroid =
          AndroidInitializationSettings('@mipmap/ic_launcher');

      const InitializationSettings initializationSettings = InitializationSettings(
        android: initializationSettingsAndroid,
      );

      await _notificationsPlugin.initialize(
        settings: initializationSettings,
      );

      // Request notification permission for Android 13+ (API level 33+)
      await _notificationsPlugin
          .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
          ?.requestNotificationsPermission();

      _isInitialized = true;
    } catch (_) {}
  }

  /// Displays a persistent/ongoing app notification in the status bar when location sharing is active.
  static Future<void> showLocationSharingNotification({
    String title = '📍 Live Location Sharing Active',
    String body = 'Your GPS position is being shared live with your WariMitra family group.',
  }) async {
    await init();
    try {
      const AndroidNotificationDetails androidDetails = AndroidNotificationDetails(
        'location_sharing_channel_v2',
        'Live Location Sharing Notifications',
        channelDescription: 'Ongoing notification while live GPS sharing is active',
        importance: Importance.high,
        priority: Priority.high,
        ongoing: true,
        autoCancel: false,
        showWhen: true,
        icon: '@mipmap/ic_launcher',
      );

      const NotificationDetails notificationDetails =
          NotificationDetails(android: androidDetails);

      await _notificationsPlugin.show(
        id: _locationNotificationId,
        title: title,
        body: body,
        notificationDetails: notificationDetails,
      );
    } catch (_) {}
  }

  /// Cancels/removes the location sharing notification when auto-share is turned OFF.
  static Future<void> cancelLocationSharingNotification() async {
    try {
      await _notificationsPlugin.cancel(id: _locationNotificationId);
    } catch (_) {}
  }
}
