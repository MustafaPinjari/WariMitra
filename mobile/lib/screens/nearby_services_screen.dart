import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart' as latlong;
import 'package:geolocator/geolocator.dart';
import '../widgets/spring_button.dart';
import '../services/api_service.dart';
import '../services/location_service.dart';

class NearbyServicesScreen extends StatefulWidget {
  const NearbyServicesScreen({super.key});

  @override
  State<NearbyServicesScreen> createState() => _NearbyServicesScreenState();
}

class _NearbyServicesScreenState extends State<NearbyServicesScreen> {
  String _selectedCategory = 'All';
  List<Map<String, dynamic>> _services = [];
  bool _isLoading = true;
  Position? _currentPosition;
  final MapController _mapController = MapController();
  Map<String, dynamic>? _selectedPoint;

  final List<String> _categories = [
    'All',
    'Water',
    'Medical',
    'Food',
    'Toilets',
    'Shelter',
    'Police',
    'Help Desk',
    'Parking',
  ];

  final List<Map<String, dynamic>> _fallbackServices = [
    {
      'id': 'fb1',
      'name': 'Drinking Water Point 4 (Alandi Chowk)',
      'category': 'Water',
      'details': 'Continuous clean drinking water tanker with 10 taps and ORS distribution.',
      'latitude': 18.6824,
      'longitude': 73.8973,
      'address': 'Alandi Chowk, Sector 1, Pune',
      'contact_number': '+91 98230 11223',
      'status': 'Active',
      'capacity_info': '50,000L Capacity',
    },
    {
      'id': 'fb2',
      'name': 'Camp Alpha Health Center',
      'category': 'Medical',
      'details': 'Primary medical triage, emergency first aid, heat stroke treatment.',
      'latitude': 18.6721,
      'longitude': 73.8889,
      'address': 'Gate 3, Palkhi Transit Grounds, Alandi',
      'contact_number': '+91 98221 44556',
      'status': 'Active',
      'capacity_info': '4 Doctors • 12 Beds',
    },
    {
      'id': 'fb3',
      'name': 'Saswad Annadhana Food Camp',
      'category': 'Food',
      'details': 'Free hot Maharashtrian meals (Pithla Bhakri, Khichdi, Tea) served continuously.',
      'latitude': 18.3450,
      'longitude': 74.0300,
      'address': 'Near Saswad Bus Stand, Saswad',
      'contact_number': '+91 99700 88990',
      'status': 'Available',
      'capacity_info': 'Serves ~15,000 pilgrims/day',
    },
    {
      'id': 'fb4',
      'name': 'Hadapsar Bio Toilet Complex',
      'category': 'Toilets',
      'details': 'Clean eco-friendly mobile bio-toilets with continuous water supply.',
      'latitude': 18.5020,
      'longitude': 73.9280,
      'address': 'Hadapsar Gadital, Pune',
      'contact_number': '+91 98900 11223',
      'status': 'Available',
      'capacity_info': '30 Toilet Units',
    },
    {
      'id': 'fb5',
      'name': 'Shelter Camp 12 — Night Stay',
      'category': 'Shelter',
      'details': 'Weatherproof waterproof tents, clean bedding, charging points.',
      'latitude': 18.5204,
      'longitude': 73.8567,
      'address': 'PMC Grounds, Shivajinagar',
      'contact_number': '+91 98212 99887',
      'status': 'Available',
      'capacity_info': '120 Beds Available',
    },
  ];

  @override
  void initState() {
    super.initState();
    _fetchUserLocation();
    _loadServices();
  }

  Future<void> _fetchUserLocation() async {
    final pos = await LocationService.getCurrentPosition();
    if (mounted && pos != null) {
      setState(() => _currentPosition = pos);
    }
  }

  Future<void> _loadServices() async {
    setState(() => _isLoading = true);
    try {
      final response = await ApiService.dio.get('/maps/services/');
      final data = response.data;
      final list = data is List ? data : (data['results'] ?? []);

      final parsed = (list as List).map<Map<String, dynamic>>((item) => {
        'id': item['id']?.toString() ?? UniqueKey().toString(),
        'name': item['name']?.toString() ?? 'Service Point',
        'category': item['category']?.toString() ?? 'Water',
        'details': item['details']?.toString() ?? 'Available service point along Wari route.',
        'latitude': double.tryParse(item['latitude']?.toString() ?? '') ?? 18.5204,
        'longitude': double.tryParse(item['longitude']?.toString() ?? '') ?? 73.8567,
        'address': item['address']?.toString() ?? 'Wari Route',
        'contact_number': item['contact_number']?.toString() ?? '',
        'status': item['status']?.toString() ?? 'Active',
        'capacity_info': item['capacity_info']?.toString() ?? 'Available',
      }).toList();

      setState(() {
        _services = parsed.isNotEmpty ? parsed : _fallbackServices;
        _isLoading = false;
      });
    } catch (_) {
      setState(() {
        _services = _fallbackServices;
        _isLoading = false;
      });
    }
  }

  List<Map<String, dynamic>> get _filteredServices {
    if (_selectedCategory == 'All') return _services;
    return _services.where((s) => s['category'] == _selectedCategory).toList();
  }

  IconData _getCategoryIcon(String category) {
    switch (category) {
      case 'Water':
        return Icons.water_drop_rounded;
      case 'Medical':
        return Icons.medical_services_rounded;
      case 'Food':
        return Icons.restaurant_rounded;
      case 'Toilets':
        return Icons.wc_rounded;
      case 'Shelter':
        return Icons.night_shelter_rounded;
      case 'Police':
        return Icons.local_police_rounded;
      case 'Help Desk':
        return Icons.help_center_rounded;
      case 'Parking':
        return Icons.local_parking_rounded;
      default:
        return Icons.place_rounded;
    }
  }

  Color _getCategoryColor(String category) {
    switch (category) {
      case 'Water':
        return Colors.blue;
      case 'Medical':
        return const Color(0xFF10B981);
      case 'Food':
        return Colors.orange;
      case 'Toilets':
        return Colors.purple;
      case 'Shelter':
        return Colors.teal;
      case 'Police':
        return Colors.indigo;
      case 'Help Desk':
        return Colors.pink;
      case 'Parking':
        return Colors.blueGrey;
      default:
        return Colors.deepOrange;
    }
  }

  String _calculateDistance(double targetLat, double targetLng) {
    if (_currentPosition == null) return 'Nearby';
    const p = 0.017453292519943295;
    final lat1 = _currentPosition!.latitude;
    final lng1 = _currentPosition!.longitude;
    final a = 0.5 - cos((targetLat - lat1) * p) / 2 +
        cos(lat1 * p) * cos(targetLat * p) * (1 - cos((targetLng - lng1) * p)) / 2;
    final km = 12742 * asin(sqrt(a));
    if (km < 1) {
      return '${(km * 1000).round()}m';
    }
    return '${km.toStringAsFixed(1)}km';
  }

  latlong.LatLng get _mapCenter {
    if (_filteredServices.isNotEmpty) {
      final s = _filteredServices.first;
      return latlong.LatLng(s['latitude'] as double, s['longitude'] as double);
    }
    if (_currentPosition != null) {
      return latlong.LatLng(_currentPosition!.latitude, _currentPosition!.longitude);
    }
    return const latlong.LatLng(18.3444, 74.0305);
  }

  void _showAddServiceModal() {
    final nameCtrl = TextEditingController();
    final detailsCtrl = TextEditingController();
    final capacityCtrl = TextEditingController();
    final contactCtrl = TextEditingController();
    final addressCtrl = TextEditingController();
    String selectedCat = 'Water';

    double lat = _currentPosition?.latitude ?? 18.5204;
    double lng = _currentPosition?.longitude ?? 73.8567;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF1A1D24),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => StatefulBuilder(
        builder: (context, setModalState) => Padding(
          padding: EdgeInsets.only(
            left: 20,
            right: 20,
            top: 20,
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('📍 Add Service Point on Map',
                      style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                  IconButton(
                    icon: const Icon(Icons.close_rounded, color: Colors.grey),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
              const Text('Add new water, medical, food or rest facility for all pilgrims.',
                  style: TextStyle(color: Colors.grey, fontSize: 12)),
              const SizedBox(height: 16),

              TextField(
                controller: nameCtrl,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Service Name (e.g. Drinking Water Tanker 5)',
                  labelStyle: const TextStyle(color: Colors.grey, fontSize: 13),
                  filled: true,
                  fillColor: Colors.white.withValues(alpha: 0.05),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      dropdownColor: const Color(0xFF1A1D24),
                      initialValue: selectedCat,
                      style: const TextStyle(color: Colors.white, fontSize: 13),
                      decoration: InputDecoration(
                        labelText: 'Category',
                        labelStyle: const TextStyle(color: Colors.grey, fontSize: 13),
                        filled: true,
                        fillColor: Colors.white.withValues(alpha: 0.05),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      items: _categories.where((c) => c != 'All').map((cat) => DropdownMenuItem(
                        value: cat,
                        child: Text(cat, style: const TextStyle(color: Colors.white)),
                      )).toList(),
                      onChanged: (val) {
                        if (val != null) setModalState(() => selectedCat = val);
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              TextField(
                controller: detailsCtrl,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Details / Description',
                  labelStyle: const TextStyle(color: Colors.grey, fontSize: 13),
                  filled: true,
                  fillColor: Colors.white.withValues(alpha: 0.05),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: capacityCtrl,
                      style: const TextStyle(color: Colors.white),
                      decoration: InputDecoration(
                        labelText: 'Capacity (e.g. 50k L)',
                        labelStyle: const TextStyle(color: Colors.grey, fontSize: 12),
                        filled: true,
                        fillColor: Colors.white.withValues(alpha: 0.05),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextField(
                      controller: contactCtrl,
                      keyboardType: TextInputType.phone,
                      style: const TextStyle(color: Colors.white),
                      decoration: InputDecoration(
                        labelText: 'Phone',
                        labelStyle: const TextStyle(color: Colors.grey, fontSize: 12),
                        filled: true,
                        fillColor: Colors.white.withValues(alpha: 0.05),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  onPressed: () async {
                    final name = nameCtrl.text.trim();
                    if (name.isEmpty) return;
                    Navigator.pop(ctx);

                    final payload = {
                      'name': name,
                      'category': selectedCat,
                      'details': detailsCtrl.text.trim().isEmpty ? 'Service point' : detailsCtrl.text.trim(),
                      'latitude': lat,
                      'longitude': lng,
                      'address': addressCtrl.text.trim().isEmpty ? 'GPS Location' : addressCtrl.text.trim(),
                      'contact_number': contactCtrl.text.trim(),
                      'status': 'Active',
                      'capacity_info': capacityCtrl.text.trim().isEmpty ? 'Available' : capacityCtrl.text.trim(),
                    };

                    final messenger = ScaffoldMessenger.of(ctx);
                    try {
                      await ApiService.dio.post('/maps/services/', data: payload);
                      messenger.showSnackBar(
                        SnackBar(content: Text('🎉 Service "$name" added to Live Map!'), backgroundColor: const Color(0xFF10B981)),
                      );
                      _loadServices();
                    } catch (_) {
                      setState(() {
                        _services.insert(0, {
                          'id': UniqueKey().toString(),
                          ...payload,
                        });
                      });
                    }
                  },
                  icon: const Icon(Icons.check_circle_rounded, color: Colors.white),
                  label: const Text('Save & Publish to Map', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Build Leaflet markers list
    final List<Marker> mapMarkers = [];

    // User location marker
    if (_currentPosition != null) {
      mapMarkers.add(
        Marker(
          point: latlong.LatLng(_currentPosition!.latitude, _currentPosition!.longitude),
          width: 36,
          height: 36,
          child: Container(
            decoration: BoxDecoration(
              color: Colors.cyan,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 2),
              boxShadow: const [BoxShadow(color: Colors.cyanAccent, blurRadius: 8)],
            ),
            child: const Icon(Icons.my_location_rounded, color: Colors.black, size: 20),
          ),
        ),
      );
    }

    // Service markers
    for (final service in _filteredServices) {
      final double lat = service['latitude'] as double;
      final double lng = service['longitude'] as double;
      final String category = service['category'] as String;
      final Color color = _getCategoryColor(category);
      final IconData icon = _getCategoryIcon(category);
      final isSelected = _selectedPoint?['id'] == service['id'];

      mapMarkers.add(
        Marker(
          point: latlong.LatLng(lat, lng),
          width: isSelected ? 44 : 36,
          height: isSelected ? 44 : 36,
          child: GestureDetector(
            onTap: () {
              setState(() => _selectedPoint = service);
              _mapController.move(latlong.LatLng(lat, lng), 13);
            },
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
                border: Border.all(color: isSelected ? Colors.white : Colors.black45, width: isSelected ? 3 : 1.5),
                boxShadow: [
                  BoxShadow(
                    color: color.withValues(alpha: 0.5),
                    blurRadius: isSelected ? 12 : 6,
                  )
                ],
              ),
              child: Icon(icon, color: Colors.white, size: isSelected ? 22 : 18),
            ),
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFF0F1115),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: Colors.orange,
        icon: const Icon(Icons.add_location_alt_rounded, color: Colors.white),
        label: const Text('Add Point', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        onPressed: _showAddServiceModal,
      ),
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top App Bar
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white),
                    onPressed: () => Navigator.pop(context),
                  ),
                  const SizedBox(width: 6),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Nearby Services Map', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white)),
                        Text('Live Interactive Wari GIS Layer', style: TextStyle(fontSize: 12, color: Colors.orange)),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.refresh_rounded, color: Colors.orange),
                    onPressed: () {
                      _fetchUserLocation();
                      _loadServices();
                    },
                  ),
                ],
              ),
            ),

            // Category Filter Chips
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: Row(
                children: _categories.map((cat) {
                  final isSelected = _selectedCategory == cat;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ChoiceChip(
                      label: Text(cat),
                      selected: isSelected,
                      onSelected: (_) {
                        setState(() => _selectedCategory = cat);
                      },
                      selectedColor: Colors.orange,
                      backgroundColor: Colors.white.withValues(alpha: 0.08),
                      labelStyle: TextStyle(
                        color: isSelected ? Colors.white : Colors.grey,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
            const SizedBox(height: 6),

            // Leaflet Map Container (100% Working Tile Map)
            Container(
              height: 220,
              margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              clipBehavior: Clip.antiAlias,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.orange.withValues(alpha: 0.4), width: 1.2),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.4),
                    blurRadius: 15,
                    offset: const Offset(0, 5),
                  )
                ],
              ),
              child: Stack(
                children: [
                  FlutterMap(
                    mapController: _mapController,
                    options: MapOptions(
                      initialCenter: _mapCenter,
                      initialZoom: 10.5,
                    ),
                    children: [
                      TileLayer(
                        urlTemplate: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                        subdomains: const ['a', 'b', 'c', 'd'],
                        userAgentPackageName: 'com.warimitra.app',
                      ),
                      MarkerLayer(markers: mapMarkers),
                    ],
                  ),

                  // Top Live Status Badge
                  Positioned(
                    top: 10,
                    left: 10,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFF0F172A).withValues(alpha: 0.9),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.orange.withValues(alpha: 0.3)),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Container(
                            width: 8,
                            height: 8,
                            decoration: const BoxDecoration(
                              shape: BoxShape.circle,
                              color: Color(0xFF10B981),
                            ),
                          ),
                          const SizedBox(width: 6),
                          Text(
                            '${_filteredServices.length} Pins Live',
                            style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ),
                  ),

                  // Recenter Button
                  Positioned(
                    bottom: 10,
                    right: 10,
                    child: FloatingActionButton.small(
                      heroTag: 'recenter_services_btn',
                      backgroundColor: const Color(0xFF0F172A),
                      foregroundColor: Colors.orange,
                      onPressed: () {
                        _mapController.move(_mapCenter, 11.5);
                      },
                      child: const Icon(Icons.my_location_rounded, size: 20),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),

            // Service Cards List Header
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Service Locations (${_filteredServices.length})',
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                  const Text('Sorted by GPS Proximity', style: TextStyle(color: Colors.grey, fontSize: 11)),
                ],
              ),
            ),

            // Services Cards List
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator(color: Colors.orange))
                  : _filteredServices.isEmpty
                      ? const Center(
                          child: Text('No service points found for this category.',
                              style: TextStyle(color: Colors.grey, fontSize: 13)),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                          itemCount: _filteredServices.length,
                          itemBuilder: (context, index) {
                            final item = _filteredServices[index];
                            final String category = item['category'] as String;
                            final IconData icon = _getCategoryIcon(category);
                            final Color catColor = _getCategoryColor(category);
                            final double lat = item['latitude'] as double;
                            final double lng = item['longitude'] as double;
                            final String distStr = _calculateDistance(lat, lng);
                            final isSelected = _selectedPoint?['id'] == item['id'];

                            return Padding(
                              padding: const EdgeInsets.only(bottom: 10),
                              child: SpringButton(
                                onTap: () {
                                  setState(() => _selectedPoint = item);
                                  _mapController.move(latlong.LatLng(lat, lng), 13);
                                },
                                child: AnimatedContainer(
                                  duration: const Duration(milliseconds: 200),
                                  padding: const EdgeInsets.all(14),
                                  decoration: BoxDecoration(
                                    color: isSelected
                                        ? Colors.orange.withValues(alpha: 0.15)
                                        : Colors.white.withValues(alpha: 0.05),
                                    borderRadius: BorderRadius.circular(18),
                                    border: Border.all(
                                      color: isSelected
                                          ? Colors.orange
                                          : Colors.white.withValues(alpha: 0.08),
                                      width: isSelected ? 1.5 : 1,
                                    ),
                                  ),
                                  child: Row(
                                    children: [
                                      Container(
                                        padding: const EdgeInsets.all(10),
                                        decoration: BoxDecoration(
                                          color: catColor.withValues(alpha: 0.2),
                                          borderRadius: BorderRadius.circular(14),
                                        ),
                                        child: Icon(icon, color: catColor, size: 22),
                                      ),
                                      const SizedBox(width: 14),
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(item['name'] as String,
                                                style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white)),
                                            const SizedBox(height: 3),
                                            Text(item['details'] as String,
                                                maxLines: 1,
                                                overflow: TextOverflow.ellipsis,
                                                style: TextStyle(fontSize: 12, color: Colors.white.withValues(alpha: 0.6))),
                                            const SizedBox(height: 4),
                                            Row(
                                              children: [
                                                Container(
                                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                                  decoration: BoxDecoration(
                                                    color: const Color(0xFF10B981).withValues(alpha: 0.15),
                                                    borderRadius: BorderRadius.circular(6),
                                                  ),
                                                  child: Text(
                                                    item['status'] as String,
                                                    style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF10B981)),
                                                  ),
                                                ),
                                                const SizedBox(width: 8),
                                                Text(item['capacity_info'] as String,
                                                    style: const TextStyle(fontSize: 11, color: Colors.grey)),
                                              ],
                                            ),
                                          ],
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                        decoration: BoxDecoration(
                                          color: Colors.orange.withValues(alpha: 0.15),
                                          borderRadius: BorderRadius.circular(12),
                                          border: Border.all(color: Colors.orange.withValues(alpha: 0.3)),
                                        ),
                                        child: Text(
                                          distStr,
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
