import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class HeritageScreen extends StatefulWidget {
  const HeritageScreen({Key? key}) : super(key: key);

  @override
  State<HeritageScreen> createState() => _HeritageScreenState();
}

class _HeritageScreenState extends State<HeritageScreen> {
  bool _isPlaying = false;

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
                        'वारी परंपरा व अभंग दालन',
                        style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      Text(
                        'Vari Heritage & Abhang Audio Guide',
                        style: TextStyle(fontSize: 11, color: AppTheme.bhagwaBright, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Audio Player Banner
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(colors: [AppTheme.bhagwaPrimary, AppTheme.sacredGold]),
                  borderRadius: BorderRadius.circular(22),
                  boxShadow: [
                    BoxShadow(color: AppTheme.bhagwaPrimary.withValues(alpha: 0.3), blurRadius: 15, offset: const Offset(0, 5))
                  ],
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: const BoxDecoration(color: Colors.white24, shape: BoxShape.circle),
                          child: const Icon(Icons.music_note_rounded, color: Colors.white, size: 28),
                        ),
                        const SizedBox(width: 14),
                        const Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('संत ज्ञानेश्वर महाराज अभंग', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 15)),
                              Text('रूप सुंदर सावळा तो हा विठ्ठल बरवा', style: TextStyle(color: Colors.white70, fontSize: 12)),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: () => setState(() => _isPlaying = !_isPlaying),
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.white, foregroundColor: AppTheme.bhagwaPrimary),
                      icon: Icon(_isPlaying ? Icons.pause_rounded : Icons.play_arrow_rounded),
                      label: Text(_isPlaying ? 'ऑडिओ थांबवा (Pause)' : 'अभंग ऐका (Listen Audio)'),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),
              const Text('महाराष्ट्राचे संत परंपरा • Wari Saints', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
              const SizedBox(height: 12),

              _buildSaintCard('संत ज्ञानेश्वर महाराज (माउली)', '1275 – 1296 CE • Alandi', 'Patron saint of Wari, composer of Dnyaneshwari.'),
              const SizedBox(height: 10),
              _buildSaintCard('संत तुकाराम महाराज (जगद्गुरु)', '1598 – 1650 CE • Dehu', 'Greatest Varkari poet saint of Dehu.'),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSaintCard(String title, String era, String desc) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
          const SizedBox(height: 2),
          Text(era, style: const TextStyle(color: AppTheme.bhagwaBright, fontSize: 11, fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          Text(desc, style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 12)),
        ],
      ),
    );
  }
}
