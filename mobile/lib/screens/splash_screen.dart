import 'package:flutter/material.dart';
import 'dart:ui';

class SplashScreen extends StatefulWidget {
  final VoidCallback onComplete;

  const SplashScreen({Key? key, required this.onComplete}) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeIn;
  late Animation<double> _scaleIn;
  late Animation<double> _fadeOut;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2800),
    );

    _fadeIn = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: const Interval(0.0, 0.35, curve: Curves.easeOut)),
    );

    _scaleIn = Tween<double>(begin: 0.85, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: const Interval(0.0, 0.4, curve: Curves.easeOutCubic)),
    );

    _fadeOut = Tween<double>(begin: 1.0, end: 0.0).animate(
      CurvedAnimation(parent: _controller, curve: const Interval(0.75, 1.0, curve: Curves.easeIn)),
    );

    _controller.forward().then((_) {
      widget.onComplete();
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Opacity(
          opacity: _fadeOut.value,
          child: Scaffold(
            backgroundColor: const Color(0xFF0F1115),
            body: Stack(
              children: [
                // Ambient background glow — orange
                Positioned(
                  top: -80,
                  left: -80,
                  child: Container(
                    width: 350,
                    height: 350,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: const Color(0xFFFF6B00).withOpacity(0.12),
                    ),
                    child: BackdropFilter(
                      filter: ImageFilter.blur(sigmaX: 120, sigmaY: 120),
                      child: Container(color: Colors.transparent),
                    ),
                  ),
                ),
                // Ambient background glow — green (bottom right)
                Positioned(
                  bottom: -80,
                  right: -80,
                  child: Container(
                    width: 300,
                    height: 300,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: const Color(0xFF2D6A4F).withOpacity(0.12),
                    ),
                    child: BackdropFilter(
                      filter: ImageFilter.blur(sigmaX: 120, sigmaY: 120),
                      child: Container(color: Colors.transparent),
                    ),
                  ),
                ),

                // Centered content
                Center(
                  child: FadeTransition(
                    opacity: _fadeIn,
                    child: ScaleTransition(
                      scale: _scaleIn,
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          // Web logo (WariMitra_WebLogo) used on splash
                          Image.asset(
                            'assets/images/splash_logo.png',
                            width: 220,
                            height: 220,
                            fit: BoxFit.contain,
                          ),
                          const SizedBox(height: 32),
                          // Tagline
                          Text(
                            'साथ चालू, सुरक्षित पोहोचू',
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.white.withOpacity(0.6),
                              fontWeight: FontWeight.w400,
                              letterSpacing: 0.5,
                            ),
                          ),
                          const SizedBox(height: 60),
                          // Loading indicator
                          SizedBox(
                            width: 180,
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(4),
                              child: LinearProgressIndicator(
                                backgroundColor: Colors.white.withOpacity(0.08),
                                color: const Color(0xFFFF6B00),
                                minHeight: 2,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
