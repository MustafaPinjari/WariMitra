import 'package:flutter/material.dart';
import '../widgets/spring_button.dart';
import 'nearby_services_screen.dart';
import 'missing_person_screen.dart';
import 'family_locator_screen.dart';
import 'temple_queue_screen.dart';
import 'login_screen.dart';
import 'dart:ui';

class HomeScreen extends StatelessWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F1115), // Deep dark theme
      body: Stack(
        children: [
          // Spatial Background Glows
          Positioned(
            top: -100,
            right: -100,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.orange.withOpacity(0.15),
              ),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 100, sigmaY: 100),
                child: Container(color: Colors.transparent),
              ),
            ),
          ),
          Positioned(
            bottom: -50,
            left: -100,
            child: Container(
              width: 250,
              height: 250,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.purple.withOpacity(0.1),
              ),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 100, sigmaY: 100),
                child: Container(color: Colors.transparent),
              ),
            ),
          ),
          
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            "Namaskar, Pilgrim!",
                            style: TextStyle(
                              fontSize: 28, 
                              fontWeight: FontWeight.w900,
                              color: Colors.white,
                              letterSpacing: -1,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            "Your live Wari companion.",
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.white.withOpacity(0.7),
                            ),
                          ),
                        ],
                      ),
                      IconButton(
                        icon: Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.08),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.logout_rounded, color: Colors.redAccent, size: 20),
                        ),
                        onPressed: () {
                          Navigator.pushReplacement(
                            context,
                            MaterialPageRoute(builder: (context) => const LoginScreen()),
                          );
                        },
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  
                  // Status Glass Card
                  SpringButton(
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => const FamilyLocatorScreen()),
                      );
                    },
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.05),
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(color: Colors.white.withOpacity(0.1)),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.2),
                            blurRadius: 20,
                            offset: const Offset(0, 10),
                          )
                        ],
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(24),
                        child: BackdropFilter(
                          filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
                          child: Padding(
                            padding: const EdgeInsets.all(20.0),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text("Live GPS & Dindi Group", style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 12)),
                                    const SizedBox(height: 4),
                                    const Text("Sector 4, Alandi Route", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Colors.white)),
                                  ],
                                ),
                                Container(
                                  padding: const EdgeInsets.all(10),
                                  decoration: BoxDecoration(
                                    color: Colors.orange.withOpacity(0.2),
                                    shape: BoxShape.circle,
                                  ),
                                  child: const Icon(Icons.my_location, color: Colors.orange, size: 20),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 28),
                  const Text("Quick Actions", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white)),
                  const SizedBox(height: 16),
                  
                  // Grid of Custom Actions
                  GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: 2,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    children: [
                      _buildActionCard(context, Icons.medical_services_rounded, "Nearby Services", Colors.blue, const NearbyServicesScreen()),
                      _buildActionCard(context, Icons.person_search_rounded, "Missing Person", Colors.orange, const MissingPersonScreen()),
                      _buildActionCard(context, Icons.groups_rounded, "Family Locator", Colors.teal, const FamilyLocatorScreen()),
                      _buildActionCard(context, Icons.temple_hindu_rounded, "Temple Queue", Colors.purple, const TempleQueueScreen()),
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

  Widget _buildActionCard(BuildContext context, IconData icon, String title, Color color, Widget destinationScreen) {
    return SpringButton(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => destinationScreen),
        );
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.05),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: Colors.white.withOpacity(0.08)),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(24),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.15),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: color.withOpacity(0.2),
                        blurRadius: 15,
                      )
                    ]
                  ),
                  child: Icon(icon, size: 32, color: color),
                ),
                const SizedBox(height: 16),
                Text(
                  title, 
                  style: const TextStyle(
                    fontWeight: FontWeight.w600, 
                    color: Colors.white,
                    letterSpacing: -0.5,
                  )
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
