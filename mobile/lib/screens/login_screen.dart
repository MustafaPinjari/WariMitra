import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:ui';
import '../theme/app_theme.dart';
import '../widgets/spring_button.dart';
import '../providers/auth_provider.dart';
import 'register_screen.dart';


class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _usernameController = TextEditingController(text: 'pilgrim_1');
  final _passwordController = TextEditingController(text: 'Pilgrim@123');

  final List<Map<String, String>> _demoAccounts = [
    {'role': 'PILGRIM', 'user': 'pilgrim_1', 'pass': 'Pilgrim@123', 'label': 'वारकरी (Pilgrim)'},
    {'role': 'VOLUNTEER', 'user': 'volunteer_1', 'pass': 'Volunteer@123', 'label': 'मदतनीस (Volunteer)'},
    {'role': 'DINDI_LEADER', 'user': 'dindi_leader', 'pass': 'Dindi@Leader1', 'label': 'दिंडी प्रमुख (Dindi)'},
    {'role': 'MEDICAL_STAFF', 'user': 'medical_officer', 'pass': 'MedOfficer@123', 'label': 'वैद्यकीय अधिकारी'},
    {'role': 'POLICE_OFFICER', 'user': 'police_officer', 'pass': 'Police@1234', 'label': 'पोलीस अधिकारी'},
    {'role': 'NGO_COORDINATOR', 'user': 'ngo_coord', 'pass': 'NGO@123456', 'label': 'स्वयंसेवी संस्था'},
  ];

  Future<void> _handleLogin() async {
    final username = _usernameController.text.trim();
    final password = _passwordController.text.trim();

    if (username.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('कृपया username आणि password टाका'),
          backgroundColor: AppTheme.sosRed,
        ),
      );
      return;
    }

    final success = await ref.read(authProvider.notifier).login(username, password);

    if (!mounted) return;

    if (!success) {
      final error = ref.read(authProvider).errorMessage ?? 'Login failed';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ $error'),
          backgroundColor: AppTheme.sosRed,
        ),
      );
    }
    // On success, main.dart's authProvider watch will auto-navigate to MainNavigation
  }

  void _selectDemoAccount(Map<String, String> acc) {
    setState(() {
      _usernameController.text = acc['user']!;
      _passwordController.text = acc['pass']!;
    });
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final isLoading = authState.isLoading;

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
                  Center(
                    child: Container(
                      width: 90,
                      height: 90,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: const LinearGradient(colors: [AppTheme.bhagwaBright, AppTheme.sacredGold]),
                        boxShadow: [
                          BoxShadow(color: AppTheme.bhagwaPrimary.withValues(alpha: 0.4), blurRadius: 20)
                        ],
                      ),
                      child: Image.asset('assets/flutter_logo.png', fit: BoxFit.cover),
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
                    onTap: isLoading ? null : _handleLogin,
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: isLoading
                              ? [Colors.grey.shade700, Colors.grey.shade600]
                              : [AppTheme.bhagwaPrimary, AppTheme.bhagwaBright],
                        ),
                        borderRadius: BorderRadius.circular(18),
                        boxShadow: [
                          BoxShadow(
                            color: AppTheme.bhagwaPrimary.withValues(alpha: isLoading ? 0.1 : 0.4),
                            blurRadius: 15,
                            offset: const Offset(0, 5),
                          )
                        ],
                      ),
                      child: Center(
                        child: isLoading
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                              )
                            : const Text(
                                'लॉगिन करा • Sign In',
                                style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Colors.white),
                              ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 18),

                  Center(
                    child: GestureDetector(
                      onTap: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(builder: (_) => const RegisterScreen()),
                        );
                      },
                      child: RichText(
                        text: TextSpan(
                          style: const TextStyle(fontSize: 13, color: Colors.white70),
                          children: [
                            const TextSpan(text: 'नवीन आहात? '),
                            TextSpan(
                              text: 'खाते तयार करा • Register Here',
                              style: TextStyle(
                                color: AppTheme.bhagwaBright,
                                fontWeight: FontWeight.bold,
                                decoration: TextDecoration.underline,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 28),


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
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.blue.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.blue.withValues(alpha: 0.3)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.info_outline_rounded, color: Colors.blueAccent, size: 16),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Demo: Select a role chip above to auto-fill credentials',
                            style: TextStyle(color: Colors.white.withValues(alpha: 0.7), fontSize: 11),
                          ),
                        ),
                      ],
                    ),
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
