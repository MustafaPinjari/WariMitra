import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import '../theme/app_theme.dart';
import '../services/heritage_service.dart';

class HeritageScreen extends StatefulWidget {
  const HeritageScreen({super.key});


  @override
  State<HeritageScreen> createState() => _HeritageScreenState();
}

class _HeritageScreenState extends State<HeritageScreen> {
  // Data
  List<SaintModel> _saints = [];
  List<AbhangModel> _abhangs = [];
  bool _isLoading = true;
  int? _selectedSaintId;
  String _selectedCategory = 'All';

  // Audio Player
  late AudioPlayer _audioPlayer;
  AbhangModel? _currentTrack;
  bool _isPlaying = false;
  Duration _position = Duration.zero;
  Duration _duration = Duration.zero;

  final List<String> _categories = ['All', 'Abhang', 'Haripath', 'Pasaydan', 'Bhajan'];

  @override
  void initState() {
    super.initState();
    _initAudioPlayer();
    _fetchData();
  }

  void _initAudioPlayer() {
    _audioPlayer = AudioPlayer();

    _audioPlayer.onPlayerStateChanged.listen((state) {
      if (mounted) {
        setState(() {
          _isPlaying = state == PlayerState.playing;
        });
      }
    });

    _audioPlayer.onPositionChanged.listen((p) {
      if (mounted) {
        setState(() {
          _position = p;
        });
      }
    });

    _audioPlayer.onDurationChanged.listen((d) {
      if (mounted) {
        setState(() {
          _duration = d;
        });
      }
    });
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

  Future<void> _fetchData() async {
    setState(() => _isLoading = true);
    final saints = await HeritageService.fetchSaints();
    final abhangs = await HeritageService.fetchAbhangs(
      saintId: _selectedSaintId,
      category: _selectedCategory,
    );

    if (mounted) {
      setState(() {
        _saints = saints;
        _abhangs = abhangs;
        _isLoading = false;
        if (_currentTrack == null && _abhangs.isNotEmpty) {
          _currentTrack = _abhangs.first;
        }
      });
    }
  }

  Future<void> _playTrack(AbhangModel track) async {
    if (_currentTrack?.id == track.id && _isPlaying) {
      await _audioPlayer.pause();
    } else {
      setState(() {
        _currentTrack = track;
      });
      await _audioPlayer.stop();
      if (track.audioUrl.isNotEmpty) {
        await _audioPlayer.play(UrlSource(track.audioUrl));
      }
    }
  }

  Future<void> _togglePlayPause() async {
    if (_currentTrack == null) return;
    if (_isPlaying) {
      await _audioPlayer.pause();
    } else {
      if (_currentTrack!.audioUrl.isNotEmpty) {
        await _audioPlayer.play(UrlSource(_currentTrack!.audioUrl));
      }
    }
  }

  String _formatDuration(Duration d) {
    final minutes = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    return "$minutes:$seconds";
  }

  void _showLyricsModal(AbhangModel track) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.surfaceDark,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(24),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [

                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: AppTheme.bhagwaBright.withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              track.category.toUpperCase(),
                              style: const TextStyle(
                                color: AppTheme.bhagwaBright,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            track.marathiTitle,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            track.saintMarathiName.isNotEmpty
                                ? track.saintMarathiName
                                : track.artist,
                            style: TextStyle(
                              color: Colors.white.withValues(alpha: 0.7),
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close_rounded, color: Colors.white70),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),
                const Divider(color: Colors.white12, height: 24),
                const Text(
                  'अभंग शब्द (Marathi Lyrics)',
                  style: TextStyle(
                    color: AppTheme.sacredGold,
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  track.lyrics.isNotEmpty ? track.lyrics : 'शब्द उपलब्ध नाहीत.',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    height: 1.6,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                if (track.translation != null && track.translation!.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  const Text(
                    'Meaning / Translation',
                    style: TextStyle(
                      color: AppTheme.bhagwaBright,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    track.translation!,
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.8),
                      fontSize: 12,
                      height: 1.5,
                    ),
                  ),
                ],
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.pop(context);
                      _playTrack(track);
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.bhagwaPrimary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),

                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    ),
                    icon: Icon(_currentTrack?.id == track.id && _isPlaying
                        ? Icons.pause_rounded
                        : Icons.play_arrow_rounded),
                    label: Text(_currentTrack?.id == track.id && _isPlaying
                        ? 'Pause Audio'
                        : 'Play Audio Stream'),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final filteredAbhangs = _abhangs.where((a) {
      final matchesSaint = _selectedSaintId == null || a.saintId == _selectedSaintId;
      final matchesCat = _selectedCategory == 'All' || a.category == _selectedCategory;
      return matchesSaint && matchesCat;
    }).toList();

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      body: SafeArea(
        child: Stack(
          children: [
            RefreshIndicator(
              onRefresh: _fetchData,
              color: AppTheme.bhagwaBright,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.only(left: 18, right: 18, top: 16, bottom: 130),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header
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
                              style: TextStyle(fontSize: 19, fontWeight: FontWeight.bold, color: Colors.white),
                            ),
                            Text(
                              'Vari Heritage & Abhang Audio Player',
                              style: TextStyle(fontSize: 11, color: AppTheme.bhagwaBright, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),

                    // Featured Banner Card
                    if (_currentTrack != null) _buildFeaturedPlayerCard(),

                    const SizedBox(height: 20),

                    // Category Pill Filters
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: _categories.map((cat) {
                          final isSelected = _selectedCategory == cat;
                          return Padding(
                            padding: const EdgeInsets.only(right: 8),
                            child: FilterChip(
                              label: Text(
                                cat == 'All' ? 'सर्व (All)' : cat,
                                style: TextStyle(
                                  color: isSelected ? Colors.black : Colors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                              selected: isSelected,
                              selectedColor: AppTheme.sacredGold,
                              backgroundColor: AppTheme.surfaceDark,
                              checkmarkColor: Colors.black,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(20),
                                side: BorderSide(
                                  color: isSelected
                                      ? AppTheme.sacredGold
                                      : Colors.white.withValues(alpha: 0.1),
                                ),
                              ),
                              onSelected: (_) {
                                setState(() {
                                  _selectedCategory = cat;
                                });
                              },
                            ),
                          );
                        }).toList(),
                      ),
                    ),

                    const SizedBox(height: 20),

                    // Saints Carousel
                    const Text(
                      'महाराष्ट्राचे संत • Patron Saints',
                      style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                    const SizedBox(height: 10),

                    if (_saints.isNotEmpty)
                      SizedBox(
                        height: 95,
                        child: ListView.builder(
                          scrollDirection: Axis.horizontal,
                          itemCount: _saints.length,
                          itemBuilder: (context, index) {
                            final saint = _saints[index];
                            final isSelected = _selectedSaintId == saint.id;
                            return GestureDetector(
                              onTap: () {
                                setState(() {
                                  _selectedSaintId = isSelected ? null : saint.id;
                                });
                              },
                              child: Container(
                                width: 200,
                                margin: const EdgeInsets.only(right: 12),
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: isSelected
                                      ? AppTheme.bhagwaPrimary.withValues(alpha: 0.25)
                                      : AppTheme.surfaceDark,
                                  borderRadius: BorderRadius.circular(18),
                                  border: Border.all(
                                    color: isSelected
                                        ? AppTheme.sacredGold
                                        : Colors.white.withValues(alpha: 0.1),
                                  ),
                                ),
                                child: Row(
                                  children: [
                                    Container(
                                      width: 44,
                                      height: 44,
                                      decoration: BoxDecoration(
                                        color: AppTheme.bhagwaPrimary.withValues(alpha: 0.3),
                                        shape: BoxShape.circle,
                                        border: Border.all(color: AppTheme.sacredGold.withValues(alpha: 0.5)),
                                      ),
                                      child: Center(
                                        child: Text(
                                          saint.marathiName.isNotEmpty
                                              ? saint.marathiName[0]
                                              : saint.name[0],
                                          style: const TextStyle(
                                            color: AppTheme.sacredGold,
                                            fontWeight: FontWeight.w900,
                                            fontSize: 18,
                                          ),
                                        ),
                                      ),
                                    ),
                                    const SizedBox(width: 10),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        mainAxisAlignment: MainAxisAlignment.center,
                                        children: [
                                          Text(
                                            saint.marathiName,
                                            maxLines: 1,
                                            overflow: TextOverflow.ellipsis,
                                            style: const TextStyle(
                                              color: Colors.white,
                                              fontWeight: FontWeight.bold,
                                              fontSize: 12,
                                            ),
                                          ),
                                          const SizedBox(height: 2),
                                          Text(
                                            saint.era,
                                            maxLines: 1,
                                            overflow: TextOverflow.ellipsis,
                                            style: const TextStyle(
                                              color: AppTheme.bhagwaBright,
                                              fontSize: 10,
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ),

                    const SizedBox(height: 24),

                    // Audio Track List
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'अभंग व भक्ती संगीत यादी',
                          style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                        Text(
                          '${filteredAbhangs.length} Songs',
                          style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 12),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),

                    if (_isLoading)
                      const Padding(
                        padding: EdgeInsets.all(30),
                        child: Center(
                          child: CircularProgressIndicator(color: AppTheme.sacredGold),
                        ),
                      )

                    else if (filteredAbhangs.isEmpty)
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(24),
                        decoration: BoxDecoration(
                          color: AppTheme.surfaceDark,
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
                        ),
                        child: const Column(
                          children: [
                            Icon(Icons.music_off_rounded, color: Colors.white38, size: 40),
                            SizedBox(height: 8),
                            Text('कोणतेही अभंग उपलब्ध नाहीत.', style: TextStyle(color: Colors.white70, fontSize: 13)),
                          ],
                        ),
                      )
                    else
                      ListView.separated(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: filteredAbhangs.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 10),
                        itemBuilder: (context, index) {
                          final track = filteredAbhangs[index];
                          final isSelectedTrack = _currentTrack?.id == track.id;
                          final isThisPlaying = isSelectedTrack && _isPlaying;

                          return Container(
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                            decoration: BoxDecoration(
                              color: isSelectedTrack
                                  ? AppTheme.bhagwaPrimary.withValues(alpha: 0.15)
                                  : AppTheme.surfaceDark,
                              borderRadius: BorderRadius.circular(18),
                              border: Border.all(
                                color: isSelectedTrack
                                    ? AppTheme.bhagwaBright
                                    : Colors.white.withValues(alpha: 0.08),
                              ),
                            ),
                            child: Row(
                              children: [
                                IconButton(
                                  icon: Container(
                                    padding: const EdgeInsets.all(8),
                                    decoration: BoxDecoration(
                                      color: isThisPlaying ? AppTheme.bhagwaBright : Colors.white12,
                                      shape: BoxShape.circle,
                                    ),
                                    child: Icon(
                                      isThisPlaying ? Icons.pause_rounded : Icons.play_arrow_rounded,
                                      color: isThisPlaying ? Colors.black : Colors.white,
                                      size: 20,
                                    ),
                                  ),
                                  onPressed: () => _playTrack(track),
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        track.marathiTitle,
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                        style: TextStyle(
                                          color: isSelectedTrack ? AppTheme.sacredGold : Colors.white,
                                          fontWeight: FontWeight.bold,
                                          fontSize: 14,
                                        ),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        '${track.saintMarathiName.isNotEmpty ? track.saintMarathiName : track.artist} • ${track.category}',
                                        style: TextStyle(
                                          color: Colors.white.withValues(alpha: 0.6),
                                          fontSize: 11,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                TextButton(
                                  onPressed: () => _showLyricsModal(track),
                                  child: const Text(
                                    'शब्द',
                                    style: TextStyle(color: AppTheme.bhagwaBright, fontSize: 12, fontWeight: FontWeight.bold),
                                  ),
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                  ],
                ),
              ),
            ),

            // Floating Sticky Bottom Audio Player Bar
            if (_currentTrack != null)
              Positioned(
                left: 12,
                right: 12,
                bottom: 16,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF1E170E), Color(0xFF2D1B0F)],
                    ),
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: AppTheme.sacredGold.withValues(alpha: 0.4)),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.5),
                        blurRadius: 16,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.music_note_rounded, color: AppTheme.sacredGold, size: 24),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _currentTrack!.marathiTitle,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 13,
                                  ),
                                ),
                                Text(
                                  _currentTrack!.saintMarathiName.isNotEmpty
                                      ? _currentTrack!.saintMarathiName
                                      : _currentTrack!.artist,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: const TextStyle(
                                    color: AppTheme.bhagwaBright,
                                    fontSize: 10,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          IconButton(
                            icon: Icon(
                              _isPlaying ? Icons.pause_circle_filled_rounded : Icons.play_circle_fill_rounded,
                              color: AppTheme.sacredGold,
                              size: 36,
                            ),
                            onPressed: _togglePlayPause,
                          ),
                        ],
                      ),
                      // Progress Bar Slider
                      Row(
                        children: [
                          Text(
                            _formatDuration(_position),
                            style: const TextStyle(color: Colors.white54, fontSize: 9),
                          ),
                          Expanded(
                            child: SliderTheme(
                              data: SliderThemeData(
                                trackHeight: 3,
                                thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 5),
                                overlayShape: const RoundSliderOverlayShape(overlayRadius: 10),
                                activeTrackColor: AppTheme.bhagwaBright,
                                inactiveTrackColor: Colors.white24,
                                thumbColor: AppTheme.sacredGold,
                              ),
                              child: Slider(
                                min: 0.0,
                                max: _duration.inSeconds > 0 ? _duration.inSeconds.toDouble() : 100.0,
                                value: _position.inSeconds.toDouble().clamp(
                                      0.0,
                                      _duration.inSeconds > 0 ? _duration.inSeconds.toDouble() : 100.0,
                                    ),
                                onChanged: (val) {
                                  _audioPlayer.seek(Duration(seconds: val.toInt()));
                                },
                              ),
                            ),
                          ),
                          Text(
                            _formatDuration(_duration),
                            style: const TextStyle(color: Colors.white54, fontSize: 9),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeaturedPlayerCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppTheme.bhagwaPrimary, Color(0xFFD97706)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(22),
        boxShadow: [
          BoxShadow(
            color: AppTheme.bhagwaPrimary.withValues(alpha: 0.35),
            blurRadius: 15,
            offset: const Offset(0, 6),
          )
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: const BoxDecoration(color: Colors.white24, shape: BoxShape.circle),
                child: const Icon(Icons.library_music_rounded, color: Colors.white, size: 26),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _currentTrack!.marathiTitle,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 15),
                    ),
                    Text(
                      '${_currentTrack!.saintMarathiName} • ${_currentTrack!.artist}',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _togglePlayPause,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: AppTheme.bhagwaPrimary,
                    padding: const EdgeInsets.symmetric(vertical: 10),

                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  icon: Icon(_isPlaying ? Icons.pause_rounded : Icons.play_arrow_rounded),
                  label: Text(
                    _isPlaying ? 'थांबवा (Pause)' : 'ऐका (Listen Audio)',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              OutlinedButton.icon(
                onPressed: () => _showLyricsModal(_currentTrack!),
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.white,
                  side: const BorderSide(color: Colors.white60),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                icon: const Icon(Icons.menu_book_rounded, size: 16),
                label: const Text('शब्द', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
