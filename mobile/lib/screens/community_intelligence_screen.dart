import 'package:flutter/material.dart';
import '../widgets/spring_button.dart';
import '../services/api_service.dart';

class CommunityIntelligenceScreen extends StatefulWidget {
  const CommunityIntelligenceScreen({Key? key}) : super(key: key);

  @override
  State<CommunityIntelligenceScreen> createState() => _CommunityIntelligenceScreenState();
}

class _CommunityIntelligenceScreenState extends State<CommunityIntelligenceScreen> {
  List<dynamic> _reports = [];
  bool _isLoading = true;
  final Set<String> _votedIds = {};

  // For posting new reports
  final _titleController = TextEditingController();
  final _descController = TextEditingController();
  String _newCategory = 'Water';
  bool _isPosting = false;

  @override
  void initState() {
    super.initState();
    _loadReports();
  }

  Future<void> _loadReports() async {
    setState(() => _isLoading = true);
    try {
      final response = await ApiService.dio.get('/community/reports/');
      final data = response.data;
      setState(() {
        _reports = data is List ? data : (data['results'] ?? []);
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _voteReport(String reportId) async {
    try {
      await ApiService.dio.post('/community/reports/$reportId/verify/', data: {'is_valid': true});
      setState(() => _votedIds.add(reportId));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('👍 Thank you! Citizen verification registered.'), backgroundColor: Color(0xFF10B981)),
        );
      }
      _loadReports(); // Refresh to get updated confidence score
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('❌ ${ApiService.errorMessage(e)}'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _postReport() async {
    if (_titleController.text.trim().isEmpty) return;
    setState(() => _isPosting = true);
    try {
      await ApiService.dio.post('/community/reports/', data: {
        'category': _newCategory,
        'description': _titleController.text.trim(),
        'latitude': 18.3444,
        'longitude': 74.0305,
      });
      _titleController.clear();
      Navigator.pop(context); // Close bottom sheet
      _loadReports();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('✅ Report submitted!'), backgroundColor: Color(0xFF10B981)),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('❌ ${ApiService.errorMessage(e)}'), backgroundColor: Colors.red),
        );
      }
    }
    setState(() => _isPosting = false);
  }

  void _showPostReportSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF1E222D),
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (context) => StatefulBuilder(
        builder: (context, setModalState) => Padding(
          padding: EdgeInsets.only(
            left: 20, right: 20, top: 20,
            bottom: MediaQuery.of(context).viewInsets.bottom + 20,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Post Citizen Report', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _newCategory,
                dropdownColor: const Color(0xFF1E222D),
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Category',
                  filled: true,
                  fillColor: Colors.white.withValues(alpha: 0.05),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                ),
                items: ['Water', 'Food', 'Medical', 'Traffic', 'Road_Block', 'Other']
                    .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                    .toList(),
                onChanged: (val) => setModalState(() => _newCategory = val!),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _titleController,
                style: const TextStyle(color: Colors.white),
                maxLines: 3,
                decoration: InputDecoration(
                  hintText: 'Describe the issue and location...',
                  hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.3), fontSize: 13),
                  filled: true,
                  fillColor: Colors.white.withValues(alpha: 0.05),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isPosting ? null : _postReport,
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.orange),
                  child: _isPosting
                      ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : const Text('Submit Report'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descController.dispose();
    super.dispose();
  }

  Color _categoryColor(String? category) {
    switch (category) {
      case 'Water': return Colors.blue;
      case 'Medical': return const Color(0xFF10B981);
      case 'Traffic': return Colors.amber;
      case 'Food': return Colors.orange;
      case 'Road_Block': return Colors.red;
      default: return Colors.grey;
    }
  }

  IconData _categoryIcon(String? category) {
    switch (category) {
      case 'Water': return Icons.water_drop_rounded;
      case 'Medical': return Icons.local_hospital_rounded;
      case 'Traffic': return Icons.traffic_rounded;
      case 'Food': return Icons.restaurant_rounded;
      default: return Icons.report_problem_rounded;
    }
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
              padding: const EdgeInsets.all(20.0),
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
                            Text('Community Intelligence', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white)),
                            Text('Citizen Reports & AI Trust Scores', style: TextStyle(fontSize: 12, color: Colors.orangeAccent)),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.refresh_rounded, color: Colors.orange),
                        onPressed: _loadReports,
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  SpringButton(
                    onTap: _showPostReportSheet,
                    child: Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(colors: [Colors.orange.withValues(alpha: 0.2), Colors.deepOrange.withValues(alpha: 0.1)]),
                        borderRadius: BorderRadius.circular(18),
                        border: Border.all(color: Colors.orange.withValues(alpha: 0.4)),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.add_location_alt_rounded, color: Colors.orange, size: 26),
                          SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Post Citizen Incident Report', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                                Text('Tap to submit a community alert', style: TextStyle(color: Colors.grey, fontSize: 12)),
                              ],
                            ),
                          ),
                          Icon(Icons.arrow_forward_ios_rounded, color: Colors.orangeAccent, size: 16),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 20),
              child: Text('Nearby Live Citizen Reports', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            ),
            const SizedBox(height: 12),

            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator(color: Colors.orange))
                  : _reports.isEmpty
                      ? const Center(child: Text('No reports yet', style: TextStyle(color: Colors.grey)))
                      : ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 20),
                          itemCount: _reports.length,
                          itemBuilder: (context, idx) {
                            final item = _reports[idx];
                            final id = item['id']?.toString() ?? '';
                            final hasVoted = _votedIds.contains(id);
                            final color = _categoryColor(item['category']?.toString());
                            final score = item['confidence_score'] ?? 50;

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
                                        backgroundColor: color.withValues(alpha: 0.2),
                                        child: Icon(_categoryIcon(item['category']?.toString()), color: color),
                                      ),
                                      const SizedBox(width: 12),
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              item['description']?.toString() ?? 'No description',
                                              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                                              maxLines: 2,
                                              overflow: TextOverflow.ellipsis,
                                            ),
                                            const SizedBox(height: 2),
                                            Text(
                                              item['category']?.toString() ?? '',
                                              style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 11),
                                            ),
                                          ],
                                        ),
                                      ),
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: const Color(0xFF10B981).withValues(alpha: 0.2),
                                          borderRadius: BorderRadius.circular(10),
                                          border: Border.all(color: const Color(0xFF10B981).withValues(alpha: 0.4)),
                                        ),
                                        child: Text(
                                          '$score% verified',
                                          style: const TextStyle(color: Color(0xFF10B981), fontSize: 11, fontWeight: FontWeight.bold),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 10),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        item['created_at']?.toString().substring(0, 10) ?? '',
                                        style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 11),
                                      ),
                                      SpringButton(
                                        onTap: hasVoted ? null : () => _voteReport(id),
                                        child: Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                          decoration: BoxDecoration(
                                            color: hasVoted ? Colors.orange.withValues(alpha: 0.3) : Colors.white.withValues(alpha: 0.1),
                                            borderRadius: BorderRadius.circular(12),
                                          ),
                                          child: Row(
                                            children: [
                                              Icon(Icons.thumb_up_alt_rounded, size: 14, color: hasVoted ? Colors.orange : Colors.grey),
                                              const SizedBox(width: 4),
                                              Text(
                                                hasVoted ? 'Confirmed' : 'Confirm',
                                                style: TextStyle(
                                                  color: hasVoted ? Colors.orange : Colors.white,
                                                  fontSize: 11,
                                                  fontWeight: FontWeight.bold,
                                                ),
                                              ),
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
          ],
        ),
      ),
    );
  }
}
