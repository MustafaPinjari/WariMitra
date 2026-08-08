/**
 * Firebase configuration for WariMitra
 * Phase 1.4: Crashlytics will be configured here
 */
import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    return android;
  }

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'YOUR_API_KEY',
    appId: 'YOUR_APP_ID',
    messagingSenderId: 'YOUR_MESSAGING_SENDER_ID',
    projectId: 'warimitra-project',
    databaseURL: 'https://warimitra-project.firebaseio.com',
  );
}
