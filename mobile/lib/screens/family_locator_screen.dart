import 'package:flutter/material.dart';
import '../widgets/spring_button.dart';

class FamilyLocatorScreen extends StatelessWidget {
  const FamilyLocatorScreen({Key? key}) : super(key: key);

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
                        'Family & Dindi Locator',
                        style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      Text(
                        'Consent-Based GPS Sharing',
                        style: TextStyle(fontSize: 12, color: Colors.blueAccent),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // Family Group Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(colors: [Colors.blue.withOpacity(0.15), Colors.purple.withOpacity(0.15)]),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.blue.withOpacity(0.3)),
                ),
                child: Row(
                  children: [
                    const CircleAvatar(
                      backgroundColor: Colors.blue,
                      child: Icon(Icons.groups_rounded, color: Colors.white),
                    ),
                    const SizedBox(width: 14),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Jadhav Family Group', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                          Text('4 Active Members • Safe Zone Active', style: TextStyle(color: Colors.grey, fontSize: 12)),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.person_add_rounded, color: Colors.blueAccent),
                      onPressed: () {},
                    )
                  ],
                ),
              ),
              const SizedBox(height: 24),

              const Text('Group Members', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 12),

              // Member List
              Expanded(
                child: ListView(
                  children: [
                    _buildMemberTile('Ramesh Jadhav (You)', 'Near Water Point 4 (150m)', '98%', const Color(0xFF10B981), true),
                    _buildMemberTile('Sunita Jadhav', 'Near Camp Alpha (350m)', '84%', const Color(0xFF10B981), false),
                    _buildMemberTile('Anish Jadhav (Child)', 'Alandi Gate 2 Approach', '62%', Colors.amber, false),
                    _buildMemberTile('Vitthal Deshmukh (Dindi Leader)', 'Shri Vitthal Dindi Head', '91%', Colors.blue, false),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMemberTile(String name, String location, String battery, Color statusColor, bool isSelf) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.08)),
      ),
      child: Row(
        children: [
          CircleAvatar(
            backgroundColor: statusColor.withOpacity(0.2),
            child: Icon(isSelf ? Icons.person_rounded : Icons.face_rounded, color: statusColor),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                const SizedBox(height: 2),
                Text(location, style: TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 12)),
              ],
            ),
          ),
          Row(
            children: [
              Icon(Icons.battery_std_rounded, size: 16, color: Colors.white.withOpacity(0.5)),
              Text(battery, style: TextStyle(color: Colors.white.withOpacity(0.7), fontSize: 12, fontWeight: FontWeight.bold)),
            ],
          ),
        ],
      ),
    );
  }
}
