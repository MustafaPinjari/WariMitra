import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';
import '../services/location_service.dart';

class ServicesScreen extends StatefulWidget {
  const ServicesScreen({Key? key}) : super(key: key);

  @override
  State<ServicesScreen> createState() => _ServicesScreenState();
}

class _ServicesScreenState extends State<ServicesScreen> {
  String? _selectedCategory = 'Water';
  final _descController = TextEditingController();
  bool _isSubmitting = false;
  List<dynamic> _recentReports = [];
  bool _loadingReports = true;

  @override
  void initState() {
    super.initState();
    _loadRecentReports();
  }

  Future<void> _loadRecentReports() async {
    try {
      final response = await ApiService.dio.get('/community/reports/');
      final data = response.data;
      setState(() {
        _recentReports = (data is List ? data : (data['results'] ?? [])).take(5).toList();
        _loadingReports = false;
      });
    } catch (_) {
      setState(() => _loadingReports = false);
    }
  }

  Future<void> _submitReport() async {
    if (_descController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please add a description'), backgroundColor: AppTheme.sosRed),
      );
      return;
    }
    setState(() => _isSubmitting = true);
    try {
      final pos = await LocationService.getCurrentPosition();
      if (pos == null) {
        setState(() => _isSubmitting = false);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('⚠️ Location required to post service report. Please turn on GPS.'),
              backgroundColor: AppTheme.sosRed,
            ),
          );
        }
        return;
      }
      final lat = LocationService.roundCoordinate(pos.latitude);
      final lng = LocationService.roundCoordinate(pos.longitude);

      await ApiService.dio.post('/community/reports/', data: {
        'category': _selectedCategory,
        'description': _descController.text.trim(),
        'latitude': lat,
        'longitude': lng,
      });
      _descController.clear();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            backgroundColor: AppTheme.bhagwaPrimary,
            content: Text("माहिती यशस्वीरित्या पाठवली! (Report submitted successfully)", style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        );
        _loadRecentReports();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('❌ ${ApiService.errorMessage(e)}'), backgroundColor: AppTheme.sosRed),
        );
      }
    }
    setState(() => _isSubmitting = false);
  }

  @override
  void dispose() {
    _descController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.only(left: 20, right: 20, top: 16, bottom: 110),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                "वारकरी सेवा व माहिती",
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: Colors.white),
              ),
              const SizedBox(height: 4),
              Text(
                "Community Relief & Ground Intel Reporting",
                style: TextStyle(fontSize: 12, color: Colors.white.withValues(alpha: 0.6), fontWeight: FontWeight.w500),
              ),
              const SizedBox(height: 24),

              // Submit report form
              Container(
                decoration: BoxDecoration(
                  color: AppTheme.surfaceDark,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: AppTheme.bhagwaPrimary.withValues(alpha: 0.3)),
                  boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.3), blurRadius: 15, offset: const Offset(0, 5))],
                ),
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(color: AppTheme.bhagwaPrimary.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(12)),
                            child: const Icon(Icons.rate_review_rounded, color: AppTheme.bhagwaBright, size: 20),
                          ),
                          const SizedBox(width: 12),
                          const Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text("समस्या नोंदवा • Submit Report", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                              Text("मदत पथकाला थेट माहिती", style: TextStyle(fontSize: 10, color: Colors.grey)),
                            ],
                          ),
                        ],
                      ),
                      const SizedBox(height: 20),

                      DropdownButtonFormField<String>(
                        value: _selectedCategory,
                        dropdownColor: AppTheme.surfaceDark,
                        style: const TextStyle(color: Colors.white, fontSize: 14),
                        decoration: const InputDecoration(labelText: 'प्रकार • Issue Category'),
                        items: [
                          DropdownMenuItem(value: 'Water', child: const Text('Water Shortage')),
                          DropdownMenuItem(value: 'Medical', child: const Text('Medical Need')),
                          DropdownMenuItem(value: 'Traffic', child: const Text('Heavy Crowd')),
                          DropdownMenuItem(value: 'Road_Block', child: const Text('Road Block')),
                          DropdownMenuItem(value: 'Food', child: const Text('Food Shortage')),
                          DropdownMenuItem(value: 'Other', child: const Text('Other')),
                        ],
                        onChanged: (val) => setState(() => _selectedCategory = val),
                      ),
                      const SizedBox(height: 16),

                      TextFormField(
                        controller: _descController,
                        maxLines: 3,
                        style: const TextStyle(color: Colors.white, fontSize: 14),
                        decoration: const InputDecoration(
                          labelText: 'तपशील • Description & Location',
                          alignLabelWithHint: true,
                        ),
                      ),
                      const SizedBox(height: 24),

                      ElevatedButton(
                        onPressed: _isSubmitting ? null : _submitReport,
                        child: _isSubmitting
                            ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                            : const Text("माहिती पाठवा • Submit Report"),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 28),
              const Text("Recent Community Reports", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
              const SizedBox(height: 12),

              if (_loadingReports)
                const Center(child: CircularProgressIndicator(color: AppTheme.bhagwaPrimary))
              else if (_recentReports.isEmpty)
                Text('No reports yet', style: TextStyle(color: Colors.white.withValues(alpha: 0.5)))
              else
                ..._recentReports.map((report) => Container(
                  margin: const EdgeInsets.only(bottom: 10),
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceDark,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.report_problem_rounded, color: AppTheme.bhagwaBright, size: 20),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(report['category']?.toString() ?? '', style: const TextStyle(color: AppTheme.bhagwaBright, fontWeight: FontWeight.bold, fontSize: 12)),
                            Text(report['description']?.toString() ?? '', style: TextStyle(color: Colors.white.withValues(alpha: 0.7), fontSize: 13), maxLines: 2, overflow: TextOverflow.ellipsis),
                          ],
                        ),
                      ),
                      Text('${report['confidence_score']}%', style: const TextStyle(color: Color(0xFF10B981), fontWeight: FontWeight.bold, fontSize: 12)),
                    ],
                  ),
                )),
            ],
          ),
        ),
      ),
    );
  }
}
