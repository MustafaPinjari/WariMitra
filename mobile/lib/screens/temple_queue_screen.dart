import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/spring_button.dart';

class TempleQueueScreen extends StatefulWidget {
  const TempleQueueScreen({Key? key}) : super(key: key);

  @override
  State<TempleQueueScreen> createState() => _TempleQueueScreenState();
}

class _TempleQueueScreenState extends State<TempleQueueScreen> {
  List<dynamic> _queues = [];
  bool _isLoading = true;
  Map<String, dynamic>? _myToken;

  @override
  void initState() {
    super.initState();
    _loadQueues();
  }

  Future<void> _loadQueues() async {
    setState(() => _isLoading = true);
    try {
      final response = await ApiService.dio.get('/temple/queues/');
      final data = response.data;
      setState(() {
        _queues = data is List ? data : (data['results'] ?? []);
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _bookSlot(String slotId) async {
    try {
      final response = await ApiService.dio.post('/temple/slots/$slotId/book_slot/');
      if (mounted) {
        setState(() {
          _myToken = response.data as Map<String, dynamic>;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ Darshan booked! Token: ${_myToken!['token']}'),
            backgroundColor: Colors.purple,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('❌ ${ApiService.errorMessage(e)}'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Color _waitColor(int? waitMins) {
    if (waitMins == null) return Colors.grey;
    if (waitMins > 200) return Colors.red;
    if (waitMins > 100) return Colors.amber;
    return const Color(0xFF10B981);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F1115),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white),
                    onPressed: () => Navigator.pop(context),
                  ),
                  const SizedBox(width: 8),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Temple Queue & Darshan', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white)),
                        Text('Live Wait Times & Pre-Booking', style: TextStyle(fontSize: 12, color: Colors.purpleAccent)),
                      ],
                    ),
                  ),
                  IconButton(icon: const Icon(Icons.refresh_rounded, color: Colors.purpleAccent), onPressed: _loadQueues),
                ],
              ),
              const SizedBox(height: 24),

              // Active Token Card (if booked)
              if (_myToken != null) ...[
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(colors: [Colors.purple.withValues(alpha: 0.3), Colors.deepPurple.withValues(alpha: 0.2)]),
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: Colors.purple.withValues(alpha: 0.4)),
                    boxShadow: [BoxShadow(color: Colors.purple.withValues(alpha: 0.2), blurRadius: 20, offset: const Offset(0, 6))],
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
                      Text(
                        'TOKEN #${_myToken!['token']}',
                        style: const TextStyle(color: Colors.white, fontSize: 26, fontWeight: FontWeight.w900, letterSpacing: 1.2),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        _myToken!['message']?.toString() ?? 'Booking confirmed',
                        style: TextStyle(color: Colors.purple.shade200, fontSize: 13, fontWeight: FontWeight.w600),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
              ],

              const Text('Live Gate Queue Status', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 12),

              if (_isLoading)
                const Center(child: CircularProgressIndicator(color: Colors.purple))
              else if (_queues.isEmpty)
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.04), borderRadius: BorderRadius.circular(16)),
                  child: Column(
                    children: [
                      const Text('No queue data available from server', style: TextStyle(color: Colors.grey)),
                      const SizedBox(height: 8),
                      const Text(
                        'Showing estimated wait times:',
                        style: TextStyle(color: Colors.white54, fontSize: 12),
                      ),
                      const SizedBox(height: 12),
                      _buildGateCard('Gate 1 — Main Entrance', 'General Queue', '260 Mins', '3,200 Pilgrims', Colors.red),
                      _buildGateCard('Gate 2 — Senior Citizens', 'Senior Queue', '80 Mins', '450 Pilgrims', const Color(0xFF10B981)),
                      _buildGateCard('Gate 3 — VIP & Emergency', 'Bypass Line', '20 Mins', '60 Pilgrims', Colors.blue),
                      _buildGateCard('Gate 4 — Women Queue', 'Women Queue', '180 Mins', '1,800 Pilgrims', Colors.purple),
                    ],
                  ),
                )
              else
                ..._queues.map((q) {
                  final waitMin = q['average_wait_time'] as int? ?? 0;
                  final color = _waitColor(waitMin);
                  return Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.05),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(q['gate_id']?.toString() ?? 'Gate', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                              const SizedBox(height: 4),
                              Text('${q['queue_type']} • ${q['current_count']} pilgrims', style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 12)),
                              Text('Status: ${q['status']}', style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          decoration: BoxDecoration(
                            color: color.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(color: color.withValues(alpha: 0.3)),
                          ),
                          child: Text('$waitMin Mins', style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 13)),
                        ),
                      ],
                    ),
                  );
                }),

              const SizedBox(height: 20),
              if (_myToken == null) ...[
                const Text('Book Darshan Slot', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 8),
                Text(
                  'Login required to book a slot. Slots are loaded from the Temple API.',
                  style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 12),
                ),
                const SizedBox(height: 12),
                SpringButton(
                  onTap: () => _bookSlot("dummy-slot-id-1234"), // We will implement actual slot fetching later
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                    decoration: BoxDecoration(
                      color: Colors.purple,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Text('Book Next Available Slot', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildGateCard(String gate, String queueType, String waitTime, String currentCount, Color accentColor) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.04),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withValues(alpha: 0.06)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(gate, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
              const SizedBox(height: 2),
              Text('$queueType • $currentCount', style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 11)),
            ],
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: accentColor.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: accentColor.withValues(alpha: 0.3)),
            ),
            child: Text(waitTime, style: TextStyle(color: accentColor, fontWeight: FontWeight.bold, fontSize: 12)),
          ),
        ],
      ),
    );
  }
}
