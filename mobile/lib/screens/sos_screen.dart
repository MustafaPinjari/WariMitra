import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:async';
import 'dart:ui';
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
      backgroundColor: const Color(0xFF0F1115),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            children: [
              // Header
              Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white),
                    onPressed: () => Navigator.pop(context),
                  ),
                  const SizedBox(width: 8),
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Emergency SOS Console',
                        style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      Text(
                        'Hold 3 Seconds to Activate • Live Responder Dispatch',
                        style: TextStyle(fontSize: 12, color: Colors.redAccent),
                      ),
                    ],
                  ),
                ],
              ),
              const Spacer(),

              // Hold-to-Activate SOS Ring or Active Countdown State
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
                              backgroundColor: Colors.red.withValues(alpha: 0.15),
                              color: Colors.redAccent,
                            );
                          },
                        ),
                      ),

                      // Inner Pulsing Panic Core
                      Container(
                        width: 180,
                        height: 180,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: const LinearGradient(colors: [Colors.red, Colors.deepOrange]),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.red.withValues(alpha: 0.5),
                              blurRadius: 30,
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
                              _holdController.isAnimating ? 'HOLD...' : 'HOLD TO SOS',
                              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Colors.white, letterSpacing: 1),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  'Press and hold for 3 seconds to prevent accidental triggers',
                  style: TextStyle(fontSize: 12, color: Colors.white.withValues(alpha: 0.6)),
                ),
              ] else ...[
                // ACTIVE SOS EMERGENCY DISPATCH STATE
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.red.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: Colors.red.withValues(alpha: 0.4)),
                  ),
                  child: Column(
                    children: [
                      const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.warning_amber_rounded, color: Colors.redAccent, size: 28),
                          SizedBox(width: 8),
                          Text('EMERGENCY BROADCAST ACTIVE', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Colors.redAccent)),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text('GPS: 18.3444° N, 74.0305° E (Dive Ghat)', style: TextStyle(fontSize: 12, color: Colors.white.withValues(alpha: 0.8), fontWeight: FontWeight.bold)),
                      const SizedBox(height: 16),

                      // Countdown window to cancel
                      if (_cancelCountdown > 0) ...[
                        Text('Cancel window closes in $_cancelCountdown s', style: const TextStyle(fontSize: 13, color: Colors.amber, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 12),
                        SpringButton(
                          onTap: _cancelEmergency,
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
                            decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(16)),
                            child: const Text('CANCEL SOS', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.white)),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // Responders ETA List
                _buildResponderETATile(Icons.local_hospital_rounded, 'Ambulance MH12-WM-1001', 'ETA: 4 Minutes', const Color(0xFF10B981)),
                _buildResponderETATile(Icons.security_rounded, 'Police Patrol Unit 9', 'ETA: 6 Minutes', Colors.indigo),
                _buildResponderETATile(Icons.volunteer_activism_rounded, 'Nearby Volunteer (Priya S.)', 'ETA: 2 Minutes (150m)', Colors.orange),
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
        color: Colors.white.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
      ),
      child: Row(
        children: [
          CircleAvatar(backgroundColor: accentColor.withValues(alpha: 0.2), child: Icon(icon, color: accentColor)),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                const SizedBox(height: 2),
                Text('Dispatched by Command Center', style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 11)),
              ],
            ),
          ),
          Text(eta, style: TextStyle(color: accentColor, fontWeight: FontWeight.w800, fontSize: 12)),
        ],
      ),
    );
  }
}
