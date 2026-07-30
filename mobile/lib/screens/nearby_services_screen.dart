import 'package:flutter/material.dart';
import '../widgets/spring_button.dart';
import '../services/api_service.dart';

class NearbyServicesScreen extends StatefulWidget {
  const NearbyServicesScreen({Key? key}) : super(key: key);

  @override
  State<NearbyServicesScreen> createState() => _NearbyServicesScreenState();
}

class _NearbyServicesScreenState extends State<NearbyServicesScreen> {
  String _selectedCategory = 'All';
  List<Map<String, dynamic>> _services = [];
  bool _isLoading = true;

  final List<Map<String, dynamic>> _fallbackServices = [
    {'name': 'Drinking Water Point 4', 'category': 'Water', 'distance': '150m', 'status': 'Available (50,000L)', 'icon': Icons.water_drop_rounded, 'color': Colors.blue},
    {'name': 'Camp Alpha Health Center', 'category': 'Medical', 'distance': '350m', 'status': '4 Doctors Available', 'icon': Icons.medical_services_rounded, 'color': Color(0xFF10B981)},
    {'name': 'Community Annadhana Stalls', 'category': 'Food', 'distance': '500m', 'status': 'Serving Meals', 'icon': Icons.restaurant_rounded, 'color': Colors.orange},
    {'name': 'Public Restrooms & Showers', 'category': 'Toilets', 'distance': '200m', 'status': 'Clean & Open', 'icon': Icons.wc_rounded, 'color': Colors.purple},
    {'name': 'Shelter Camp 12 — Night Stay', 'category': 'Shelter', 'distance': '1.2km', 'status': 'Beds Available (120)', 'icon': Icons.night_shelter_rounded, 'color': Colors.teal},
  ];

  @override
  void initState() {
    super.initState();
    _loadServices();
  }

  Future<void> _loadServices() async {
    setState(() => _isLoading = true);
    try {
      // Try to load toilets from backend as a real data source
      final response = await ApiService.dio.get('/sanitation/toilets/');
      final data = response.data;
      final toilets = data is List ? data : (data['results'] ?? []);

      // Map toilet records to service card format
      final toiletServices = (toilets as List).map<Map<String, dynamic>>((t) => {
        'name': t['name']?.toString() ?? 'Public Toilet',
        'category': 'Toilets',
        'distance': 'Nearby',
        'status': 'Cleanliness: ${t['cleanliness_score']}%',
        'icon': Icons.wc_rounded,
        'color': Colors.purple,
      }).toList();

      // Merge with fallback static services (Water, Medical, Food, Shelter)
      final merged = [
        ..._fallbackServices.where((s) => s['category'] != 'Toilets'),
        ...toiletServices,
      ];

      setState(() {
        _services = merged;
        _isLoading = false;
      });
    } catch (_) {
      // Fall back to static data
      setState(() {
        _services = List.from(_fallbackServices);
        _isLoading = false;
      });
    }
  }

  List<Map<String, dynamic>> get _filtered {
    if (_selectedCategory == 'All') return _services;
    return _services.where((s) => s['category'] == _selectedCategory).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F1115),
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
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
                            Text('Nearby Services', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white)),
                            Text('GPS Distance Filtered', style: TextStyle(fontSize: 12, color: Colors.grey)),
                          ],
                        ),
                      ),
                      IconButton(icon: const Icon(Icons.refresh_rounded, color: Colors.orange), onPressed: _loadServices),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Filter chips
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: ['All', 'Water', 'Food', 'Medical', 'Toilets', 'Shelter'].map((cat) {
                        final isSelected = _selectedCategory == cat;
                        return Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: ChoiceChip(
                            label: Text(cat),
                            selected: isSelected,
                            onSelected: (_) => setState(() => _selectedCategory = cat),
                            selectedColor: Colors.orange,
                            backgroundColor: Colors.white.withValues(alpha: 0.08),
                            labelStyle: TextStyle(color: isSelected ? Colors.white : Colors.grey, fontWeight: FontWeight.bold),
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                ],
              ),
            ),

            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator(color: Colors.orange))
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 20),
                      itemCount: _filtered.length,
                      itemBuilder: (context, index) {
                        final item = _filtered[index];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: SpringButton(
                            onTap: () {},
                            child: Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: Colors.white.withValues(alpha: 0.05),
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
                              ),
                              child: Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.all(12),
                                    decoration: BoxDecoration(
                                      color: (item['color'] as Color).withValues(alpha: 0.2),
                                      borderRadius: BorderRadius.circular(16),
                                    ),
                                    child: Icon(item['icon'] as IconData, color: item['color'] as Color),
                                  ),
                                  const SizedBox(width: 16),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(item['name'] as String, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white)),
                                        const SizedBox(height: 4),
                                        Text(item['status'] as String, style: TextStyle(fontSize: 12, color: Colors.white.withValues(alpha: 0.6))),
                                      ],
                                    ),
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                    decoration: BoxDecoration(
                                      color: Colors.white.withValues(alpha: 0.08),
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: Text(
                                      item['distance'] as String,
                                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.orange),
                                    ),
                                  ),
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
    );
  }
}
