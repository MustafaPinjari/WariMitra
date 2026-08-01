import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:ui';
import 'theme/app_theme.dart';
import 'screens/home_screen.dart';
import 'screens/sos_screen.dart';
import 'screens/services_screen.dart';
import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'providers/auth_provider.dart';

import 'services/notification_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await NotificationService.init();
  runApp(const ProviderScope(child: WariMitraApp()));
}

class WariMitraApp extends StatelessWidget {
  const WariMitraApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'WariMitra • वारीमित्र',
      theme: AppTheme.darkTheme,
      home: const AppEntry(),
      debugShowCheckedModeBanner: false,
    );
  }
}

/// AppEntry shows SplashScreen first, then checks auth and routes accordingly.
class AppEntry extends ConsumerStatefulWidget {
  const AppEntry({Key? key}) : super(key: key);

  @override
  ConsumerState<AppEntry> createState() => _AppEntryState();
}

class _AppEntryState extends ConsumerState<AppEntry> {
  bool _showSplash = true;

  void _onSplashComplete() {
    setState(() => _showSplash = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_showSplash) {
      return SplashScreen(onComplete: _onSplashComplete);
    }

    final authState = ref.watch(authProvider);

    // While checking existing session, show loading
    if (authState.isLoading) {
      return const Scaffold(
        backgroundColor: AppTheme.bgDark,
        body: Center(
          child: CircularProgressIndicator(color: AppTheme.bhagwaPrimary),
        ),
      );
    }

    if (authState.isLoggedIn) {
      return const MainNavigation();
    }

    return const LoginScreen();
  }
}

class MainNavigation extends StatefulWidget {
  const MainNavigation({Key? key}) : super(key: key);

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const HomeScreen(),
    const SOSScreen(),
    const ServicesScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      extendBody: true,
      body: Stack(
        children: [
          _screens[_currentIndex],

          // Floating Navigation Bar with Safety Padding
          Positioned(
            bottom: 20,
            left: 20,
            right: 20,
            child: SafeArea(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(26),
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: AppTheme.marathaNavy.withValues(alpha: 0.92),
                      borderRadius: BorderRadius.circular(26),
                      border: Border.all(color: AppTheme.bhagwaPrimary.withValues(alpha: 0.35), width: 1.2),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.5),
                          blurRadius: 25,
                          offset: const Offset(0, 10),
                        )
                      ],
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _buildNavItem(Icons.home_rounded, 'गृह • Home', 0),
                        _buildNavItem(Icons.warning_amber_rounded, 'आणीबाणी • SOS', 1, isSos: true),
                        _buildNavItem(Icons.handshake_rounded, 'सेवा • Relief', 2),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavItem(IconData icon, String label, int index, {bool isSos = false}) {
    final isSelected = _currentIndex == index;
    final activeColor = isSos ? AppTheme.sosRed : AppTheme.bhagwaPrimary;
    final inactiveColor = Colors.white.withValues(alpha: 0.5);

    return GestureDetector(
      onTap: () => setState(() => _currentIndex = index),
      behavior: HitTestBehavior.opaque,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 220),
        curve: Curves.easeOutCubic,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected
              ? activeColor.withValues(alpha: 0.18)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(18),
          border: isSelected
              ? Border.all(color: activeColor.withValues(alpha: 0.4), width: 1)
              : Border.all(color: Colors.transparent),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              color: isSelected ? activeColor : inactiveColor,
              size: isSelected ? 24 : 22,
            ),
            if (isSelected) ...[
              const SizedBox(width: 8),
              Text(
                label,
                style: TextStyle(
                  color: activeColor,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                  letterSpacing: -0.2,
                ),
              ),
            ]
          ],
        ),
      ),
    );
  }
}
