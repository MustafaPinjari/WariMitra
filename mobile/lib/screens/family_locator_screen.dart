import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/location_service.dart';

class FamilyLocatorScreen extends StatefulWidget {
  const FamilyLocatorScreen({Key? key}) : super(key: key);

  @override
  State<FamilyLocatorScreen> createState() => _FamilyLocatorScreenState();
}

class _FamilyLocatorScreenState extends State<FamilyLocatorScreen> {
  List<dynamic> _members = [];
  List<dynamic> _groups = [];
  bool _isLoading = true;
  bool _isUpdatingLocation = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final futures = await Future.wait([
        ApiService.dio.get('/pilgrims/families/'),
        ApiService.dio.get('/pilgrims/family-locations/'),
      ]);
      final groupData = futures[0].data;
      final locationData = futures[1].data;
      setState(() {
        _groups = groupData is List ? groupData : (groupData['results'] ?? []);
        _members = locationData is List ? locationData : (locationData['results'] ?? []);
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _shareMyLocation() async {
    setState(() => _isUpdatingLocation = true);
    await LocationService.updateBackendLocation();
    setState(() => _isUpdatingLocation = false);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('📍 Your location shared with family group!'), backgroundColor: Color(0xFF10B981)),
      );
    }
    _loadData(); // Refresh to show updated location
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
                            Text('Family & Dindi Locator', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white)),
                            Text('Consent-Based GPS Sharing', style: TextStyle(fontSize: 12, color: Colors.blueAccent)),
                          ],
                        ),
                      ),
                      IconButton(icon: const Icon(Icons.refresh_rounded, color: Colors.blueAccent), onPressed: _loadData),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Share location button
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _isUpdatingLocation ? null : _shareMyLocation,
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.blue.shade700),
                      icon: _isUpdatingLocation
                          ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                          : const Icon(Icons.my_location_rounded),
                      label: const Text('Share My Location Now'),
                    ),
                  ),

                  // Family groups
                  if (_groups.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    ..._groups.map((group) => Container(
                      padding: const EdgeInsets.all(14),
                      margin: const EdgeInsets.only(bottom: 8),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(colors: [Colors.blue.withValues(alpha: 0.15), Colors.purple.withValues(alpha: 0.1)]),
                        borderRadius: BorderRadius.circular(18),
                        border: Border.all(color: Colors.blue.withValues(alpha: 0.3)),
                      ),
                      child: Row(
                        children: [
                          const CircleAvatar(backgroundColor: Colors.blue, child: Icon(Icons.groups_rounded, color: Colors.white)),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(group['name']?.toString() ?? 'Family Group', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                                Text('Group members • Tracking Active', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                              ],
                            ),
                          ),
                        ],
                      ),
                    )),
                  ] else ...[
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: Colors.blue.withValues(alpha: 0.08),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.blue.withValues(alpha: 0.2)),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.info_outline_rounded, color: Colors.blueAccent),
                          SizedBox(width: 10),
                          Expanded(
                            child: Text('No family groups found. Create one to track members.',
                              style: TextStyle(color: Colors.white70, fontSize: 12)),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),

            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 20),
              child: Text('Member Locations', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            ),
            const SizedBox(height: 12),

            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator(color: Colors.blue))
                  : _members.isEmpty
                      ? Padding(
                          padding: const EdgeInsets.all(20),
                          child: Container(
                            padding: const EdgeInsets.all(20),
                            decoration: BoxDecoration(
                              color: Colors.white.withValues(alpha: 0.04),
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: const Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.location_off_rounded, color: Colors.grey, size: 40),
                                SizedBox(height: 8),
                                Text('No family members have shared their location yet.',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(color: Colors.grey, fontSize: 13)),
                              ],
                            ),
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 20),
                          itemCount: _members.length,
                          itemBuilder: (context, index) {
                            final member = _members[index];
                            final battery = member['battery_level'];
                            final lat = member['latitude']?.toString() ?? '?';
                            final lng = member['longitude']?.toString() ?? '?';
                            return _buildMemberTile(
                              member['full_name']?.toString() ?? member['username'] ?? 'Unknown',
                              'GPS: $lat, $lng',
                              battery != null ? '$battery%' : 'N/A',
                              const Color(0xFF10B981),
                            );
                          },
                        ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMemberTile(String name, String location, String battery, Color statusColor) {
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
          CircleAvatar(
            backgroundColor: statusColor.withValues(alpha: 0.2),
            child: Icon(Icons.person_rounded, color: statusColor),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                const SizedBox(height: 2),
                Text(location, style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 11)),
              ],
            ),
          ),
          Row(
            children: [
              Icon(Icons.battery_std_rounded, size: 16, color: Colors.white.withValues(alpha: 0.5)),
              Text(battery, style: TextStyle(color: Colors.white.withValues(alpha: 0.7), fontSize: 12, fontWeight: FontWeight.bold)),
            ],
          ),
        ],
      ),
    );
  }
}
