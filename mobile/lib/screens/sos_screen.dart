import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:async';
import '../theme/app_theme.dart';
import '../widgets/spring_button.dart';
import '../services/api_service.dart';
import '../services/location_service.dart';

class SOSScreen extends StatefulWidget {
  const SOSScreen({Key? key}) : super(key: key);

  @override
  State<SOSScreen> createState() => _SOSScreenState();
}

class _SOSScreenState extends State<SOSScreen> with SingleTickerProviderStateMixin {
  late AnimationController _holdController;
  bool _isActivated = false;
  bool _isSending = false;
  int _cancelCountdown = 5;
  Timer? _countdownTimer;
  String? _activeIncidentId;
  String _gpsInfo = 'Getting location...';
  double? _lat;
  double? _lng;

  // Mock responder data (shown after SOS activation)
  final List<Map<String, dynamic>> _responders = [
    {'icon': Icons.local_hospital_rounded, 'title': 'रुग्णवाहिका', 'eta': 'ETA: 4 mins', 'color': Color(0xFF10B981)},
    {'icon': Icons.security_rounded, 'title': 'पोलीस गस्त पथक', 'eta': 'ETA: 6 mins', 'color': Colors.indigoAccent},
    {'icon': Icons.volunteer_activism_rounded, 'title': 'जवळचे मदतनीस', 'eta': 'ETA: 2 mins', 'color': AppTheme.bhagwaBright},
  ];

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
    _initLocation();
  }

  Future<void> _initLocation() async {
    final pos = await LocationService.getCurrentPosition();
    if (mounted) {
      setState(() {
        if (pos != null) {
          _lat = pos.latitude;
          _lng = pos.longitude;
          _gpsInfo = '${pos.latitude.toStringAsFixed(4)}° N, ${pos.longitude.toStringAsFixed(4)}° E';
        } else {
          _gpsInfo = 'Location unavailable';
        }
      });
    }
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

  Future<void> _triggerEmergencyBroadcast() async {
    HapticFeedback.vibrate();
    setState(() {
      _isActivated = true;
      _isSending = true;
      _cancelCountdown = 5;
    });

    // Call backend SOS API
    try {
      final response = await ApiService.dio.post('/sos/', data: {
        'emergency_type': 'Medical',
        'priority': 'Critical',
        'latitude': _lat ?? 18.3444,
        'longitude': _lng ?? 74.0305,
        'description': 'SOS triggered from WariMitra app',
      });
      _activeIncidentId = response.data['id']?.toString();
    } catch (e) {
      // SOS sent best-effort; show a warning but keep activated
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('⚠️ Network issue: ${ApiService.errorMessage(e)}. Local alert active.'),
            backgroundColor: AppTheme.sacredGold,
          ),
        );
      }
    }

    setState(() => _isSending = false);

    // Countdown timer
    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_cancelCountdown > 1) {
        setState(() => _cancelCountdown--);
      } else {
        timer.cancel();
      }
    });
  }

  Future<void> _cancelEmergency() async {
    _countdownTimer?.cancel();
    _holdController.reset();

    // If an incident was created, close it
    if (_activeIncidentId != null) {
      try {
        await ApiService.dio.post('/sos/$_activeIncidentId/close/');
      } catch (_) {}
    }

    setState(() {
      _isActivated = false;
      _activeIncidentId = null;
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
                  const Expanded(
                    child: Column(
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
                  ),
                ],
              ),

              // GPS Status
              Container(
                margin: const EdgeInsets.only(top: 12),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.05),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.location_on_rounded, size: 14, color: _lat != null ? AppTheme.bhagwaBright : Colors.grey),
                    const SizedBox(width: 6),
                    Text(_gpsInfo, style: TextStyle(fontSize: 11, color: Colors.white.withValues(alpha: 0.7))),
                  ],
                ),
              ),

              const Spacer(),

              if (!_isActivated) ...[
                GestureDetector(
                  onTapDown: (_) => _onHoldStart(),
                  onTapUp: (_) => _onHoldEnd(),
                  onTapCancel: () => _onHoldEnd(),
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
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
                            AnimatedBuilder(
                              animation: _holdController,
                              builder: (context, _) => Text(
                                _holdController.isAnimating ? 'HOLD...' : 'दाबा (SOS)',
                                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Colors.white, letterSpacing: 1),
                              ),
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
                // ACTIVE SOS STATE
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppTheme.sosRed.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: AppTheme.sosRed.withValues(alpha: 0.4)),
                  ),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.warning_amber_rounded, color: AppTheme.sosRed, size: 28),
                          const SizedBox(width: 8),
                          Text(
                            _isSending ? 'अलर्ट पाठवत आहे...' : 'आणीबाणी अलर्ट सक्रिय',
                            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: AppTheme.sosRed),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'GPS: $_gpsInfo',
                        style: TextStyle(fontSize: 12, color: Colors.white.withValues(alpha: 0.9), fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 16),

                      if (_cancelCountdown > 1) ...[
                        Text(
                          'रद्द करण्यासाठी उर्वरित वेळ: $_cancelCountdown s',
                          style: const TextStyle(fontSize: 13, color: AppTheme.sacredGold, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 12),
                        SpringButton(
                          onTap: _cancelEmergency,
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
                            decoration: BoxDecoration(
                              color: Colors.white.withValues(alpha: 0.15),
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: const Text(
                              'अलर्ट रद्द करा (CANCEL)',
                              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // Responders list
                ..._responders.map((r) => _buildResponderETATile(
                  r['icon'] as IconData,
                  r['title'] as String,
                  r['eta'] as String,
                  r['color'] as Color,
                )),
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
          CircleAvatar(
            backgroundColor: accentColor.withValues(alpha: 0.2),
            child: Icon(icon, color: accentColor),
          ),
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
