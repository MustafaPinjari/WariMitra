import 'package:flutter/material.dart';
import '../widgets/spring_button.dart';
import '../services/api_service.dart';

class MissingPersonScreen extends StatefulWidget {
  const MissingPersonScreen({Key? key}) : super(key: key);

  @override
  State<MissingPersonScreen> createState() => _MissingPersonScreenState();
}

class _MissingPersonScreenState extends State<MissingPersonScreen> {
  final _nameController = TextEditingController();
  final _ageController = TextEditingController();
  final _descController = TextEditingController();
  final _locationController = TextEditingController();
  final _contactController = TextEditingController();
  String _category = 'Child';
  bool _isLoading = false;

  // Existing reports from backend
  List<dynamic> _reports = [];
  bool _loadingReports = true;

  @override
  void initState() {
    super.initState();
    _loadReports();
  }

  Future<void> _loadReports() async {
    try {
      final response = await ApiService.dio.get('/missing-person/reports/');
      setState(() {
        _reports = response.data is List ? response.data : (response.data['results'] ?? []);
        _loadingReports = false;
      });
    } catch (_) {
      setState(() => _loadingReports = false);
    }
  }

  String? _selectedImageName;

  Future<void> _submitReport() async {
    if (_nameController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('कृपया व्यक्तीचे नाव टाका'), backgroundColor: Colors.orange),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      await ApiService.dio.post('/missing-person/reports/', data: {
        'name': _nameController.text.trim(),
        'age': int.tryParse(_ageController.text.trim()) ?? 0,
        'category': _category,
        'description': _descController.text.trim(),
        'last_seen_location': _locationController.text.trim(),
        'contact_mobile': _contactController.text.trim(),
        'photo_url': _selectedImageName != null ? 'https://dummyimage.com/600x400/f97316/ffffff&text=$_selectedImageName' : '',
      });
      _nameController.clear();
      _ageController.clear();
      _descController.clear();
      _locationController.clear();
      _contactController.clear();
      setState(() {
        _selectedImageName = null;
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('⚡ Missing Report Created! Volunteers & Police Notified.'),
            backgroundColor: Colors.orange,
          ),
        );
        _loadReports(); // Refresh list
      }
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('❌ ${ApiService.errorMessage(e)}'), backgroundColor: Colors.red),
        );
      }
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _ageController.dispose();
    _descController.dispose();
    _locationController.dispose();
    _contactController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F1115),
      body: SafeArea(
        child: SingleChildScrollView(
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
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Missing Person Search', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white)),
                      Text('Instant Alert to Police & Volunteers', style: TextStyle(fontSize: 12, color: Colors.redAccent)),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Report Form
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.04),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.orange.withValues(alpha: 0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Report a Missing Person', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                    const SizedBox(height: 16),

                    _buildInputLabel('Person Category'),
                    DropdownButtonFormField<String>(
                      value: _category,
                      dropdownColor: const Color(0xFF1E222D),
                      style: const TextStyle(color: Colors.white),
                      decoration: _buildInputDecoration(),
                      items: ['Child', 'Elderly', 'Adult', 'Disabled'].map((cat) {
                        return DropdownMenuItem(value: cat, child: Text(cat));
                      }).toList(),
                      onChanged: (val) => setState(() => _category = val!),
                    ),
                    const SizedBox(height: 12),

                    _buildInputLabel('Full Name *'),
                    TextField(
                      controller: _nameController,
                      style: const TextStyle(color: Colors.white),
                      decoration: _buildInputDecoration(hint: 'e.g., Anish Jadhav'),
                    ),
                    const SizedBox(height: 12),

                    _buildInputLabel('Age'),
                    TextField(
                      controller: _ageController,
                      keyboardType: TextInputType.number,
                      style: const TextStyle(color: Colors.white),
                      decoration: _buildInputDecoration(hint: 'e.g., 8'),
                    ),
                    const SizedBox(height: 12),

                    _buildInputLabel('Last Seen Location'),
                    TextField(
                      controller: _locationController,
                      style: const TextStyle(color: Colors.white),
                      decoration: _buildInputDecoration(hint: 'e.g., Near Water Point 2, Alandi Gate'),
                    ),
                    const SizedBox(height: 12),

                    _buildInputLabel('Description & Clothes'),
                    TextField(
                      controller: _descController,
                      maxLines: 3,
                      style: const TextStyle(color: Colors.white),
                      decoration: _buildInputDecoration(hint: 'Wearing saffron kurta...'),
                    ),
                    const SizedBox(height: 12),

                    _buildInputLabel('Contact Mobile'),
                    TextField(
                      controller: _contactController,
                      keyboardType: TextInputType.phone,
                      style: const TextStyle(color: Colors.white),
                      decoration: _buildInputDecoration(hint: '+91 98765 43210'),
                    ),
                    const SizedBox(height: 12),

                    // Dummy Photo Attachment Button
                    InkWell(
                      onTap: () {
                        setState(() {
                          _selectedImageName = 'person_photo_${DateTime.now().millisecondsSinceEpoch}.jpg';
                        });
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.05),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.orange.withValues(alpha: 0.3)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.add_a_photo_rounded, color: Colors.orange, size: 18),
                            const SizedBox(width: 8),
                            Text(
                              _selectedImageName != null ? '📸 Attached: $_selectedImageName' : 'फोटो जोडा (Upload Photo - Optional)',
                              style: TextStyle(
                                color: _selectedImageName != null ? Colors.orangeAccent : Colors.white70,
                                fontSize: 12,
                                fontWeight: _selectedImageName != null ? FontWeight.bold : FontWeight.normal,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),

                    SpringButton(
                      onTap: _isLoading ? null : _submitReport,
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(colors: [Colors.orange, Colors.deepOrange]),
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [BoxShadow(color: Colors.orange.withValues(alpha: 0.4), blurRadius: 15, offset: const Offset(0, 6))],
                        ),
                        child: Center(
                          child: _isLoading
                              ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                              : const Text('Broadcast Missing Report', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white)),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 28),

              // Active reports list
              Row(
                children: [
                  const Text('Active Reports', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.refresh_rounded, color: Colors.orange, size: 20),
                    onPressed: _loadReports,
                  ),
                ],
              ),
              const SizedBox(height: 12),

              if (_loadingReports)
                const Center(child: CircularProgressIndicator(color: Colors.orange))
              else if (_reports.isEmpty)
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.04),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Center(
                    child: Text('No active missing person reports', style: TextStyle(color: Colors.grey)),
                  ),
                )
              else
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _reports.length,
                  itemBuilder: (context, index) {
                    final item = _reports[index];
                    final String status = item['status']?.toString() ?? 'Searching';
                    final bool hasPhoto = item['photo_url'] != null && item['photo_url'].toString().isNotEmpty;

                    Color statusColor = Colors.orange;
                    if (status == 'Found') statusColor = Colors.greenAccent;
                    if (status == 'Closed') statusColor = Colors.grey;

                    return Container(
                      margin: const EdgeInsets.only(bottom: 10),
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.04),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: statusColor.withValues(alpha: 0.3)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              CircleAvatar(
                                backgroundColor: statusColor.withValues(alpha: 0.2),
                                child: Icon(
                                  hasPhoto ? Icons.photo_camera_rounded : Icons.person_search_rounded,
                                  color: statusColor,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      item['name']?.toString() ?? 'Unknown',
                                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                                    ),
                                    Text(
                                      '${item['category']} • Age: ${item['age'] ?? 'N/A'}',
                                      style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 12),
                                    ),
                                    if (hasPhoto)
                                      const Text('📸 Photo attached', style: TextStyle(color: Colors.orangeAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                                  ],
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: statusColor.withValues(alpha: 0.2),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  status,
                                  style: TextStyle(color: statusColor, fontSize: 11, fontWeight: FontWeight.bold),
                                ),
                              ),
                            ],
                          ),
                          if (item['last_seen_location']?.toString().isNotEmpty == true) ...[
                            const SizedBox(height: 8),
                            Text(
                              '📍 Last seen: ${item['last_seen_location']}',
                              style: TextStyle(color: Colors.white.withValues(alpha: 0.7), fontSize: 12),
                            ),
                          ],
                          if (item['description']?.toString().isNotEmpty == true) ...[
                            const SizedBox(height: 4),
                            Text(
                              item['description'],
                              style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 11),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ],
                      ),
                    );
                  },
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInputLabel(String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6.0),
      child: Text(label, style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.white.withValues(alpha: 0.8))),
    );
  }

  InputDecoration _buildInputDecoration({String? hint}) {
    return InputDecoration(
      hintText: hint,
      hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.3), fontSize: 13),
      filled: true,
      fillColor: Colors.white.withValues(alpha: 0.05),
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1))),
      enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1))),
      focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Colors.orange)),
    );
  }
}
