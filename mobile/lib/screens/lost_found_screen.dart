import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class LostFoundScreen extends StatelessWidget {
  const LostFoundScreen({Key? key}) : super(key: key);

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
                      Text(
                        'हरवलेल्या वस्तू व व्यक्ती',
                        style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      Text(
                        'Digital Lost & Found Management',
                        style: TextStyle(fontSize: 11, color: Colors.cyanAccent, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 24),

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
                    TextFormField(
                      style: const TextStyle(color: Colors.white, fontSize: 13),
                      decoration: const InputDecoration(labelText: 'वस्तूचे नाव • Item Title'),
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      style: const TextStyle(color: Colors.white, fontSize: 13),
                      decoration: const InputDecoration(labelText: 'ठिकाण • Location Lost/Found'),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('✅ वस्तूची नोंद झाली! (Item Registered)'), backgroundColor: Colors.cyan)
                        );
                      },
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.cyan),
                      icon: const Icon(Icons.qr_code_scanner_rounded),
                      label: const Text('नोंद करा व क्यूआर कोड मिळवा'),
                    )
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
