import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import '../services/api_service.dart';
import '../services/location_service.dart';

class FamilyLocatorScreen extends StatefulWidget {
  const FamilyLocatorScreen({super.key});

  @override
  State<FamilyLocatorScreen> createState() => _FamilyLocatorScreenState();
}

class _FamilyLocatorScreenState extends State<FamilyLocatorScreen> {
  List<dynamic> _members = [];
  List<dynamic> _groups = [];
  bool _isLoading = true;
  bool _isUpdatingLocation = false;
  bool _isAutoSharing = false;

  Position? _currentPosition;
  GoogleMapController? _mapController;
  final Set<Marker> _markers = {};

  @override
  void initState() {
    super.initState();
    _isAutoSharing = LocationService.isAutoSharing;
    _loadData();
    _fetchUserLocation();
  }

  @override
  void dispose() {
    super.dispose();
  }

  Future<void> _fetchUserLocation() async {
    final pos = await LocationService.getCurrentPosition();
    if (mounted && pos != null) {
      setState(() => _currentPosition = pos);
      _updateMapMarkers();
    }
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

      final groupsList = groupData is List ? groupData : (groupData['results'] ?? []);
      final membersList = locationData is List ? locationData : (locationData['results'] ?? []);

      setState(() {
        _groups = groupsList;
        _members = membersList;
        _isLoading = false;
      });

      _updateMapMarkers();
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _updateMapMarkers() {
    final Set<Marker> newMarkers = {};

    // 1. Add current user position marker if available
    if (_currentPosition != null) {
      newMarkers.add(
        Marker(
          markerId: const MarkerId('my_location'),
          position: LatLng(_currentPosition!.latitude, _currentPosition!.longitude),
          infoWindow: const InfoWindow(
            title: 'माझे स्थान • My Location',
            snippet: 'You are here',
          ),
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueCyan),
        ),
      );
    }

    // 2. Add family members markers
    for (int i = 0; i < _members.length; i++) {
      final member = _members[i];
      final double? lat = double.tryParse(member['latitude']?.toString() ?? '');
      final double? lng = double.tryParse(member['longitude']?.toString() ?? '');
      final String name = member['full_name']?.toString() ?? member['username'] ?? 'Family Member';
      final int batteryVal = member['battery_level'] ?? 85;

      if (lat != null && lng != null) {
        newMarkers.add(
          Marker(
            markerId: MarkerId('member_${member['user'] ?? i}'),
            position: LatLng(lat, lng),
            infoWindow: InfoWindow(
              title: name,
              snippet: '🔋 Battery: $batteryVal% • ${_getRelativeTime(member['updated_at'])}',
            ),
            icon: BitmapDescriptor.defaultMarkerWithHue(
              i == 0 ? BitmapDescriptor.hueAzure : BitmapDescriptor.hueOrange,
            ),
          ),
        );
      }
    }

    setState(() {
      _markers.clear();
      _markers.addAll(newMarkers);
    });
  }

  void _toggleAutoSharing(bool value) {
    LocationService.toggleAutoSharing(value);
    setState(() => _isAutoSharing = LocationService.isAutoSharing);

    if (value) {
      _shareMyLocation(silent: true);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('⚡ Live location sharing active globally (persists across screens)'),
            backgroundColor: Color(0xFF10B981),
            duration: Duration(seconds: 3),
          ),
        );
      }
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('⏸ Live location sharing paused'),
            backgroundColor: Colors.orange,
            duration: Duration(seconds: 2),
          ),
        );
      }
    }
  }

  Future<void> _shareMyLocation({bool silent = false}) async {
    if (!silent) setState(() => _isUpdatingLocation = true);
    await LocationService.updateBackendLocation();
    await _fetchUserLocation();
    if (!silent) setState(() => _isUpdatingLocation = false);

    if (!silent && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('📍 Your location updated and shared with family!'),
          backgroundColor: Color(0xFF10B981),
        ),
      );
    }
    _loadData();
  }

  void _showCreateGroupDialog() {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1A1D24),
        title: const Text('Create Family Group', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Create a family or dindi group to track each other live during Wari.', style: TextStyle(color: Colors.grey, fontSize: 12)),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                labelText: 'Group Name (e.g. Pawar Family Wari)',
                labelStyle: const TextStyle(color: Colors.grey),
                filled: true,
                fillColor: Colors.white.withValues(alpha: 0.05),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
            onPressed: () async {
              final name = controller.text.trim();
              if (name.isEmpty) return;
              Navigator.pop(ctx);
              try {
                final response = await ApiService.dio.post('/pilgrims/families/', data: {'name': name});
                final code = response.data['invite_code'];
                if (mounted) {
                  _showInviteCodeDialog(name, code ?? 'CREATED');
                  _loadData();
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error: ${ApiService.errorMessage(e)}'), backgroundColor: Colors.red),
                  );
                }
              }
            },
            child: const Text('Create Group'),
          ),
        ],
      ),
    );
  }

  void _showJoinGroupDialog() {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1A1D24),
        title: const Text('Join Family Group', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Enter the 6-character Invite Code shared by your family group admin.', style: TextStyle(color: Colors.grey, fontSize: 12)),
            const SizedBox(height: 14),
            TextField(
              controller: controller,
              textCapitalization: TextCapitalization.characters,
              maxLength: 6,
              style: const TextStyle(color: Colors.white, fontSize: 18, letterSpacing: 3, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
              decoration: InputDecoration(
                hintText: 'CODE12',
                hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.3)),
                filled: true,
                fillColor: Colors.white.withValues(alpha: 0.05),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.green.shade700),
            onPressed: () async {
              final code = controller.text.trim().toUpperCase();
              if (code.isEmpty) return;
              Navigator.pop(ctx);
              try {
                final response = await ApiService.dio.post('/pilgrims/families/join/', data: {'invite_code': code});
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('🎉 ${response.data['message']}'), backgroundColor: const Color(0xFF10B981)),
                  );
                  _loadData();
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('⚠️ ${ApiService.errorMessage(e)}'), backgroundColor: Colors.red),
                  );
                }
              }
            },
            child: const Text('Join Group'),
          ),
        ],
      ),
    );
  }

  void _showInviteCodeDialog(String groupName, String code) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1A1D24),
        title: Text('🎉 $groupName Created!', style: const TextStyle(color: Colors.white)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Share this 6-character code with your family members so they can join:', style: TextStyle(color: Colors.grey, fontSize: 13)),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              decoration: BoxDecoration(
                color: Colors.blueAccent.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: Colors.blueAccent),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(code, style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold, letterSpacing: 4)),
                  const SizedBox(width: 12),
                  IconButton(
                    icon: const Icon(Icons.copy_rounded, color: Colors.blueAccent),
                    onPressed: () {
                      Clipboard.setData(ClipboardData(text: code));
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Invite code copied to clipboard!')),
                      );
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Done'),
          ),
        ],
      ),
    );
  }

  LatLng get _mapCenter {
    if (_members.isNotEmpty) {
      final double? lat = double.tryParse(_members[0]['latitude']?.toString() ?? '');
      final double? lng = double.tryParse(_members[0]['longitude']?.toString() ?? '');
      if (lat != null && lng != null) return LatLng(lat, lng);
    }
    if (_currentPosition != null) {
      return LatLng(_currentPosition!.latitude, _currentPosition!.longitude);
    }
    return const LatLng(18.3444, 74.0305);
  }

  String _getRelativeTime(String? dateTimeStr) {
    if (dateTimeStr == null) return 'Unknown';
    final dt = DateTime.tryParse(dateTimeStr)?.toLocal();
    if (dt == null) return 'Unknown';
    final diff = DateTime.now().difference(dt);
    if (diff.inSeconds < 45) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
  }

  String _getDistanceString(double? targetLat, double? targetLng) {
    if (_currentPosition == null || targetLat == null || targetLng == null) {
      return 'Location synced';
    }
    const p = 0.017453292519943295;
    final lat1 = _currentPosition!.latitude;
    final lng1 = _currentPosition!.longitude;
    final a = 0.5 - cos((targetLat - lat1) * p) / 2 +
        cos(lat1 * p) * cos(targetLat * p) * (1 - cos((targetLng - lng1) * p)) / 2;
    final km = 12742 * asin(sqrt(a));
    if (km < 1) {
      return '${(km * 1000).round()} meters away';
    }
    return '${km.toStringAsFixed(1)} km away';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F1115),
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
                        Text('Family & Dindi Locator', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white)),
                        Text('Consent-Based Live GPS Sharing', style: TextStyle(fontSize: 12, color: Colors.blueAccent)),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.refresh_rounded, color: Colors.blueAccent),
                    onPressed: _loadData,
                  ),
                ],
              ),
            ),

            // Live Auto-Share Toggle & Action Bar
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.04),
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.share_location_rounded, color: Colors.blueAccent, size: 22),
                  const SizedBox(width: 10),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Auto-Share Location', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                        Text('Auto updates every 30s', style: TextStyle(color: Colors.grey, fontSize: 11)),
                      ],
                    ),
                  ),
                  Switch(
                    value: _isAutoSharing,
                    activeThumbColor: const Color(0xFF10B981),
                    onChanged: _toggleAutoSharing,
                  ),
                ],
              ),
            ),

            // Map View Header (Always visible)
            Container(
              height: 200,
              margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              clipBehavior: Clip.antiAlias,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.4), width: 1.2),
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
                  GoogleMap(
                    initialCameraPosition: CameraPosition(
                      target: _mapCenter,
                      zoom: 13,
                    ),
                    markers: _markers,
                    myLocationEnabled: true,
                    zoomControlsEnabled: false,
                    mapToolbarEnabled: false,
                    onMapCreated: (controller) => _mapController = controller,
                  ),

                  // Top Status Badge Overlay
                  Positioned(
                    top: 10,
                    left: 10,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFF0F172A).withValues(alpha: 0.88),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.3)),
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
                            _members.isNotEmpty ? '${_members.length} Members Active' : 'Live Map Ready',
                            style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ),
                  ),

                  // Recenter / Fit Button Overlay
                  Positioned(
                    bottom: 10,
                    right: 10,
                    child: FloatingActionButton.small(
                      heroTag: 'recenter_map_btn',
                      backgroundColor: const Color(0xFF0F172A),
                      foregroundColor: Colors.blueAccent,
                      onPressed: () {
                        if (_mapController != null) {
                          _mapController!.animateCamera(
                            CameraUpdate.newLatLngZoom(_mapCenter, 14),
                          );
                        }
                      },
                      child: const Icon(Icons.my_location_rounded, size: 20),
                    ),
                  ),
                ],
              ),
            ),


            // Family Groups Section Header
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('My Family Groups', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                  Row(
                    children: [
                      TextButton.icon(
                        style: TextButton.styleFrom(padding: EdgeInsets.zero),
                        onPressed: _showJoinGroupDialog,
                        icon: const Icon(Icons.login_rounded, size: 16, color: Colors.greenAccent),
                        label: const Text('Join Group', style: TextStyle(color: Colors.greenAccent, fontSize: 12)),
                      ),
                      const SizedBox(width: 8),
                      TextButton.icon(
                        style: TextButton.styleFrom(padding: EdgeInsets.zero),
                        onPressed: _showCreateGroupDialog,
                        icon: const Icon(Icons.add_circle_outline_rounded, size: 16, color: Colors.blueAccent),
                        label: const Text('+ Create', style: TextStyle(color: Colors.blueAccent, fontSize: 12)),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // Family Groups Cards List
            if (_groups.isNotEmpty) ...[
              SizedBox(
                height: 80,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: _groups.length,
                  itemBuilder: (context, index) {
                    final group = _groups[index];
                    final String name = group['name']?.toString() ?? 'Family Group';
                    final String code = group['invite_code']?.toString() ?? 'N/A';
                    final int count = group['member_count'] ?? 1;

                    return Container(
                      width: 220,
                      margin: const EdgeInsets.only(right: 10),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [Colors.blue.withValues(alpha: 0.15), Colors.purple.withValues(alpha: 0.1)],
                        ),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.3)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const CircleAvatar(
                                radius: 12,
                                backgroundColor: Colors.blueAccent,
                                child: Icon(Icons.groups_rounded, size: 14, color: Colors.white),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(name, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                              ),
                            ],
                          ),
                          const Spacer(),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('$count Member${count > 1 ? 's' : ''}', style: const TextStyle(color: Colors.grey, fontSize: 11)),
                              InkWell(
                                onTap: () {
                                  Clipboard.setData(ClipboardData(text: code));
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(content: Text('Code $code copied!')),
                                  );
                                },
                                child: Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: Colors.white.withValues(alpha: 0.1),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Row(
                                    children: [
                                      Text(code, style: const TextStyle(color: Colors.blueAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                                      const SizedBox(width: 4),
                                      const Icon(Icons.copy_rounded, size: 10, color: Colors.blueAccent),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ] else ...[
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.withValues(alpha: 0.08),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: Colors.blue.withValues(alpha: 0.2)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.info_outline_rounded, color: Colors.blueAccent, size: 20),
                      const SizedBox(width: 10),
                      const Expanded(
                        child: Text('No family group found. Create one or join with invite code.',
                            style: TextStyle(color: Colors.white70, fontSize: 11)),
                      ),
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent, padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4)),
                        onPressed: _showCreateGroupDialog,
                        child: const Text('Create', style: TextStyle(fontSize: 11)),
                      ),
                    ],
                  ),
                ),
              ),
            ],

            const SizedBox(height: 12),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Member Live Status', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                  TextButton.icon(
                    onPressed: _isUpdatingLocation ? null : () => _shareMyLocation(),
                    icon: _isUpdatingLocation
                        ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                        : const Icon(Icons.my_location_rounded, size: 14, color: Colors.blueAccent),
                    label: const Text('Share My GPS Now', style: TextStyle(color: Colors.blueAccent, fontSize: 12)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 6),

            // Members Location List
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator(color: Colors.blueAccent))
                  : _members.isEmpty
                      ? Padding(
                          padding: const EdgeInsets.all(16),
                          child: Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(24),
                            decoration: BoxDecoration(
                              color: Colors.white.withValues(alpha: 0.04),
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.location_off_rounded, color: Colors.grey, size: 36),
                                const SizedBox(height: 8),
                                const Text('No family members have shared location yet.',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(color: Colors.grey, fontSize: 13)),
                                const SizedBox(height: 12),
                                ElevatedButton.icon(
                                  style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
                                  onPressed: () => _shareMyLocation(),
                                  icon: const Icon(Icons.my_location_rounded, size: 16),
                                  label: const Text('Share My Location First'),
                                ),
                              ],
                            ),
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          itemCount: _members.length,
                          itemBuilder: (context, index) {
                            final member = _members[index];
                            final int batteryVal = member['battery_level'] ?? 85;
                            final double? lat = double.tryParse(member['latitude']?.toString() ?? '');
                            final double? lng = double.tryParse(member['longitude']?.toString() ?? '');
                            final String name = member['full_name']?.toString() ?? member['username'] ?? 'Unknown Member';
                            final String relativeTime = _getRelativeTime(member['updated_at']);
                            final String distance = _getDistanceString(lat, lng);

                            Color batteryColor = Colors.greenAccent;
                            if (batteryVal < 20) {
                              batteryColor = Colors.redAccent;
                            } else if (batteryVal < 50) {
                              batteryColor = Colors.orangeAccent;
                            }

                            return Container(
                              margin: const EdgeInsets.only(bottom: 10),
                              padding: const EdgeInsets.all(14),
                              decoration: BoxDecoration(
                                color: Colors.white.withValues(alpha: 0.05),
                                borderRadius: BorderRadius.circular(16),
                                border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
                              ),
                              child: Row(
                                children: [
                                  CircleAvatar(
                                    backgroundColor: Colors.blueAccent.withValues(alpha: 0.2),
                                    child: Text(
                                      name.isNotEmpty ? name[0].toUpperCase() : 'U',
                                      style: const TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold),
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                                        const SizedBox(height: 2),
                                        Row(
                                          children: [
                                            const Icon(Icons.near_me_rounded, size: 12, color: Colors.blueAccent),
                                            const SizedBox(width: 4),
                                            Text(distance, style: const TextStyle(color: Colors.white70, fontSize: 11)),
                                            const SizedBox(width: 8),
                                            Text('•  $relativeTime', style: const TextStyle(color: Colors.grey, fontSize: 11)),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ),
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.end,
                                    children: [
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                        decoration: BoxDecoration(
                                          color: batteryColor.withValues(alpha: 0.15),
                                          borderRadius: BorderRadius.circular(8),
                                          border: Border.all(color: batteryColor.withValues(alpha: 0.4)),
                                        ),
                                        child: Row(
                                          children: [
                                            Icon(
                                              batteryVal < 20 ? Icons.battery_alert_rounded : Icons.battery_charging_full_rounded,
                                              size: 14,
                                              color: batteryColor,
                                            ),
                                            const SizedBox(width: 4),
                                            Text(
                                              '$batteryVal%',
                                              style: TextStyle(color: batteryColor, fontSize: 11, fontWeight: FontWeight.bold),
                                            ),
                                          ],
                                        ),
                                      ),
                                      if (lat != null && lng != null) ...[
                                        const SizedBox(height: 4),
                                        InkWell(
                                          onTap: () {
                                            if (_mapController != null) {
                                              _mapController!.animateCamera(
                                                CameraUpdate.newLatLngZoom(LatLng(lat, lng), 15),
                                              );
                                            }
                                          },
                                          child: const Text('View on Map', style: TextStyle(color: Colors.blueAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                                        ),
                                      ],
                                    ],
                                  ),
                                ],
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
