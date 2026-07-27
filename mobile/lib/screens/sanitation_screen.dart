import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class SanitationScreen extends StatelessWidget {
  const SanitationScreen({Key? key}) : super(key: key);

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
                        'स्वच्छतागृह व कचरा व्यवस्थापन',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      Text(
                        'Public Toilet & Sanitation Finder',
                        style: TextStyle(fontSize: 11, color: Colors.tealAccent, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 24),

              _buildToiletCard('आळंदी विश्रामगृह सार्वजनिक स्वच्छतागृह', 'स्वच्छता: ९२%', true),
              const SizedBox(height: 10),
              _buildToiletCard('दिवे घाट परिसर मोबाईल टॉयलेट ब्लॉक', 'स्वच्छता: ८५%', true),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildToiletCard(String name, String status, bool water) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.teal.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          CircleAvatar(backgroundColor: Colors.teal.withValues(alpha: 0.2), child: const Icon(Icons.wc_rounded, color: Colors.tealAccent)),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                const SizedBox(height: 2),
                Text(status, style: const TextStyle(color: Colors.tealAccent, fontWeight: FontWeight.bold, fontSize: 11)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
