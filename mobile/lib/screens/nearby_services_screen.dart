import 'package:flutter/material.dart';
import 'dart:ui';
import '../widgets/spring_button.dart';

class NearbyServicesScreen extends StatefulWidget {
  const NearbyServicesScreen({Key? key}) : super(key: key);

  @override
  State<NearbyServicesScreen> createState() => _NearbyServicesScreenState();
}

class _NearbyServicesScreenState extends State<NearbyServicesScreen> {
  String _selectedCategory = 'All';

  final List<Map<String, dynamic>> _services = [
    {
      'name': 'Drinking Water Point 4',
      'category': 'Water',
      'distance': '150m',
      'status': 'Available (50,000L)',
      'icon': Icons.water_drop_rounded,
      'color': Colors.blue,
    },
    {
      'name': 'Camp Alpha Health Center',
      'category': 'Medical',
      'distance': '350m',
      'status': '4 Doctors Available',
      'icon': Icons.medical_services_rounded,
      'color': const Color(0xFF10B981),
    },
    {
      'name': 'Community Annadhana Stalls',
      'category': 'Food',
      'distance': '500m',
      'status': 'Serving Meals',
      'icon': Icons.restaurant_rounded,
      'color': Colors.orange,
    },
    {
      'name': 'Public Restrooms & Showers',
      'category': 'Toilets',
      'distance': '200m',
      'status': 'Clean & Open',
      'icon': Icons.wc_rounded,
      'color': Colors.purple,
    },
    {
      'name': 'Shelter Camp 12 — Night Stay',
      'category': 'Shelter',
      'distance': '1.2km',
      'status': 'Beds Available (120)',
      'icon': Icons.night_shelter_rounded,
      'color': Colors.teal,
    },
  ];

  @override
  Widget build(BuildContext context) {
    final filtered = _selectedCategory == 'All'
        ? _services
        : _services.where((s) => s['category'] == _selectedCategory).toList();

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
                        'Nearby Services',
                        style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      Text(
                        'GPS Distance Filtered',
                        style: TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // Filter Chips
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: ['All', 'Water', 'Food', 'Medical', 'Toilets', 'Shelter'].map((cat) {
                    final isSelected = _selectedCategory == cat;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8.0),
                      child: ChoiceChip(
                        label: Text(cat),
                        selected: isSelected,
                        onSelected: (_) => setState(() => _selectedCategory = cat),
                        selectedColor: Colors.orange,
                        backgroundColor: Colors.white.withOpacity(0.08),
                        labelStyle: TextStyle(
                          color: isSelected ? Colors.white : Colors.grey,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
              const SizedBox(height: 20),

              // List of services
              Expanded(
                child: ListView.builder(
                  itemCount: filtered.length,
                  itemBuilder: (context, index) {
                    final item = filtered[index];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12.0),
                      child: SpringButton(
                        onTap: () {},
                        child: Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.05),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(color: Colors.white.withOpacity(0.08)),
                          ),
                          child: Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: (item['color'] as Color).withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(16),
                                ),
                                child: Icon(item['icon'], color: item['color']),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      item['name'],
                                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      item['status'],
                                      style: TextStyle(fontSize: 12, color: Colors.white.withOpacity(0.6)),
                                    ),
                                  ],
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.08),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Text(
                                  item['distance'],
                                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.orange),
                                ),
                              )
                            ],
                          ),
                        ),
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
