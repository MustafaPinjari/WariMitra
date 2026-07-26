import 'package:flutter/material.dart';
import 'dart:ui';
import 'screens/home_screen.dart';
import 'screens/sos_screen.dart';
import 'screens/services_screen.dart';
import 'screens/splash_screen.dart';

void main() {
  runApp(const WariMitraApp());
}

class WariMitraApp extends StatelessWidget {
  const WariMitraApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'WariMitra',
      theme: ThemeData(
        primarySwatch: Colors.orange,
        scaffoldBackgroundColor: const Color(0xFF0F1115),
      ),
      home: const AppEntry(),
      debugShowCheckedModeBanner: false,
    );
  }
}

/// AppEntry shows the SplashScreen first, then transitions to MainNavigation.
class AppEntry extends StatefulWidget {
  const AppEntry({Key? key}) : super(key: key);

  @override
  State<AppEntry> createState() => _AppEntryState();
}

class _AppEntryState extends State<AppEntry> {
  bool _showSplash = true;

  void _onSplashComplete() {
    setState(() => _showSplash = false);
  }

  @override
  Widget build(BuildContext context) {
    return _showSplash
        ? SplashScreen(onComplete: _onSplashComplete)
        : const MainNavigation();
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
    SOSScreen(),
    const ServicesScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F1115),
      extendBody: true,
      body: Stack(
        children: [
          _screens[_currentIndex],
          Positioned(
            bottom: 30,
            left: 40,
            right: 40,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(30),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 15, sigmaY: 15),
                child: Container(
                  height: 65,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(30),
                    border: Border.all(color: Colors.white.withOpacity(0.1)),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _buildNavItem(Icons.home_rounded, 0),
                      _buildNavItem(Icons.warning_rounded, 1, isSos: true),
                      _buildNavItem(Icons.handshake_rounded, 2),
                    ],
                  ),
                ),
              ),
            ),
          )
        ],
      ),
    );
  }

  Widget _buildNavItem(IconData icon, int index, {bool isSos = false}) {
    final isSelected = _currentIndex == index;
    final color = isSos 
        ? Colors.red 
        : isSelected ? Colors.orange : Colors.white.withOpacity(0.4);
    
    return GestureDetector(
      onTap: () => setState(() => _currentIndex = index),
      behavior: HitTestBehavior.opaque,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeOutCubic,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
        decoration: BoxDecoration(
          color: isSelected && !isSos ? Colors.orange.withOpacity(0.15) : Colors.transparent,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Icon(icon, color: color, size: isSelected ? 28 : 24),
      ),
    );
  }
}
