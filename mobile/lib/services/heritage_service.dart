import 'package:flutter/foundation.dart';
import 'api_service.dart';


class SaintModel {
  final int id;
  final String name;
  final String marathiName;
  final String title;
  final String era;
  final String biography;
  final String? imageUrl;
  final int abhangCount;

  SaintModel({
    required this.id,
    required this.name,
    required this.marathiName,
    required this.title,
    required this.era,
    required this.biography,
    this.imageUrl,
    this.abhangCount = 0,
  });

  factory SaintModel.fromJson(Map<String, dynamic> json) {
    return SaintModel(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      marathiName: json['marathi_name'] ?? json['name'] ?? '',
      title: json['title'] ?? '',
      era: json['era'] ?? '',
      biography: json['biography'] ?? '',
      imageUrl: json['image_url'],
      abhangCount: json['abhang_count'] ?? 0,
    );
  }
}

class AbhangModel {
  final int id;
  final int? saintId;
  final String saintName;
  final String saintMarathiName;
  final String title;
  final String marathiTitle;
  final String artist;
  final String category;
  final String lyrics;
  final String? translation;
  final String audioUrl;
  final String duration;

  AbhangModel({
    required this.id,
    this.saintId,
    required this.saintName,
    required this.saintMarathiName,
    required this.title,
    required this.marathiTitle,
    required this.artist,
    required this.category,
    required this.lyrics,
    this.translation,
    required this.audioUrl,
    required this.duration,
  });

  factory AbhangModel.fromJson(Map<String, dynamic> json) {
    return AbhangModel(
      id: json['id'] ?? 0,
      saintId: json['saint'],
      saintName: json['saint_name'] ?? '',
      saintMarathiName: json['saint_marathi_name'] ?? '',
      title: json['title'] ?? '',
      marathiTitle: json['marathi_title'] ?? json['title'] ?? '',
      artist: json['artist'] ?? 'Traditional',
      category: json['category'] ?? 'Abhang',
      lyrics: json['lyrics'] ?? '',
      translation: json['translation'],
      audioUrl: json['audio_url'] ?? '',
      duration: json['duration'] ?? '03:30',
    );
  }
}

class HeritageService {
  static Future<List<SaintModel>> fetchSaints() async {
    try {
      final response = await ApiService.dio.get('/heritage/saints/');
      final data = response.data;
      final List list = data is List ? data : (data['results'] ?? []);
      return list.map((json) => SaintModel.fromJson(json)).toList();
    } catch (e) {
      debugPrint('Error fetching saints: $e');

      return [];
    }
  }

  static Future<List<AbhangModel>> fetchAbhangs({int? saintId, String? category}) async {
    try {
      final Map<String, dynamic> queryParams = {};
      if (saintId != null) queryParams['saint'] = saintId;
      if (category != null && category != 'All') queryParams['category'] = category;

      final response = await ApiService.dio.get('/heritage/abhangs/', queryParameters: queryParams);
      final data = response.data;
      final List list = data is List ? data : (data['results'] ?? []);
      return list.map((json) => AbhangModel.fromJson(json)).toList();
    } catch (e) {
      debugPrint('Error fetching abhangs: $e');

      return [];
    }
  }
}
