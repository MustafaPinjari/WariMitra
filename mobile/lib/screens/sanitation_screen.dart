import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';

class SanitationScreen extends StatefulWidget {
  const SanitationScreen({Key? key}) : super(key: key);

  @override
  State<SanitationScreen> createState() => _SanitationScreenState();
}

class _SanitationScreenState extends State<SanitationScreen> {
  List<dynamic> _toilets = [];
  bool _isLoading = true;
  String? _errorMsg;

  @override
  void initState() {
    super.initState();
    _loadToilets();
  }

  Future<void> _loadToilets() async {
    setState(() { _isLoading = true; _errorMsg = null; });
    try {
      final response = await ApiService.dio.get('/sanitation/toilets/');
      final data = response.data;
      setState(() {
        _toilets = data is List ? data : (data['results'] ?? []);
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMsg = ApiService.errorMessage(e);
        _isLoading = false;
      });
    }
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
              Row(
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
                  const SizedBox(width: 10),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('स्वच्छतागृह व कचरा व्यवस्थापन', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                        Text('Public Toilet & Sanitation Finder', style: TextStyle(fontSize: 11, color: Colors.tealAccent, fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ),
                  IconButton(icon: const Icon(Icons.refresh_rounded, color: Colors.tealAccent, size: 20), onPressed: _loadToilets),
                ],
              ),
              const SizedBox(height: 24),

              if (_isLoading)
                const Center(child: Padding(padding: EdgeInsets.all(40), child: CircularProgressIndicator(color: Colors.teal)))
              else if (_errorMsg != null)
                _buildErrorCard(_errorMsg!)
              else if (_toilets.isEmpty)
                _buildEmptyCard()
              else
                ..._toilets.map((toilet) => Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: _buildToiletCard(toilet),
                )),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildToiletCard(Map<String, dynamic> toilet) {
    final score = toilet['cleanliness_score'] ?? 85;
    final hasWater = toilet['is_water_available'] ?? true;
    final genderType = toilet['gender_type'] ?? 'Unisex';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.teal.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          CircleAvatar(
            backgroundColor: Colors.teal.withValues(alpha: 0.2),
            child: const Icon(Icons.wc_rounded, color: Colors.tealAccent),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(toilet['name']?.toString() ?? 'Unknown', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                const SizedBox(height: 2),
                Text(toilet['location']?.toString() ?? '', style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 11)),
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
        ],
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

  Widget _buildErrorCard(String msg) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline_rounded, color: Colors.red),
          const SizedBox(width: 10),
          Expanded(child: Text(msg, style: const TextStyle(color: Colors.white70, fontSize: 13))),
          TextButton(onPressed: _loadToilets, child: const Text('Retry', style: TextStyle(color: Colors.teal))),
        ],
      ),
    );
  }

  Widget _buildEmptyCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.04), borderRadius: BorderRadius.circular(16)),
      child: const Center(child: Text('No sanitation facilities listed yet', style: TextStyle(color: Colors.grey))),
    );
  }
}
