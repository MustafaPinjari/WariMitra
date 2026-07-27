import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:async';
import '../theme/app_theme.dart';
import '../widgets/spring_button.dart';

class SOSScreen extends StatefulWidget {
  const SOSScreen({Key? key}) : super(key: key);

  @override
  State<SOSScreen> createState() => _SOSScreenState();
}

class _SOSScreenState extends State<SOSScreen> with SingleTickerProviderStateMixin {
  late AnimationController _holdController;
  bool _isActivated = false;
  int _cancelCountdown = 5;
  Timer? _countdownTimer;

  @override
  void initState() {
    super.initState();
    _holdController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    );

    _holdController.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        _triggerEmergencyBroadcast();
      }
    });
  }

  void _onHoldStart() {
    if (_isActivated) return;
    HapticFeedback.heavyImpact();
    _holdController.forward();
  }

  void _onHoldEnd() {
    if (_isActivated) return;
    if (_holdController.status != AnimationStatus.completed) {
      _holdController.reverse();
    }
  }

  void _triggerEmergencyBroadcast() {
    HapticFeedback.vibrate();
    setState(() {
      _isActivated = true;
      _cancelCountdown = 5;
    });

    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_cancelCountdown > 1) {
        setState(() => _cancelCountdown--);
      } else {
        timer.cancel();
      }
    });
  }

  void _cancelEmergency() {
    _countdownTimer?.cancel();
    _holdController.reset();
    setState(() {
      _isActivated = false;
    });
    HapticFeedback.mediumImpact();
  }

  @override
  void dispose() {
    _holdController.dispose();
    _countdownTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.only(left: 20, right: 20, top: 16, bottom: 100),
          child: Column(
            children: [
              // Header
              Row(
                children: [
                  IconButton(
                    icon: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.08),
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
                      ),
                      child: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white, size: 16),
                    ),
                    onPressed: () => Navigator.pop(context),
                  ),
                  const SizedBox(width: 10),
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'आणीबाणी SOS कंसोल',
                        style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      Text(
                        '३ सेकंद दाबून ठेवा • Live Emergency Dispatch',
                        style: TextStyle(fontSize: 11, color: AppTheme.sosRed, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ],
              ),
              const Spacer(),

              // Hold to activate SOS core
              if (!_isActivated) ...[
                GestureDetector(
                  onTapDown: (_) => _onHoldStart(),
                  onTapUp: (_) => _onHoldEnd(),
                  onTapCancel: () => _onHoldEnd(),
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      // Radial Progress Ring
                      SizedBox(
                        width: 220,
                        height: 220,
                        child: AnimatedBuilder(
                          animation: _holdController,
                          builder: (context, child) {
                            return CircularProgressIndicator(
                              value: _holdController.value,
                              strokeWidth: 8,
                              backgroundColor: AppTheme.sosRed.withValues(alpha: 0.15),
                              color: AppTheme.sosRed,
                            );
                          },
                        ),
                      ),

                      // Inner Panic Button Core
                      Container(
                        width: 180,
                        height: 180,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: const LinearGradient(
                            colors: [AppTheme.sosRed, Color(0xFFB91C1C)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: AppTheme.sosRed.withValues(alpha: 0.5),
                              blurRadius: 35,
                              spreadRadius: 5,
                            )
                          ],
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.touch_app_rounded, size: 48, color: Colors.white),
                            const SizedBox(height: 8),
                            Text(
                              _holdController.isAnimating ? 'HOLD...' : 'दाबा (SOS)',
                              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Colors.white, letterSpacing: 1),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  'चुकीचा वापर टाळण्यासाठी ३ सेकंद दाबून ठेवा',
                  style: TextStyle(fontSize: 12, color: Colors.white.withValues(alpha: 0.6), fontWeight: FontWeight.bold),
                ),
              ] else ...[
                // ACTIVE BROADCAST DISPATCH STATE
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppTheme.sosRed.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: AppTheme.sosRed.withValues(alpha: 0.4)),
                  ),
                  child: Column(
                    children: [
                      const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.warning_amber_rounded, color: AppTheme.sosRed, size: 28),
                          SizedBox(width: 8),
                          Text('आणीबाणी अलर्ट सक्रिय', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: AppTheme.sosRed)),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text('GPS: 18.3444° N, 74.0305° E (Dive Ghat)', style: TextStyle(fontSize: 12, color: Colors.white.withValues(alpha: 0.9), fontWeight: FontWeight.bold)),
                      const SizedBox(height: 16),

                      if (_cancelCountdown > 0) ...[
                        Text('रद्द करण्यासाठी उर्वरित वेळ: $_cancelCountdown s', style: const TextStyle(fontSize: 13, color: AppTheme.sacredGold, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 12),
                        SpringButton(
                          onTap: _cancelEmergency,
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
                            decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(16)),
                            child: const Text('अलर्ट रद्द करा (CANCEL)', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white)),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // Responders ETA
                _buildResponderETATile(Icons.local_hospital_rounded, 'रुग्णवाहिका MH12-WM-1001', 'ETA: 4 मिनिटे', const Color(0xFF10B981)),
                _buildResponderETATile(Icons.security_rounded, 'पोलीस गस्त पथक ९', 'ETA: 6 मिनिटे', Colors.indigoAccent),
                _buildResponderETATile(Icons.volunteer_activism_rounded, 'मदतनीस (Priya S.)', 'ETA: 2 मिनिटे (150m)', AppTheme.bhagwaBright),
              ],

              const Spacer(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildResponderETATile(IconData icon, String title, String eta, Color accentColor) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
      ),
      child: Row(
        children: [
          CircleAvatar(backgroundColor: accentColor.withValues(alpha: 0.2), child: Icon(icon, color: accentColor)),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                const SizedBox(height: 2),
                Text('नियंत्रण कक्षाद्वारे रवाना', style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 10)),
              ],
            ),
          ),
          Text(eta, style: TextStyle(color: accentColor, fontWeight: FontWeight.w800, fontSize: 12)),
        ],
      ),
    );
  }
}
