import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart' as latlong;
import 'package:geolocator/geolocator.dart';
import '../theme/app_theme.dart';
import '../widgets/spring_button.dart';
import '../services/api_service.dart';
import '../services/location_service.dart';

class SanitationScreen extends StatefulWidget {
  const SanitationScreen({super.key});

  @override
  State<SanitationScreen> createState() => _SanitationScreenState();
}

class _SanitationScreenState extends State<SanitationScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<Map<String, dynamic>> _toilets = [];
  List<Map<String, dynamic>> _wasteReports = [];
  bool _isLoading = true;
  Position? _currentPosition;
  final MapController _mapController = MapController();
  Map<String, dynamic>? _selectedItem;

  final List<Map<String, dynamic>> _fallbackToilets = [
    {
      'id': '1',
      'name': 'Alandi Sector 1 Bio-Toilet Complex',
      'location': 'Alandi Chowk, Sector 1, Pune',
      'gender_type': 'Unisex',
      'cleanliness_score': 92,
      'is_water_available': true,
      'latitude': 18.6824,
      'longitude': 73.8973,
    },
    {
      'id': '2',
      'name': 'Camp Alpha Mobile Restroom Trailer',
      'location': 'Gate 3, Palkhi Grounds, Alandi',
      'gender_type': 'Accessible',
      'cleanliness_score': 88,
      'is_water_available': true,
      'latitude': 18.6721,
      'longitude': 73.8889,
    },
    {
      'id': '3',
      'name': 'Hadapsar Gadital Sanitation Hub',
      'location': 'Hadapsar Gadital Junction, Pune',
      'gender_type': 'Unisex',
      'cleanliness_score': 85,
      'is_water_available': true,
      'latitude': 18.5020,
      'longitude': 73.9280,
    },
    {
      'id': '4',
      'name': 'Dive Ghat Emergency Mobile Toilets',
      'location': 'Dive Ghat Slope Corridor',
      'gender_type': 'Unisex',
      'cleanliness_score': 95,
      'is_water_available': true,
      'latitude': 18.3444,
      'longitude': 74.0305,
    },
    {
      'id': '5',
      'name': 'Saswad Bus Stand Sanitation Complex',
      'location': 'Near Saswad Bus Stand, Saswad',
      'gender_type': 'Unisex',
      'cleanliness_score': 78,
      'is_water_available': true,
      'latitude': 18.3450,
      'longitude': 74.0300,
    },
  ];

  final List<Map<String, dynamic>> _fallbackWasteReports = [
    {
      'id': 'w1',
      'location_name': 'Alandi Gate 2 Pilgrimage Path',
      'waste_type': 'Overflowing Bin',
      'description': 'Plastic bottles and paper waste overflowing near tea stalls.',
      'status': 'PENDING',
      'latitude': 18.6750,
      'longitude': 73.8920,
      'image_url': '',
    },
    {
      'id': 'w2',
      'location_name': 'Saswad Halt Grounds Sector B',
      'waste_type': 'Plastic Waste',
      'description': 'Accumulation of disposable food packets after lunch distribution.',
      'status': 'CLEANING_DISPATCHED',
      'latitude': 18.3430,
      'longitude': 74.0290,
      'image_url': '',
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _fetchUserLocation();
    _loadSanitationData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _fetchUserLocation() async {
    final pos = await LocationService.getCurrentPosition();
    if (mounted && pos != null) {
      setState(() => _currentPosition = pos);
    }
  }

  Future<void> _loadSanitationData() async {
    setState(() => _isLoading = true);
    try {
      final futures = await Future.wait([
        ApiService.dio.get('/sanitation/toilets/'),
        ApiService.dio.get('/sanitation/waste-reports/'),
      ]);

      final toiletsData = futures[0].data;
      final wasteData = futures[1].data;

      final toiletList = toiletsData is List ? toiletsData : (toiletsData['results'] ?? []);
      final wasteList = wasteData is List ? wasteData : (wasteData['results'] ?? []);

      final parsedToilets = (toiletList as List).map<Map<String, dynamic>>((t) => {
        'id': t['id']?.toString() ?? UniqueKey().toString(),
        'name': t['name']?.toString() ?? 'Public Toilet',
        'location': t['location']?.toString() ?? 'Wari Route',
        'gender_type': t['gender_type']?.toString() ?? 'Unisex',
        'cleanliness_score': t['cleanliness_score'] ?? 85,
        'is_water_available': t['is_water_available'] ?? true,
        'latitude': double.tryParse(t['latitude']?.toString() ?? '') ?? 18.5204,
        'longitude': double.tryParse(t['longitude']?.toString() ?? '') ?? 73.8567,
      }).toList();

      final parsedWaste = (wasteList as List).map<Map<String, dynamic>>((w) => {
        'id': w['id']?.toString() ?? UniqueKey().toString(),
        'location_name': w['location_name']?.toString() ?? 'Wari Path',
        'waste_type': w['waste_type']?.toString() ?? 'Garbage Issue',
        'description': w['description']?.toString() ?? 'Sanitation report',
        'status': w['status']?.toString() ?? 'PENDING',
        'image_url': w['image_url']?.toString() ?? (w['image']?.toString() ?? ''),
        'latitude': double.tryParse(w['latitude']?.toString() ?? '') ?? 18.5204,
        'longitude': double.tryParse(w['longitude']?.toString() ?? '') ?? 73.8567,
      }).toList();

      setState(() {
        _toilets = parsedToilets.isNotEmpty ? parsedToilets : _fallbackToilets;
        _wasteReports = parsedWaste.isNotEmpty ? parsedWaste : _fallbackWasteReports;
        _isLoading = false;
      });
    } catch (_) {
      setState(() {
        _toilets = _fallbackToilets;
        _wasteReports = _fallbackWasteReports;
        _isLoading = false;
      });
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
    if (_toilets.isNotEmpty) {
      final t = _toilets.first;
      return latlong.LatLng(t['latitude'] as double, t['longitude'] as double);
    }
    if (_currentPosition != null) {
      return latlong.LatLng(_currentPosition!.latitude, _currentPosition!.longitude);
    }
    return const latlong.LatLng(18.3444, 74.0305);
  }

  void _showReportWasteModal() {
    final locationCtrl = TextEditingController();
    final descCtrl = TextEditingController();
    final imageUrlCtrl = TextEditingController();
    String selectedType = 'Overflowing Bin';

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
                  const Text('🚨 Report Sanitation / Waste Issue',
                      style: TextStyle(color: Colors.white, fontSize: 17, fontWeight: FontWeight.bold)),
                  IconButton(
                    icon: const Icon(Icons.close_rounded, color: Colors.grey),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
              const Text('Notify cleaning crews of overflowing bins or unhygienic spots.',
                  style: TextStyle(color: Colors.grey, fontSize: 12)),
              const SizedBox(height: 14),

              DropdownButtonFormField<String>(
                dropdownColor: const Color(0xFF1A1D24),
                initialValue: selectedType,
                style: const TextStyle(color: Colors.white, fontSize: 13),
                decoration: InputDecoration(
                  labelText: 'Waste Issue Type',
                  labelStyle: const TextStyle(color: Colors.grey, fontSize: 13),
                  filled: true,
                  fillColor: Colors.white.withValues(alpha: 0.05),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
                items: [
                  'Overflowing Bin',
                  'Plastic Waste Accumulation',
                  'Unhygienic Public Toilet',
                  'Organic Waste / Food Remnants',
                  'Sewage / Water Leakage',
                ].map((type) => DropdownMenuItem(
                  value: type,
                  child: Text(type, style: const TextStyle(color: Colors.white)),
                )).toList(),
                onChanged: (val) {
                  if (val != null) setModalState(() => selectedType = val);
                },
              ),
              const SizedBox(height: 12),

              TextField(
                controller: locationCtrl,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Location Name / Landmark (e.g. Gate 2 Tea Stalls)',
                  labelStyle: const TextStyle(color: Colors.grey, fontSize: 13),
                  filled: true,
                  fillColor: Colors.white.withValues(alpha: 0.05),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 12),

              TextField(
                controller: descCtrl,
                maxLines: 2,
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

              TextField(
                controller: imageUrlCtrl,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Image URL / Attachment (Optional)',
                  labelStyle: const TextStyle(color: Colors.grey, fontSize: 13),
                  hintText: 'https://... or photo URL',
                  hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.3)),
                  filled: true,
                  fillColor: Colors.white.withValues(alpha: 0.05),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 16),

              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.teal,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  onPressed: () async {
                    final loc = locationCtrl.text.trim();
                    if (loc.isEmpty) return;
                    Navigator.pop(ctx);

                    final payload = {
                      'location_name': loc,
                      'waste_type': selectedType,
                      'description': descCtrl.text.trim().isEmpty ? 'Sanitation report' : descCtrl.text.trim(),
                      'image_url': imageUrlCtrl.text.trim(),
                      'status': 'PENDING',
                      'latitude': lat,
                      'longitude': lng,
                    };

                    final messenger = ScaffoldMessenger.of(ctx);
                    try {
                      await ApiService.dio.post('/sanitation/waste-reports/', data: payload);
                      messenger.showSnackBar(
                        const SnackBar(
                          content: Text('🎉 Sanitation issue reported! Crew dispatched.'),
                          backgroundColor: Color(0xFF10B981),
                        ),
                      );
                      _loadSanitationData();
                    } catch (_) {
                      setState(() {
                        _wasteReports.insert(0, {
                          'id': UniqueKey().toString(),
                          ...payload,
                        });
                      });
                    }
                  },
                  icon: const Icon(Icons.send_rounded, color: Colors.white),
                  label: const Text('Submit Report', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
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
    // Map Markers with Reduced Size for Sleek Display
    final List<Marker> markers = [];

    // Current user position marker
    if (_currentPosition != null) {
      markers.add(
        Marker(
          point: latlong.LatLng(_currentPosition!.latitude, _currentPosition!.longitude),
          width: 24,
          height: 24,
          child: Container(
            decoration: BoxDecoration(
              color: Colors.blueAccent,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 2),
              boxShadow: const [BoxShadow(color: Colors.blueAccent, blurRadius: 4)],
            ),
            child: const Icon(Icons.my_location_rounded, color: Colors.white, size: 13),
          ),
        ),
      );
    }

    // Toilet Markers (Purple - Reduced Size: 22px / 28px selected)
    for (final toilet in _toilets) {
      final double lat = toilet['latitude'] as double;
      final double lng = toilet['longitude'] as double;
      final isSelected = _selectedItem?['id'] == toilet['id'];

      markers.add(
        Marker(
          point: latlong.LatLng(lat, lng),
          width: isSelected ? 28 : 22,
          height: isSelected ? 28 : 22,
          child: GestureDetector(
            onTap: () {
              setState(() => _selectedItem = toilet);
              _mapController.move(latlong.LatLng(lat, lng), 13);
            },
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              decoration: BoxDecoration(
                color: Colors.purple,
                shape: BoxShape.circle,
                border: Border.all(color: isSelected ? Colors.tealAccent : Colors.white, width: isSelected ? 2.5 : 1.2),
                boxShadow: const [BoxShadow(color: Colors.purpleAccent, blurRadius: 4)],
              ),
              child: Icon(Icons.wc_rounded, color: Colors.white, size: isSelected ? 15 : 12),
            ),
          ),
        ),
      );
    }

    // Waste Report Markers (Orange/Red - Reduced Size: 22px / 28px selected)
    for (final report in _wasteReports) {
      final double lat = report['latitude'] as double;
      final double lng = report['longitude'] as double;
      final isSelected = _selectedItem?['id'] == report['id'];

      markers.add(
        Marker(
          point: latlong.LatLng(lat, lng),
          width: isSelected ? 28 : 22,
          height: isSelected ? 28 : 22,
          child: GestureDetector(
            onTap: () {
              setState(() => _selectedItem = report);
              _mapController.move(latlong.LatLng(lat, lng), 13);
            },
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              decoration: BoxDecoration(
                color: Colors.deepOrange,
                shape: BoxShape.circle,
                border: Border.all(color: isSelected ? Colors.amberAccent : Colors.white, width: isSelected ? 2.5 : 1.2),
                boxShadow: const [BoxShadow(color: Colors.deepOrangeAccent, blurRadius: 4)],
              ),
              child: Icon(Icons.warning_amber_rounded, color: Colors.white, size: isSelected ? 15 : 12),
            ),
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: Colors.teal,
        icon: const Icon(Icons.add_alert_rounded, color: Colors.white),
        label: const Text('Report Waste Issue', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        onPressed: _showReportWasteModal,
      ),
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // App Bar Header
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
              child: Row(
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
                  const SizedBox(width: 8),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('स्वच्छतागृह व कचरा व्यवस्थापन', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                        Text('Public Toilet & Waste Map (Light GIS)', style: TextStyle(fontSize: 11, color: Colors.tealAccent, fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.refresh_rounded, color: Colors.tealAccent),
                    onPressed: () {
                      _fetchUserLocation();
                      _loadSanitationData();
                    },
                  ),
                ],
              ),
            ),

            // Light Theme Map Container (CartoDB Voyager Light Map Tiles)
            Container(
              height: 210,
              margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              clipBehavior: Clip.antiAlias,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.teal.withValues(alpha: 0.4), width: 1.2),
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
                      // CartoDB Voyager Light Theme Map Tiles
                      TileLayer(
                        urlTemplate: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
                        subdomains: const ['a', 'b', 'c', 'd'],
                        userAgentPackageName: 'com.warimitra.app',
                      ),
                      MarkerLayer(markers: markers),
                    ],
                  ),

                  // Top Status Badge Overlay
                  Positioned(
                    top: 10,
                    left: 10,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFF0F172A).withValues(alpha: 0.92),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.teal.withValues(alpha: 0.3)),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Container(
                            width: 8,
                            height: 8,
                            decoration: const BoxDecoration(
                              shape: BoxShape.circle,
                              color: Colors.tealAccent,
                            ),
                          ),
                          const SizedBox(width: 6),
                          Text(
                            '${_toilets.length} Toilets • ${_wasteReports.length} Issues',
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
                      heroTag: 'recenter_sanitation_btn',
                      backgroundColor: const Color(0xFF0F172A),
                      foregroundColor: Colors.tealAccent,
                      onPressed: () {
                        _mapController.move(_mapCenter, 11.5);
                      },
                      child: const Icon(Icons.my_location_rounded, size: 20),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 6),

            // Tab Bar
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 16),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(14),
              ),
              child: TabBar(
                controller: _tabController,
                indicatorColor: Colors.tealAccent,
                indicatorWeight: 3,
                labelColor: Colors.tealAccent,
                unselectedLabelColor: Colors.grey,
                labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                tabs: [
                  Tab(text: '🚽 Public Toilets (${_toilets.length})'),
                  Tab(text: '🚨 Waste Reports (${_wasteReports.length})'),
                ],
              ),
            ),

            // Tab Bar View Lists
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator(color: Colors.teal))
                  : TabBarView(
                      controller: _tabController,
                      children: [
                        // 1. Toilets List Tab
                        _toilets.isEmpty
                            ? const Center(child: Text('No sanitation facilities listed', style: TextStyle(color: Colors.grey)))
                            : ListView.builder(
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                                itemCount: _toilets.length,
                                itemBuilder: (context, index) {
                                  final toilet = _toilets[index];
                                  final double lat = toilet['latitude'] as double;
                                  final double lng = toilet['longitude'] as double;
                                  final String distStr = _calculateDistance(lat, lng);
                                  final score = toilet['cleanliness_score'] ?? 85;
                                  final hasWater = toilet['is_water_available'] ?? true;
                                  final genderType = toilet['gender_type'] ?? 'Unisex';
                                  final isSelected = _selectedItem?['id'] == toilet['id'];

                                  return Padding(
                                    padding: const EdgeInsets.only(bottom: 10),
                                    child: SpringButton(
                                      onTap: () {
                                        setState(() => _selectedItem = toilet);
                                        _mapController.move(latlong.LatLng(lat, lng), 13);
                                      },
                                      child: Container(
                                        padding: const EdgeInsets.all(14),
                                        decoration: BoxDecoration(
                                          color: isSelected
                                              ? Colors.teal.withValues(alpha: 0.15)
                                              : AppTheme.surfaceDark,
                                          borderRadius: BorderRadius.circular(18),
                                          border: Border.all(
                                            color: isSelected
                                                ? Colors.tealAccent
                                                : Colors.white.withValues(alpha: 0.08),
                                            width: isSelected ? 1.5 : 1,
                                          ),
                                        ),
                                        child: Row(
                                          children: [
                                            CircleAvatar(
                                              backgroundColor: Colors.purple.withValues(alpha: 0.2),
                                              child: const Icon(Icons.wc_rounded, color: Colors.purpleAccent),
                                            ),
                                            const SizedBox(width: 12),
                                            Expanded(
                                              child: Column(
                                                crossAxisAlignment: CrossAxisAlignment.start,
                                                children: [
                                                  Text(toilet['name']?.toString() ?? 'Toilet',
                                                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                                                  const SizedBox(height: 2),
                                                  Text(toilet['location']?.toString() ?? '',
                                                      style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 11)),
                                                  const SizedBox(height: 4),
                                                  Row(
                                                    children: [
                                                      _buildChip('$score% Clean', Colors.teal),
                                                      const SizedBox(width: 6),
                                                      _buildChip(genderType, Colors.purple),
                                                      if (hasWater) ...[
                                                        const SizedBox(width: 6),
                                                        _buildChip('Water ✓', Colors.blue),
                                                      ],
                                                    ],
                                                  ),
                                                ],
                                              ),
                                            ),
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                              decoration: BoxDecoration(
                                                color: Colors.teal.withValues(alpha: 0.15),
                                                borderRadius: BorderRadius.circular(10),
                                              ),
                                              child: Text(distStr,
                                                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.tealAccent)),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ),
                                  );
                                },
                              ),

                        // 2. Waste Reports Tab
                        _wasteReports.isEmpty
                            ? const Center(child: Text('No waste reports submitted', style: TextStyle(color: Colors.grey)))
                            : ListView.builder(
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                                itemCount: _wasteReports.length,
                                itemBuilder: (context, index) {
                                  final report = _wasteReports[index];
                                  final double lat = report['latitude'] as double;
                                  final double lng = report['longitude'] as double;
                                  final String distStr = _calculateDistance(lat, lng);
                                  final String status = report['status'] ?? 'PENDING';
                                  final String imgUrl = report['image_url'] ?? '';
                                  final isSelected = _selectedItem?['id'] == report['id'];

                                  Color statusColor = Colors.orange;
                                  if (status == 'CLEANED') statusColor = const Color(0xFF10B981);
                                  if (status == 'CLEANING_DISPATCHED') statusColor = Colors.blue;

                                  return Padding(
                                    padding: const EdgeInsets.only(bottom: 10),
                                    child: SpringButton(
                                      onTap: () {
                                        setState(() => _selectedItem = report);
                                        _mapController.move(latlong.LatLng(lat, lng), 13);
                                      },
                                      child: Container(
                                        padding: const EdgeInsets.all(14),
                                        decoration: BoxDecoration(
                                          color: isSelected
                                              ? Colors.deepOrange.withValues(alpha: 0.15)
                                              : AppTheme.surfaceDark,
                                          borderRadius: BorderRadius.circular(18),
                                          border: Border.all(
                                            color: isSelected
                                                ? Colors.deepOrangeAccent
                                                : Colors.white.withValues(alpha: 0.08),
                                            width: isSelected ? 1.5 : 1,
                                          ),
                                        ),
                                        child: Row(
                                          children: [
                                            CircleAvatar(
                                              backgroundColor: Colors.deepOrange.withValues(alpha: 0.2),
                                              child: const Icon(Icons.warning_amber_rounded, color: Colors.deepOrangeAccent),
                                            ),
                                            const SizedBox(width: 12),
                                            Expanded(
                                              child: Column(
                                                crossAxisAlignment: CrossAxisAlignment.start,
                                                children: [
                                                  Text(report['location_name']?.toString() ?? 'Waste Issue',
                                                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                                                  const SizedBox(height: 2),
                                                  Text(report['waste_type']?.toString() ?? '',
                                                      style: const TextStyle(color: Colors.orangeAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                                                  const SizedBox(height: 3),
                                                  Text(report['description']?.toString() ?? '',
                                                      maxLines: 1,
                                                      overflow: TextOverflow.ellipsis,
                                                      style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 11)),
                                                  const SizedBox(height: 4),
                                                  Row(
                                                    children: [
                                                      _buildChip(status, statusColor),
                                                      if (imgUrl.isNotEmpty) ...[
                                                        const SizedBox(width: 6),
                                                        _buildChip('📷 Photo Attached', Colors.cyan),
                                                      ],
                                                    ],
                                                  ),
                                                ],
                                              ),
                                            ),
                                            Text(distStr, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.orange)),
                                          ],
                                        ),
                                      ),
                                    ),
                                  );
                                },
                              ),
                      ],
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChip(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(color: color.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(6)),
      child: Text(label, style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }
}
