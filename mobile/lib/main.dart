/**
 * WariMitra Mobile App - Entry point
 * Phase 1.7: Add device check for root/jailbreak detection
 */
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  
  // Phase 1.7: Device check before app runs
  // await DeviceSecurityService.checkDeviceIntegrity();
  
  runApp(const ProviderScope(child: WariMitraApp()));
}

class WariMitraApp extends ConsumerWidget {
  const WariMitraApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: 'WariMitra',
      theme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      // Phase 1.8: Support text scaling up to 200%
      builder: (context, child) {
        return MediaQuery(
          data: MediaQuery.of(context).copyWith(
            textScaleFactor: (MediaQuery.of(context).textScaleFactor * 1.2).clamp(1.0, 2.0),
          ),
          child: child!,
        );
      },
      routerConfig: _buildRouter(),
    );
  }

  GoRouter _buildRouter() {
    return GoRouter(
      initialLocation: '/',
      routes: [
        GoRoute(
          path: '/',
          builder: (context, state) => const HomePage(),
        ),
        GoRoute(
          path: '/sos',
          builder: (context, state) => const SOSPage(),
        ),
        GoRoute(
          path: '/tracking',
          builder: (context, state) => const TrackingPage(),
        ),
      ],
    );
  }
}

// Placeholder pages
class HomePage extends StatelessWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('WariMitra')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('Pilgrim Safety System'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => context.go('/sos'),
              child: const Text('SOS'),
            ),
            ElevatedButton(
              onPressed: () => context.go('/tracking'),
              child: const Text('Live Tracking'),
            ),
          ],
        ),
      ),
    );
  }
}

class SOSPage extends StatelessWidget {
  const SOSPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('SOS')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Phase 1.6: SOS button with SMS fallback
            // Phase 1.7: Geofence check before allowing SOS
            ElevatedButton(
              onPressed: () {
                // SOS logic with SMS fallback
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('SOS Activated')),
                );
              },
              child: const Text('Trigger SOS'),
            ),
          ],
        ),
      ),
    );
  }
}

class TrackingPage extends StatelessWidget {
  const TrackingPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Live Tracking')),
      body: const Center(
        child: Text('Live tracking map'),
      ),
    );
  }
}
