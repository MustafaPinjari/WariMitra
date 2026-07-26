import 'package:flutter/material.dart';
import '../widgets/spring_button.dart';

class CommunityIntelligenceScreen extends StatefulWidget {
  const CommunityIntelligenceScreen({Key? key}) : super(key: key);

  @override
  State<CommunityIntelligenceScreen> createState() => _CommunityIntelligenceScreenState();
}

class _CommunityIntelligenceScreenState extends State<CommunityIntelligenceScreen> {
  final List<Map<String, dynamic>> _reports = [
    {
      'id': 'rep-101',
      'title': 'Water Tanker Empty near Station 2',
      'category': 'Water',
      'location': 'Saswad Route (150m away)',
      'reporter': 'Priya S. (Gold Tier Citizen)',
      'confidence': '94% Verified',
      'confirmations': 18,
      'time': '5m ago',
      'icon': Icons.water_drop_rounded,
      'color': Colors.blue,
      'userVoted': false,
    },
    {
      'id': 'rep-102',
      'title': 'Heavy Crowd Bottleneck on Dive Ghat Slope',
      'category': 'Traffic',
      'location': 'Sector 4 Slope (400m away)',
      'reporter': 'Vitthal D. (Dindi Leader)',
      'confidence': '88% Verified',
      'confirmations': 12,
      'time': '12m ago',
      'icon': Icons.traffic_rounded,
      'color': Colors.amber,
      'userVoted': false,
    },
    {
      'id': 'rep-103',
      'title': 'Lost Elderly Pilgrim (Saffron Shawl)',
      'category': 'Missing',
      'location': 'Alandi Gate 2 (800m away)',
      'reporter': 'Anand K. (Volunteer)',
      'confidence': '99% Verified',
      'confirmations': 34,
      'time': '18m ago',
      'icon': Icons.person_search_rounded,
      'color': Colors.orange,
      'userVoted': false,
    },
  ];

  void _voteReport(int index) {
    setState(() {
      _reports[index]['confirmations']++;
      _reports[index]['userVoted'] = true;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('👍 Thank you! Citizen verification registered.'), backgroundColor: Colors.emerald),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F1115),
      body: SafeArea(
        child: Padding(
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
                        'Community Intelligence',
                        style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      Text(
                        'Waze-Style Citizen Reports & AI Trust Scores',
                        style: TextStyle(fontSize: 12, color: Colors.orangeAccent),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // Add Citizen Report Floating Banner
              SpringButton(
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('📷 Camera & GPS report camera opened!'), backgroundColor: Colors.orange),
                  );
                },
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(colors: [Colors.orange.withValues(alpha: 0.2), Colors.deepOrange.withValues(alpha: 0.1)]),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: Colors.orange.withValues(alpha: 0.4)),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.add_location_alt_rounded, color: Colors.orange, size: 28),
                      SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Post Citizen Incident Report', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                            Text('Attach GPS, Photo & Voice Note', style: TextStyle(color: Colors.grey, fontSize: 12)),
                          ],
                        ),
                      ),
                      Icon(Icons.camera_alt_rounded, color: Colors.orangeAccent),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              const Text('Nearby Live Citizen Reports', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 12),

              // Report Feed List
              Expanded(
                child: ListView.builder(
                  itemCount: _reports.length,
                  itemBuilder: (context, idx) {
                    final item = _reports[idx];
                    return Container(
                      margin: const EdgeInsets.only(bottom: 14),
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.05),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              CircleAvatar(
                                backgroundColor: (item['color'] as Color).withValues(alpha: 0.2),
                                child: Icon(item['icon'], color: item['color']),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(item['title'], style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                                    const SizedBox(height: 2),
                                    Text(item['location'], style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 11)),
                                  ],
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.emerald.withValues(alpha: 0.2),
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(color: Colors.emerald.withValues(alpha: 0.4)),
                                ),
                                child: Text(
                                  item['confidence'],
                                  style: const TextStyle(color: Color(0xFF10B981), fontSize: 11, fontWeight: FontWeight.bold),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('Reported by ${item['reporter']}', style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 11)),
                              SpringButton(
                                onTap: item['userVoted'] ? null : () => _voteReport(idx),
                                child: Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: item['userVoted'] ? Colors.orange.withValues(alpha: 0.3) : Colors.white.withValues(alpha: 0.1),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Row(
                                    children: [
                                      Icon(Icons.thumb_up_alt_rounded, size: 14, color: item['userVoted'] ? Colors.orange : Colors.grey),
                                      const SizedBox(width: 4),
                                      Text(
                                        'Confirm (${item['confirmations']})',
                                        style: TextStyle(
                                          color: item['userVoted'] ? Colors.orange : Colors.white,
                                          fontSize: 11,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          )
                        ],
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
