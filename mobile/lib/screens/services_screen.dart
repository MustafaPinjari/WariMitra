import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class ServicesScreen extends StatefulWidget {
  const ServicesScreen({Key? key}) : super(key: key);

  @override
  State<ServicesScreen> createState() => _ServicesScreenState();
}

class _ServicesScreenState extends State<ServicesScreen> {
  String? _selectedCategory = 'Water Shortage';

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
              
              Container(
                decoration: BoxDecoration(
                  color: AppTheme.surfaceDark,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: AppTheme.bhagwaPrimary.withValues(alpha: 0.3)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.3),
                      blurRadius: 15,
                      offset: const Offset(0, 5),
                    )
                  ],
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
                            decoration: BoxDecoration(
                              color: AppTheme.bhagwaPrimary.withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Icon(Icons.rate_review_rounded, color: AppTheme.bhagwaBright, size: 20),
                          ),
                          const SizedBox(width: 12),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text("समस्या नोंदवा • Submit Report", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                              Text("मदत पथकाला थेट माहिती मिळण्यासाठी", style: TextStyle(fontSize: 10, color: Colors.grey.shade700)),
                            ],
                          ),
                        ],
                      ),
                      const SizedBox(height: 20),
                      
                      DropdownButtonFormField<String>(
                        value: _selectedCategory,
                        dropdownColor: AppTheme.surfaceDark,
                        style: const TextStyle(color: Colors.white, fontSize: 14),
                        decoration: const InputDecoration(
                          labelText: 'प्रकार • Issue Category',
                        ),
                        items: ['Water Shortage', 'Medical Need', 'Heavy Crowd', 'Road Block']
                            .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                            .toList(),
                        onChanged: (val) => setState(() => _selectedCategory = val),
                      ),
                      const SizedBox(height: 16),

                      TextFormField(
                        maxLines: 3,
                        style: const TextStyle(color: Colors.white, fontSize: 14),
                        decoration: const InputDecoration(
                          labelText: 'तपशील • Description & Location',
                          alignLabelWithHint: true,
                        ),
                      ),
                      const SizedBox(height: 24),

                      ElevatedButton(
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              backgroundColor: AppTheme.bhagwaPrimary,
                              content: Text("माहिती यशस्वीरित्या पाठवली! (Report submitted successfully)", style: TextStyle(fontWeight: FontWeight.bold)),
                            )
                          );
                        },
                        child: const Text("माहिती पाठवा • Submit Report"),
                      )
                    ],
                  ),
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
