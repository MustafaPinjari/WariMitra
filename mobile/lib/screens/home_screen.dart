import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:ui';
import '../theme/app_theme.dart';
import '../widgets/spring_button.dart';
import '../providers/auth_provider.dart';
import 'nearby_services_screen.dart';
import 'missing_person_screen.dart';
import 'family_locator_screen.dart';
import 'temple_queue_screen.dart';
import 'community_intelligence_screen.dart';
import 'heritage_screen.dart';
import 'lost_found_screen.dart';
import 'sanitation_screen.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      body: Stack(
        children: [
          // Bhagwa Ambient Glow - Top Right
          Positioned(
            top: -100,
            right: -100,
            child: Container(
              width: 320,
              height: 320,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppTheme.bhagwaPrimary.withValues(alpha: 0.18),
              ),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 110, sigmaY: 110),
                child: Container(color: Colors.transparent),
              ),
            ),
          ),

          // Sacred Gold Ambient Glow - Bottom Left
          Positioned(
            bottom: -60,
            left: -80,
            child: Container(
              width: 280,
              height: 280,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppTheme.sacredGold.withValues(alpha: 0.12),
              ),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 110, sigmaY: 110),
                child: Container(color: Colors.transparent),
              ),
            ),
          ),
          
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.only(left: 20, right: 20, top: 16, bottom: 110),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Top Header & Greeting
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(
                                  color: AppTheme.bhagwaPrimary.withValues(alpha: 0.2),
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(color: AppTheme.bhagwaPrimary.withValues(alpha: 0.4)),
                                ),
                                child: const Text(
                                  "जय हरी विठ्ठल",
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    color: AppTheme.bhagwaBright,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            "नमस्कार, ${auth.username.isNotEmpty ? auth.username : 'वारकरी'}!",
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.w900,
                              color: Colors.white,
                              letterSpacing: -0.5,
                            ),
                          ),
                          Text(
                            "साथीला वारीमित्र • Live Wari Companion",
                            style: TextStyle(
                              fontSize: 13,
                              color: Colors.white.withValues(alpha: 0.6),
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                      IconButton(
                        icon: Container(
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.08),
                            shape: BoxShape.circle,
                            border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
                          ),
                          child: const Icon(Icons.logout_rounded, color: AppTheme.sosRed, size: 20),
                        ),
                        onPressed: () async {
                          await ref.read(authProvider.notifier).logout();
                        },
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  
                  // Live Route Status Glass Card
                  SpringButton(
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => const FamilyLocatorScreen()),
                      );
                    },
                    child: Container(
                      decoration: BoxDecoration(
                        color: AppTheme.marathaNavy.withValues(alpha: 0.8),
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(color: AppTheme.bhagwaPrimary.withValues(alpha: 0.35)),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.4),
                            blurRadius: 20,
                            offset: const Offset(0, 8),
                          )
                        ],
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(24),
                        child: BackdropFilter(
                          filter: ImageFilter.blur(sigmaX: 15, sigmaY: 15),
                          child: Padding(
                            padding: const EdgeInsets.all(20.0),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        const Icon(Icons.location_on_rounded, color: AppTheme.bhagwaBright, size: 14),
                                        const SizedBox(width: 4),
                                        Text("पालखी ट्रॅकर • Live GPS", style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 11, fontWeight: FontWeight.bold)),
                                      ],
                                    ),
                                    const SizedBox(height: 6),
                                    const Text("Sector 4, Alandi Route", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Colors.white)),
                                    const SizedBox(height: 2),
                                    Text("ज्ञानेश्वर महाराज पालखी मार्ग", style: TextStyle(color: AppTheme.sacredGold, fontSize: 12, fontWeight: FontWeight.w600)),
                                  ],
                                ),
                                Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: AppTheme.bhagwaPrimary.withValues(alpha: 0.25),
                                    shape: BoxShape.circle,
                                    border: Border.all(color: AppTheme.bhagwaPrimary.withValues(alpha: 0.5)),
                                  ),
                                  child: const Icon(Icons.my_location_rounded, color: AppTheme.bhagwaBright, size: 22),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 28),
                  const Text("प्रमुख सेवा • Quick Actions", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                  const SizedBox(height: 16),
                  
                  // Grid of Custom Actions
                  GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: 2,
                    crossAxisSpacing: 14,
                    mainAxisSpacing: 14,
                    childAspectRatio: 1.1,
                    children: [
                      _buildActionCard(context, Icons.menu_book_rounded, "वारी वारसा", "Vari Heritage", AppTheme.sacredGold, const HeritageScreen()),
                      _buildActionCard(context, Icons.search_rounded, "हरवलेल्या वस्तू", "Lost & Found", Colors.cyanAccent, const LostFoundScreen()),
                      _buildActionCard(context, Icons.wc_rounded, "स्वच्छतागृह", "Sanitation", Colors.tealAccent, const SanitationScreen()),
                      _buildActionCard(context, Icons.medical_services_rounded, "मदत केंद्र", "Nearby Services", AppTheme.bhagwaBright, const NearbyServicesScreen()),
                      _buildActionCard(context, Icons.campaign_rounded, "गर्दी माहिती", "Community Intel", AppTheme.sacredGold, const CommunityIntelligenceScreen()),
                      _buildActionCard(context, Icons.person_search_rounded, "हरवलेले व्यक्ती", "Missing Person", Colors.orangeAccent, const MissingPersonScreen()),
                      _buildActionCard(context, Icons.groups_rounded, "कुटुंब शोधा", "Family Locator", Colors.tealAccent, const FamilyLocatorScreen()),
                      _buildActionCard(context, Icons.temple_hindu_rounded, "दर्शन रांग", "Temple Queue", Colors.purpleAccent, const TempleQueueScreen()),
                    ],
                  )
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionCard(BuildContext context, IconData icon, String titleMarathi, String titleEnglish, Color color, Widget destinationScreen) {
    return SpringButton(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => destinationScreen),
        );
      },
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppTheme.surfaceDark,
          borderRadius: BorderRadius.circular(22),
          border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.3),
              blurRadius: 10,
              offset: const Offset(0, 4),
            )
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.15),
                shape: BoxShape.circle,
                border: Border.all(color: color.withValues(alpha: 0.3)),
              ),
              child: Icon(icon, size: 28, color: color),
            ),
            const SizedBox(height: 10),
            Text(
              titleMarathi, 
              style: const TextStyle(
                fontWeight: FontWeight.bold, 
                color: Colors.white,
                fontSize: 13,
              ),
              textAlign: TextAlign.center,
            ),
            Text(
              titleEnglish, 
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.5),
                fontSize: 10,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
