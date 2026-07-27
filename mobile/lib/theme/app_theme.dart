import 'package:flutter/material.dart';

/// AppTheme defines the signature visual identity for WariMitra
/// Rooted in Maharashtra's rich Wari pilgrimage heritage:
/// - Bhagwa Saffron (#E85D04): Primary color for devotion, high visibility, and energy.
/// - Royal Maratha Navy (#0F172A): Deep authoritative color for government & emergency command.
/// - Sacred Gold (#D97706): Warm accent for Palkhi tracking, notifications, and badges.
/// - Vithoba Kesari / Maroon (#7C2D12): High priority emergency states.
class AppTheme {
  static const Color bhagwaPrimary = Color(0xFFE85D04);
  static const Color bhagwaBright = Color(0xFFF97316);
  static const Color bhagwaLight = Color(0xFFFFECE0);
  
  static const Color marathaNavy = Color(0xFF0F172A);
  static const Color marathaNavyCard = Color(0xFF1E293B);
  
  static const Color sacredGold = Color(0xFFD97706);
  static const Color sacredGoldLight = Color(0xFFFEF3C7);

  static const Color vithobaKesari = Color(0xFF7C2D12);
  static const Color sosRed = Color(0xFFDC2626);
  
  static const Color bgDark = Color(0xFF0D1117);
  static const Color surfaceDark = Color(0xFF161B22);
  static const Color surfaceBorder = Color(0xFF30363D);

  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      primaryColor: bhagwaPrimary,
      scaffoldBackgroundColor: bgDark,
      colorScheme: const ColorScheme.dark(
        primary: bhagwaPrimary,
        secondary: sacredGold,
        surface: surfaceDark,
        background: bgDark,
        error: sosRed,
      ),
      fontFamily: 'Roboto', // Default fallback, paired with Devanagari support
      cardTheme: CardThemeData(
        color: surfaceDark,
        elevation: 4,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: surfaceBorder, width: 1),
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: marathaNavy,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          fontSize: 24,
          fontWeight: FontWeight.w900,
          color: Colors.white,
          letterSpacing: -0.5,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: bhagwaPrimary,
          foregroundColor: Colors.white,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          textStyle: const TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w900,
            letterSpacing: 0.2,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0xFF21262D),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: surfaceBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: surfaceBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: bhagwaPrimary, width: 1.5),
        ),
        hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 13),
      ),
    );
  }
}
