import 'package:flutter/material.dart';
import 'dart:ui';
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
    {'role': 'PILGRIM', 'user': 'pilgrim_1', 'pass': 'Pilgrim@123', 'label': 'Pilgrim (Ramesh)'},
    {'role': 'VOLUNTEER', 'user': 'volunteer_1', 'pass': 'Volunteer@123', 'label': 'Volunteer (Priya)'},
    {'role': 'DINDI_LEADER', 'user': 'dindi_leader', 'pass': 'Dindi@Leader1', 'label': 'Dindi Leader (Vitthal)'},
    {'role': 'MEDICAL_STAFF', 'user': 'medical_officer', 'pass': 'MedOfficer@123', 'label': 'Medical Officer'},
    {'role': 'POLICE_OFFICER', 'user': 'police_officer', 'pass': 'Police@1234', 'label': 'Police Officer'},
    {'role': 'NGO_COORDINATOR', 'user': 'ngo_coord', 'pass': 'NGO@123456', 'label': 'NGO Coordinator'},
  ];

  void _handleLogin() async {
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(milliseconds: 600));
    setState(() => _isLoading = false);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('✅ Logged in as ${_usernameController.text} [$_selectedRole]'),
          backgroundColor: Colors.orange,
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
      backgroundColor: const Color(0xFF0F1115),
      body: Stack(
        children: [
          // Background Glows
          Positioned(
            top: -100,
            left: -100,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.orange.withValues(alpha: 0.15),
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
                  const SizedBox(height: 20),
                  // Logo
                  Center(
                    child: Image.asset(
                      'assets/images/splash_logo.png',
                      width: 140,
                      height: 140,
                      fit: BoxFit.contain,
                    ),
                  ),
                  const SizedBox(height: 24),

                  const Text(
                    'Welcome Back',
                    style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900, color: Colors.white),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Sign in to access your Wari services',
                    style: TextStyle(fontSize: 14, color: Colors.white.withValues(alpha: 0.6)),
                  ),
                  const SizedBox(height: 28),

                  // Input Username
                  _buildInputLabel('Username / Mobile'),
                  TextField(
                    controller: _usernameController,
                    style: const TextStyle(color: Colors.white),
                    decoration: _buildInputDecoration(hint: 'Enter username', icon: Icons.person_rounded),
                  ),
                  const SizedBox(height: 16),

                  // Input Password
                  _buildInputLabel('Password'),
                  TextField(
                    controller: _passwordController,
                    obscureText: true,
                    style: const TextStyle(color: Colors.white),
                    decoration: _buildInputDecoration(hint: 'Enter password', icon: Icons.lock_rounded),
                  ),
                  const SizedBox(height: 28),

                  // Submit Button
                  SpringButton(
                    onTap: _isLoading ? null : _handleLogin,
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(colors: [Colors.orange, Colors.deepOrange]),
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(color: Colors.orange.withValues(alpha: 0.4), blurRadius: 20, offset: const Offset(0, 8))
                        ],
                      ),
                      child: Center(
                        child: Text(
                          _isLoading ? 'Authenticating...' : 'Sign In',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 32),

                  // Quick Demo Accounts
                  Text(
                    'Quick Demo Accounts',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white.withValues(alpha: 0.8)),
                  ),
                  const SizedBox(height: 12),

                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _demoAccounts.map((acc) {
                      final isSelected = _usernameController.text == acc['user'];
                      return ActionChip(
                        label: Text(acc['label']!),
                        backgroundColor: isSelected ? Colors.orange.withValues(alpha: 0.25) : Colors.white.withValues(alpha: 0.05),
                        side: BorderSide(color: isSelected ? Colors.orange : Colors.white.withValues(alpha: 0.1)),
                        labelStyle: TextStyle(
                          color: isSelected ? Colors.orange : Colors.grey,
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
        style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.white.withValues(alpha: 0.8)),
      ),
    );
  }

  InputDecoration _buildInputDecoration({required String hint, required IconData icon}) {
    return InputDecoration(
      hintText: hint,
      prefixIcon: Icon(icon, color: Colors.grey, size: 20),
      hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.3), fontSize: 13),
      filled: true,
      fillColor: Colors.white.withValues(alpha: 0.05),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: Colors.orange),
      ),
    );
  }
}
