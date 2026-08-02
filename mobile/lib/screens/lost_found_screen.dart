import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';

class LostFoundScreen extends StatefulWidget {
  const LostFoundScreen({Key? key}) : super(key: key);

  @override
  State<LostFoundScreen> createState() => _LostFoundScreenState();
}

class _LostFoundScreenState extends State<LostFoundScreen> {
  final _titleController = TextEditingController();
  final _locationController = TextEditingController();
  final _descController = TextEditingController();
  final _contactController = TextEditingController();
  String _category = 'Bag';
  bool _isSubmitting = false;

  List<dynamic> _items = [];
  bool _loadingItems = true;

  @override
  void initState() {
    super.initState();
    _loadItems();
  }

  Future<void> _loadItems() async {
    try {
      final response = await ApiService.dio.get('/lost-found/items/');
      final data = response.data;
      setState(() {
        _items = data is List ? data : (data['results'] ?? []);
        _loadingItems = false;
      });
    } catch (_) {
      setState(() => _loadingItems = false);
    }
  }

  String? _selectedImageName;

  Future<void> _submitItem() async {
    if (_titleController.text.trim().isEmpty || _locationController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Item title and location are required'), backgroundColor: Colors.red),
      );
      return;
    }
    setState(() => _isSubmitting = true);
    try {
      await ApiService.dio.post('/lost-found/items/', data: {
        'title': _titleController.text.trim(),
        'category': _category,
        'description': _descController.text.trim(),
        'location': _locationController.text.trim(),
        'contact_phone': _contactController.text.trim(),
        'image_url': _selectedImageName != null ? 'https://dummyimage.com/600x400/00bcd4/ffffff&text=$_selectedImageName' : '',
      });
      _titleController.clear();
      _locationController.clear();
      _descController.clear();
      _contactController.clear();
      setState(() => _selectedImageName = null);
      _loadItems();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('✅ Item Registered! Check list below.'), backgroundColor: Colors.cyan),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('❌ ${ApiService.errorMessage(e)}'), backgroundColor: Colors.red),
        );
      }
    }
    setState(() => _isSubmitting = false);
  }

  @override
  void dispose() {
    _titleController.dispose();
    _locationController.dispose();
    _descController.dispose();
    _contactController.dispose();
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
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('हरवलेल्या वस्तू व व्यक्ती', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white)),
                      Text('Digital Lost & Found Management', style: TextStyle(fontSize: 11, color: Colors.cyanAccent, fontWeight: FontWeight.bold)),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Report form
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: AppTheme.surfaceDark,
                  borderRadius: BorderRadius.circular(22),
                  border: Border.all(color: Colors.cyan.withValues(alpha: 0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Text('वस्तूची नोंद करा • Report Item', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                    const SizedBox(height: 14),

                    DropdownButtonFormField<String>(
                      value: _category,
                      dropdownColor: AppTheme.surfaceDark,
                      style: const TextStyle(color: Colors.white),
                      decoration: const InputDecoration(labelText: 'Category'),
                      items: ['Bag', 'Phone', 'ID Card', 'Jewellery', 'Clothing', 'Other']
                          .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                          .toList(),
                      onChanged: (val) => setState(() => _category = val!),
                    ),
                    const SizedBox(height: 12),

                    TextFormField(
                      controller: _titleController,
                      style: const TextStyle(color: Colors.white, fontSize: 13),
                      decoration: const InputDecoration(labelText: 'वस्तूचे नाव • Item Title *'),
                    ),
                    const SizedBox(height: 10),

                    TextFormField(
                      controller: _locationController,
                      style: const TextStyle(color: Colors.white, fontSize: 13),
                      decoration: const InputDecoration(labelText: 'ठिकाण • Location *'),
                    ),
                    const SizedBox(height: 10),

                    TextFormField(
                      controller: _descController,
                      style: const TextStyle(color: Colors.white, fontSize: 13),
                      maxLines: 2,
                      decoration: const InputDecoration(labelText: 'Description'),
                    ),
                    const SizedBox(height: 10),

                    TextFormField(
                      controller: _contactController,
                      keyboardType: TextInputType.phone,
                      style: const TextStyle(color: Colors.white, fontSize: 13),
                      decoration: const InputDecoration(labelText: 'Contact Phone'),
                    ),
                    const SizedBox(height: 12),

                    // Dummy Image Upload Button
                    InkWell(
                      onTap: () {
                        setState(() {
                          _selectedImageName = 'item_photo_${DateTime.now().millisecondsSinceEpoch}.jpg';
                        });
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.05),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.cyan.withValues(alpha: 0.3)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.add_a_photo_rounded, color: Colors.cyan, size: 18),
                            const SizedBox(width: 8),
                            Text(
                              _selectedImageName != null ? '📸 Attached: $_selectedImageName' : 'फोटो जोडा (Upload Photo - Optional)',
                              style: TextStyle(
                                color: _selectedImageName != null ? Colors.cyanAccent : Colors.white70,
                                fontSize: 12,
                                fontWeight: _selectedImageName != null ? FontWeight.bold : FontWeight.normal,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    ElevatedButton.icon(
                      onPressed: _isSubmitting ? null : _submitItem,
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.cyan),
                      icon: _isSubmitting
                          ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                          : const Icon(Icons.qr_code_scanner_rounded),
                      label: const Text('नोंद करा • Submit Report'),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              Row(
                children: [
                  const Text('Recent Reports', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                  const Spacer(),
                  IconButton(icon: const Icon(Icons.refresh_rounded, color: Colors.cyan, size: 20), onPressed: _loadItems),
                ],
              ),
              const SizedBox(height: 10),

              if (_loadingItems)
                const Center(child: CircularProgressIndicator(color: Colors.cyan))
              else if (_items.isEmpty)
                const Text('No items reported yet', style: TextStyle(color: Colors.grey))
              else
                ..._items.map((item) {
                  final String status = item['status']?.toString() ?? 'REPORTED';
                  final bool hasPhoto = item['image_url'] != null && item['image_url'].toString().isNotEmpty;

                  Color statusColor = Colors.cyan;
                  if (status == 'FOUND') statusColor = Colors.greenAccent;
                  if (status == 'RETURNED') statusColor = Colors.blueAccent;

                  return Container(
                    margin: const EdgeInsets.only(bottom: 10),
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: AppTheme.surfaceDark,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: statusColor.withValues(alpha: 0.3)),
                    ),
                    child: Row(
                      children: [
                        CircleAvatar(
                          backgroundColor: statusColor.withValues(alpha: 0.15),
                          child: Icon(
                            hasPhoto ? Icons.photo_camera_rounded : Icons.inventory_2_rounded,
                            color: statusColor,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(item['title']?.toString() ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                              Text('${item['category']} • ${item['location']}', style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 12)),
                              if (hasPhoto)
                                const Text('📸 Photo attached', style: TextStyle(color: Colors.cyanAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(color: statusColor.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(8)),
                          child: Text(status, style: TextStyle(color: statusColor, fontSize: 10, fontWeight: FontWeight.bold)),
                        ),
                      ],
                    ),
                  );
                }),
            ],
          ),
        ),
      ),
    );
  }
}
