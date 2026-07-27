import 'package:flutter/material.dart';
import 'dart:ui';
import '../theme/app_theme.dart';
import '../widgets/spring_button.dart';
import '../main.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController(text: 'pilgrim_1');
  final _passwordController = TextEditingController(text: 'Pilgrim@123');
  String _selectedRole = 'PILGRIM';
  bool _isLoading = false;

  final List<Map<String, String>> _demoAccounts = [
    {'role': 'PILGRIM', 'user': 'pilgrim_1', 'pass': 'Pilgrim@123', 'label': 'वारकरी (Pilgrim)'},
    {'role': 'VOLUNTEER', 'user': 'volunteer_1', 'pass': 'Volunteer@123', 'label': 'मदतनीस (Volunteer)'},
    {'role': 'DINDI_LEADER', 'user': 'dindi_leader', 'pass': 'Dindi@Leader1', 'label': 'दिंडी प्रमुख (Dindi)'},
    {'role': 'MEDICAL_STAFF', 'user': 'medical_officer', 'pass': 'MedOfficer@123', 'label': 'वैद्यकीय अधिकारी'},
    {'role': 'POLICE_OFFICER', 'user': 'police_officer', 'pass': 'Police@1234', 'label': 'पोलीस अधिकारी'},
    {'role': 'NGO_COORDINATOR', 'user': 'ngo_coord', 'pass': 'NGO@123456', 'label': 'स्वयंसेवी संस्था'},
  ];

  void _handleLogin() async {
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(milliseconds: 500));
    setState(() => _isLoading = false);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('✅ स्वागत आहे! (Logged in as ${_usernameController.text})'),
          backgroundColor: AppTheme.bhagwaPrimary,
        ),
      );
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const MainNavigation()),
      );
    }
  }

  void _selectDemoAccount(Map<String, String> acc) {
    setState(() {
      _selectedRole = acc['role']!;
      _usernameController.text = acc['user']!;
      _passwordController.text = acc['pass']!;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      body: Stack(
        children: [
          Positioned(
            top: -100,
            left: -100,
            child: Container(
              width: 320,
              height: 320,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppTheme.bhagwaPrimary.withValues(alpha: 0.18),
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
                  const SizedBox(height: 10),
                  // Logo Emblem
                  Center(
                    child: Container(
                      width: 90,
                      height: 90,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: const LinearGradient(colors: [AppTheme.bhagwaBright, AppTheme.sacredGold]),
                        boxShadow: [
                          BoxShadow(color: AppTheme.bhagwaPrimary.withValues(alpha: 0.4), blurRadius: 20)
                        ]
                      ),
                      child: Image.asset('assets/flutter_logo.png', fit: BoxFit.cover)
                    ),
                  ),
                  const SizedBox(height: 24),

                  const Text(
                    'वारीमित्र लॉगिन',
                    style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900, color: Colors.white),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Sign in to access your Wari pilgrim & responder services',
                    style: TextStyle(fontSize: 12, color: Colors.white.withValues(alpha: 0.6), fontWeight: FontWeight.w500),
                  ),
                  const SizedBox(height: 28),

                  _buildInputLabel('उपयोगकर्ता नाव • Username'),
                  TextField(
                    controller: _usernameController,
                    style: const TextStyle(color: Colors.white, fontSize: 14),
                    decoration: _buildInputDecoration(hint: 'Enter username', icon: Icons.person_rounded),
                  ),
                  const SizedBox(height: 16),

                  _buildInputLabel('संकेतशब्द • Password'),
                  TextField(
                    controller: _passwordController,
                    obscureText: true,
                    style: const TextStyle(color: Colors.white, fontSize: 14),
                    decoration: _buildInputDecoration(hint: 'Enter password', icon: Icons.lock_rounded),
                  ),
                  const SizedBox(height: 28),

                  SpringButton(
                    onTap: _isLoading ? null : _handleLogin,
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(colors: [AppTheme.bhagwaPrimary, AppTheme.bhagwaBright]),
                        borderRadius: BorderRadius.circular(18),
                        boxShadow: [
                          BoxShadow(color: AppTheme.bhagwaPrimary.withValues(alpha: 0.4), blurRadius: 15, offset: const Offset(0, 5))
                        ],
                      ),
                      child: Center(
                        child: Text(
                          _isLoading ? 'प्रमाणित करत आहे...' : 'लॉगिन करा • Sign In',
                          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Colors.white),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 32),

                  Text(
                    'द्रुत भूमिका निवड • Quick Role Selector',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.white.withValues(alpha: 0.8)),
                  ),
                  const SizedBox(height: 12),

                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _demoAccounts.map((acc) {
                      final isSelected = _usernameController.text == acc['user'];
                      return ActionChip(
                        label: Text(acc['label']!),
                        backgroundColor: isSelected ? AppTheme.bhagwaPrimary.withValues(alpha: 0.25) : AppTheme.surfaceDark,
                        side: BorderSide(color: isSelected ? AppTheme.bhagwaPrimary : Colors.white.withValues(alpha: 0.1)),
                        labelStyle: TextStyle(
                          color: isSelected ? AppTheme.bhagwaBright : Colors.white70,
                          fontSize: 12,
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                        ),
                        onPressed: () => _selectDemoAccount(acc),
                      );
                    }).toList(),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInputLabel(String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6.0),
      child: Text(
        label,
        style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white.withValues(alpha: 0.8)),
      ),
    );
  }

  InputDecoration _buildInputDecoration({required String hint, required IconData icon}) {
    return InputDecoration(
      hintText: hint,
      prefixIcon: Icon(icon, color: AppTheme.bhagwaBright, size: 20),
      hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.3), fontSize: 13),
      filled: true,
      fillColor: AppTheme.surfaceDark,
    );
  }
}
