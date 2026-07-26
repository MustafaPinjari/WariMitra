import 'package:flutter/material.dart';
import '../widgets/spring_button.dart';

class TempleQueueScreen extends StatelessWidget {
  const TempleQueueScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F1115),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
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
                        'Temple Queue & Darshan',
                        style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      Text(
                        'Live Wait Times & Pre-Booking',
                        style: TextStyle(fontSize: 12, color: Colors.purpleAccent),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Active Token Card
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(colors: [Colors.purple.withOpacity(0.3), Colors.deepPurple.withOpacity(0.2)]),
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: Colors.purple.withOpacity(0.4)),
                  boxShadow: [
                    BoxShadow(color: Colors.purple.withOpacity(0.2), blurRadius: 20, offset: const Offset(0, 6)),
                  ],
                ),
                child: Column(
                  children: [
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Your Virtual Darshan Token', style: TextStyle(color: Colors.white70, fontSize: 13, fontWeight: FontWeight.bold)),
                        Icon(Icons.qr_code_2_rounded, color: Colors.purpleAccent, size: 28),
                      ],
                    ),
                    const SizedBox(height: 16),
                    const Text('TOKEN #WM-8492', style: TextStyle(color: Colors.white, fontSize: 26, fontWeight: FontWeight.w900, letterSpacing: 1.2)),
                    const SizedBox(height: 6),
                    Text('Assigned Slot: 06:30 PM — 07:00 PM', style: TextStyle(color: Colors.purple.shade200, fontSize: 13, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                      decoration: BoxDecoration(color: Colors.white.withOpacity(0.1), borderRadius: BorderRadius.circular(12)),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.timer_rounded, size: 16, color: Colors.amber),
                          SizedBox(width: 6),
                          Text('Estimated Wait: 45 Minutes', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              const Text('Live Gate Queue Status', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 12),

              _buildGateCard('Gate 1 — Main Entrance', 'General Queue', '260 Mins', '3,200 Pilgrims', Colors.red),
              _buildGateCard('Gate 2 — Senior Citizens', 'Senior Queue', '80 Mins', '450 Pilgrims', const Color(0xFF10B981)),
              _buildGateCard('Gate 3 — VIP & Emergency', 'Bypass Line', '20 Mins', '60 Pilgrims', Colors.blue),
              _buildGateCard('Gate 4 — Women Queue', 'Women Queue', '180 Mins', '1,800 Pilgrims', Colors.purple),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildGateCard(String gate, String queueType, String waitTime, String currentCount, Color accentColor) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.08)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(gate, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
              const SizedBox(height: 4),
              Text('$queueType • $currentCount', style: TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 12)),
            ],
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: accentColor.withOpacity(0.15),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: accentColor.withOpacity(0.3)),
            ),
            child: Text(waitTime, style: TextStyle(color: accentColor, fontWeight: FontWeight.bold, fontSize: 13)),
          ),
        ],
      ),
    );
  }
}
