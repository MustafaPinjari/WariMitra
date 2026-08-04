"use client";

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BookOpen, Play, Pause, Sparkles, Volume2, VolumeX, Music, Plus, 
  Upload, Trash2, Edit3, CheckCircle2, ShieldAlert, Layers, Search, 
  FileAudio, CloudUpload, ArrowRight, X, ListMusic, User, RefreshCw
} from 'lucide-react';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';
import { heritageService } from '@/lib/api';

interface Saint {
  id: number;
  name: string;
  marathi_name: string;
  title: string;
  era: string;
  biography: string;
  image_url?: string;
  abhang_count?: number;
}

interface Abhang {
  id: number;
  saint?: number | null;
  saint_name?: string;
  saint_marathi_name?: string;
  saint_image_url?: string;
  title: string;
  marathi_title: string;
  artist?: string;
  category: string;
  lyrics: string;
  translation?: string;
  audio_url: string;
  duration?: string;
  created_at?: string;
}

const CATEGORIES = ['All', 'Abhang', 'Haripath', 'Pasaydan', 'Bhajan', 'Kirtan'];

export default function HeritagePage() {
  const { t } = useAccessibility();
  const [activeTab, setActiveTab] = useState<'explore' | 'manage'>('explore');

  // Data States
  const [saints, setSaints] = useState<Saint[]>([]);
  const [abhangs, setAbhangs] = useState<Abhang[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSaintId, setSelectedSaintId] = useState<number | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Active Audio Player State
  const [currentAbhang, setCurrentAbhang] = useState<Abhang | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Selected Lyrics Modal State
  const [lyricsModalAbhang, setLyricsModalAbhang] = useState<Abhang | null>(null);

  // Manage Studio Form States
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string>('');
  const [newAbhang, setNewAbhang] = useState({
    title: '',
    marathi_title: '',
    saint: '',
    category: 'Abhang',
    artist: '',
    duration: '03:30',
    lyrics: '',
    translation: '',
    audio_url: '',
  });

  const [newSaint, setNewSaint] = useState({
    name: '',
    marathi_name: '',
    title: '',
    era: '',
    biography: '',
    image_url: '',
  });
  const [showSaintModal, setShowSaintModal] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [saintsRes, abhangsRes] = await Promise.all([
        heritageService.getSaints().catch(() => ({ data: [] })),
        heritageService.getAbhangs().catch(() => ({ data: [] })),
      ]);

      const fetchedSaints = Array.isArray(saintsRes.data) ? saintsRes.data : saintsRes.data.results || [];
      const fetchedAbhangs = Array.isArray(abhangsRes.data) ? abhangsRes.data : abhangsRes.data.results || [];

      setSaints(fetchedSaints);
      setAbhangs(fetchedAbhangs);

      if (fetchedAbhangs.length > 0 && !currentAbhang) {
        setCurrentAbhang(fetchedAbhangs[0]);
      }
    } catch (err) {
      console.error('Failed to load heritage data:', err);
    } finally {
      setLoading(false);
    }
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Audio Playback Handlers
  const handlePlayAbhang = (abhang: Abhang) => {
    if (currentAbhang?.id === abhang.id && isPlaying) {
      audioRef.current?.pause();
      setIsPlaying(false);
    } else {
      setCurrentAbhang(abhang);
      setIsPlaying(true);
      if (audioRef.current) {
        audioRef.current.src = abhang.audio_url;
        audioRef.current.play().catch(e => console.error("Audio play error:", e));
      }
    }
  };

  const togglePlayPause = () => {
    if (!audioRef.current || !currentAbhang) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().catch(e => console.error("Audio play error:", e));
      setIsPlaying(true);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
      setDuration(audioRef.current.duration || 0);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    setCurrentTime(time);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
  };

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const formatTime = (secs: number) => {
    if (isNaN(secs) || secs === 0) return '00:00';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
  };

  // S3 File Upload Handler
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>, isImage = false) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadProgress(`Uploading ${file.name} to AWS S3...`);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('folder', isImage ? 'heritage/saints' : 'heritage/audio');

    try {
      const res = await heritageService.uploadFile(formData);
      const fileUrl = res.data.url;

      if (isImage) {
        setNewSaint(prev => ({ ...prev, image_url: fileUrl }));
        showToast('Saint photo uploaded to AWS S3!');
      } else {
        setNewAbhang(prev => ({ ...prev, audio_url: fileUrl }));
        showToast('Audio file uploaded successfully to AWS S3!');
      }
    } catch (err: any) {
      console.error('File upload failed:', err);
      showToast('Upload failed! Please try again.');
    } finally {
      setIsUploading(false);
      setUploadProgress('');
    }
  };

  // Create Abhang
  const handleCreateAbhang = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAbhang.title || !newAbhang.marathi_title || !newAbhang.audio_url) {
      showToast('Please fill title, Marathi title, and upload audio file!');
      return;
    }

    try {
      const payload = {
        title: newAbhang.title,
        marathi_title: newAbhang.marathi_title,
        saint: newAbhang.saint ? parseInt(newAbhang.saint) : null,
        category: newAbhang.category,
        artist: newAbhang.artist || 'Traditional',
        duration: newAbhang.duration || '03:30',
        lyrics: newAbhang.lyrics,
        translation: newAbhang.translation,
        audio_url: newAbhang.audio_url,
      };

      await heritageService.createAbhang(payload);
      showToast('Abhang / Song successfully published and saved!');
      
      setNewAbhang({
        title: '',
        marathi_title: '',
        saint: '',
        category: 'Abhang',
        artist: '',
        duration: '03:30',
        lyrics: '',
        translation: '',
        audio_url: '',
      });

      fetchData();
    } catch (err) {
      console.error('Failed to create abhang:', err);
      showToast('Failed to save Abhang. Check fields and try again.');
    }
  };

  // Create Saint
  const handleCreateSaint = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSaint.name || !newSaint.marathi_name) {
      showToast('Please enter Saint name and Marathi name.');
      return;
    }

    try {
      await heritageService.createSaint(newSaint);
      showToast('Saint added successfully!');
      setShowSaintModal(false);
      setNewSaint({ name: '', marathi_name: '', title: '', era: '', biography: '', image_url: '' });
      fetchData();
    } catch (err) {
      console.error('Failed to create saint:', err);
      showToast('Failed to add Saint.');
    }
  };

  // Delete Abhang
  const handleDeleteAbhang = async (id: number) => {
    if (!confirm('Are you sure you want to delete this audio content?')) return;
    try {
      await heritageService.deleteAbhang(id);
      showToast('Audio track deleted successfully.');
      fetchData();
    } catch (err) {
      console.error('Failed to delete abhang:', err);
      showToast('Failed to delete track.');
    }
  };

  // Filter Abhangs
  const filteredAbhangs = abhangs.filter(a => {
    const matchesSaint = !selectedSaintId || a.saint === selectedSaintId;
    const matchesCategory = selectedCategory === 'All' || a.category === selectedCategory;
    const matchesSearch = !searchQuery || 
      a.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
      a.marathi_title.includes(searchQuery) ||
      a.lyrics.includes(searchQuery);
    return matchesSaint && matchesCategory && matchesSearch;
  });

  return (
    <div className="space-y-6 pb-16 max-w-7xl mx-auto px-4 sm:px-6">
      
      {/* Hidden Global Audio Element */}
      <audio
        ref={audioRef}
        src={currentAbhang?.audio_url}
        onTimeUpdate={handleTimeUpdate}
        onEnded={() => setIsPlaying(false)}
        preload="metadata"
      />

      {/* Toast Notification */}
      <AnimatePresence>
        {toastMessage && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-6 right-6 z-50 px-5 py-3 rounded-2xl bg-gradient-to-r from-orange-600 to-amber-500 text-white font-bold text-sm shadow-2xl flex items-center gap-3 border border-white/20"
          >
            <CheckCircle2 size={20} />
            <span>{toastMessage}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Page Header */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 p-6 sm:p-8 rounded-3xl bg-[#131B2E] border border-amber-500/40 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
        
        <div className="flex items-center gap-4 relative z-10">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-orange-500 to-amber-500 p-0.5 shadow-lg flex-shrink-0">
            <div className="w-full h-full rounded-[14px] bg-[#131B2E] flex items-center justify-center text-amber-400">
              <BookOpen size={30} />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full bg-orange-500/20 text-orange-400 text-[10px] font-black uppercase tracking-wider border border-orange-500/30">
                Wari Heritage Studio
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight mt-1">
              {t('पालखी सोहळा वारसा व अभंग गाथा', 'Vari Heritage & Spiritual Audio Guide')}
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 font-medium mt-0.5">
              {t('वारकरी संप्रदाय अभंग, हरिपाठ व संत माहिती व्यवस्थापन (S3 Cloud Storage)', 'Explore devotional hymns, saint histories, and manage audio contents via AWS S3')}
            </p>
          </div>
        </div>

        {/* Tab Switchers */}
        <div className="flex items-center p-1.5 rounded-2xl bg-[#0B0F19] border border-white/10 relative z-10 w-full lg:w-auto">
          <button
            onClick={() => setActiveTab('explore')}
            className={`flex-1 lg:flex-initial px-5 py-2.5 rounded-xl font-extrabold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all ${
              activeTab === 'explore'
                ? 'bg-gradient-to-r from-orange-600 to-amber-500 text-white shadow-lg'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Music size={16} />
            <span>{t('अभंग गाथा (Explore)', 'Abhang Audio Gallery')}</span>
          </button>
          <button
            onClick={() => setActiveTab('manage')}
            className={`flex-1 lg:flex-initial px-5 py-2.5 rounded-xl font-extrabold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all ${
              activeTab === 'manage'
                ? 'bg-gradient-to-r from-orange-600 to-amber-500 text-white shadow-lg'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <CloudUpload size={16} />
            <span>{t('सामग्री व्यवस्थापन (S3 Upload Studio)', 'Manage Audio & S3')}</span>
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      {activeTab === 'explore' ? (
        <div className="space-y-6">

          {/* Sticky/Featured Player Banner */}
          {currentAbhang && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-6 rounded-3xl bg-gradient-to-r from-[#1E170E] via-[#2D1B0F] to-[#131B2E] border border-amber-500/40 shadow-2xl space-y-4"
            >
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 shadow-inner flex-shrink-0">
                    <FileAudio size={28} className={isPlaying ? 'animate-bounce' : ''} />
                  </div>
                  <div>
                    <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-extrabold text-[10px] uppercase tracking-wider">
                      {currentAbhang.category || 'Abhang'}
                    </span>
                    <h3 className="text-lg font-black text-white mt-0.5">
                      {currentAbhang.marathi_title}
                    </h3>
                    <p className="text-xs text-amber-200/70 font-semibold">
                      {currentAbhang.saint_marathi_name ? `${currentAbhang.saint_marathi_name} • ` : ''}
                      {currentAbhang.artist || 'Traditional Singer'}
                    </p>
                  </div>
                </div>

                {/* Player Controls */}
                <div className="flex items-center gap-4 w-full md:w-auto justify-between md:justify-end">
                  <button
                    onClick={() => setLyricsModalAbhang(currentAbhang)}
                    className="px-3 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-amber-300 font-bold text-xs flex items-center gap-1.5 transition-all"
                  >
                    <BookOpen size={14} />
                    <span>{t('अभंग शब्द (Lyrics)', 'View Lyrics')}</span>
                  </button>

                  <button
                    onClick={togglePlayPause}
                    className="w-12 h-12 rounded-2xl bg-gradient-to-r from-orange-500 to-amber-500 text-white flex items-center justify-center shadow-lg hover:scale-105 transition-all"
                  >
                    {isPlaying ? <Pause size={24} /> : <Play size={24} className="ml-0.5" />}
                  </button>

                  <button
                    onClick={toggleMute}
                    className="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-slate-300 transition-all"
                  >
                    {isMuted ? <VolumeX size={18} /> : <Volume2 size={18} />}
                  </button>
                </div>
              </div>

              {/* Progress Slider */}
              <div className="space-y-1.5 pt-2 border-t border-white/10">
                <input
                  type="range"
                  min="0"
                  max={duration || 100}
                  value={currentTime}
                  onChange={handleSeek}
                  className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-orange-500"
                />
                <div className="flex justify-between text-[11px] font-bold text-amber-200/60">
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(duration)}</span>
                </div>
              </div>
            </motion.div>
          )}

          {/* Search & Category Pills */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            
            {/* Category Pills */}
            <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto pb-2 sm:pb-0 scrollbar-none">
              {CATEGORIES.map(cat => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-4 py-2 rounded-xl text-xs font-black whitespace-nowrap transition-all ${
                    selectedCategory === cat
                      ? 'bg-amber-500 text-slate-950 shadow-lg scale-105'
                      : 'bg-[#131B2E] text-slate-300 border border-white/10 hover:bg-white/10'
                  }`}
                >
                  {cat === 'All' ? t('सर्व अभंग', 'All Hymns') : cat}
                </button>
              ))}
            </div>

            {/* Search Box */}
            <div className="relative w-full sm:w-72">
              <Search className="absolute left-3.5 top-3 text-slate-400" size={16} />
              <input
                type="text"
                placeholder={t('अभंग किंवा संत शोधा...', 'Search title or lyrics...')}
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-2xl bg-[#131B2E] border border-white/10 text-white placeholder-slate-400 text-xs font-semibold focus:outline-none focus:border-amber-500"
              />
            </div>
          </div>

          {/* Saints Section */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-base sm:text-lg font-black text-white flex items-center gap-2">
                <Sparkles className="text-amber-400" size={20} />
                <span>{t('वारकरी संप्रदाय संत (Patron Saints)', 'Patron Saints of Maharashtra')}</span>
              </h2>
              {selectedSaintId && (
                <button
                  onClick={() => setSelectedSaintId(null)}
                  className="text-xs text-amber-400 font-bold hover:underline"
                >
                  {t('सर्व संत (Show All Saints)', 'Clear Saint Filter')}
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {saints.map(saint => (
                <div
                  key={saint.id}
                  onClick={() => setSelectedSaintId(selectedSaintId === saint.id ? null : saint.id)}
                  className={`p-4 rounded-3xl border cursor-pointer transition-all space-y-2 relative overflow-hidden ${
                    selectedSaintId === saint.id
                      ? 'bg-gradient-to-br from-orange-600/30 to-amber-500/20 border-amber-500 shadow-xl'
                      : 'bg-[#131B2E] border-white/10 hover:border-amber-500/40 hover:bg-[#1A243B]'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400 overflow-hidden font-black text-lg">
                      {saint.image_url ? (
                        <img src={saint.image_url} alt={saint.name} className="w-full h-full object-cover" />
                      ) : (
                        saint.name[0]
                      )}
                    </div>
                    <div>
                      <h4 className="font-black text-sm text-white">{saint.marathi_name || saint.name}</h4>
                      <p className="text-[11px] text-amber-400 font-bold">{saint.era}</p>
                    </div>
                  </div>
                  <p className="text-xs text-slate-300 line-clamp-2">{saint.biography}</p>
                  <div className="flex items-center justify-between text-[10px] font-bold text-slate-400 pt-1 border-t border-white/5">
                    <span>{saint.title || 'Varkari Saint'}</span>
                    <span className="text-orange-400">{saint.abhang_count || 0} Abhangs</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Abhang Songs List Grid */}
          <div className="space-y-3">
            <h2 className="text-base sm:text-lg font-black text-white flex items-center gap-2">
              <ListMusic className="text-amber-400" size={20} />
              <span>{t('संगीत व अभंग यादी (Devotional Songs)', 'Audio & Hymns Catalog')} ({filteredAbhangs.length})</span>
            </h2>

            {loading ? (
              <div className="p-12 text-center text-slate-400 font-bold flex items-center justify-center gap-2">
                <RefreshCw className="animate-spin text-amber-400" size={20} />
                <span>{t('अभंग लोड होत आहेत...', 'Loading Abhang songs...')}</span>
              </div>
            ) : filteredAbhangs.length === 0 ? (
              <div className="p-12 rounded-3xl bg-[#131B2E] border border-white/10 text-center space-y-2">
                <Music className="mx-auto text-slate-500" size={40} />
                <p className="text-sm font-bold text-slate-300">
                  {t('कोणतेही अभंग सापडले नाहीत.', 'No Abhangs found matching your filter.')}
                </p>
                <p className="text-xs text-slate-500">
                  {t('सामग्री व्यवस्थापनात नवीन अभंग किंवा ऑडिओ जोडा.', 'Use the S3 Upload Studio tab to add new audio content.')}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredAbhangs.map(abhang => {
                  const isCurrentTrack = currentAbhang?.id === abhang.id;
                  const isThisPlaying = isCurrentTrack && isPlaying;

                  return (
                    <div
                      key={abhang.id}
                      className={`p-4 rounded-2xl border transition-all flex items-center justify-between gap-4 ${
                        isCurrentTrack
                          ? 'bg-gradient-to-r from-orange-500/20 to-amber-500/10 border-amber-500 shadow-lg'
                          : 'bg-[#131B2E] border-white/10 hover:bg-[#1A243B]'
                      }`}
                    >
                      <div className="flex items-center gap-3.5 flex-1 min-w-0">
                        <button
                          onClick={() => handlePlayAbhang(abhang)}
                          className={`w-11 h-11 rounded-2xl flex items-center justify-center flex-shrink-0 transition-all ${
                            isThisPlaying
                              ? 'bg-orange-500 text-white shadow-lg scale-105'
                              : 'bg-amber-500/20 text-amber-400 hover:bg-amber-500 hover:text-slate-950'
                          }`}
                        >
                          {isThisPlaying ? <Pause size={20} /> : <Play size={20} className="ml-0.5" />}
                        </button>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="px-2 py-0.5 rounded bg-white/10 text-amber-300 font-extrabold text-[9px] uppercase">
                              {abhang.category}
                            </span>
                            {abhang.duration && (
                              <span className="text-[10px] text-slate-400 font-bold">{abhang.duration}</span>
                            )}
                          </div>
                          <h4 className="font-extrabold text-sm text-white truncate mt-0.5">
                            {abhang.marathi_title}
                          </h4>
                          <p className="text-xs text-slate-400 truncate">
                            {abhang.saint_marathi_name || abhang.title} • {abhang.artist || 'Traditional'}
                          </p>
                        </div>
                      </div>

                      <button
                        onClick={() => setLyricsModalAbhang(abhang)}
                        className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-slate-300 font-bold text-xs flex-shrink-0 transition-all"
                      >
                        {t('शब्द (Lyrics)', 'Lyrics')}
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

        </div>
      ) : (
        /* Manage Tab - Website Admin S3 Upload Studio */
        <div className="space-y-6">

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Upload & Create Form (Left 2 Columns) */}
            <div className="lg:col-span-2 p-6 rounded-3xl bg-[#131B2E] border border-amber-500/30 space-y-6 shadow-xl">
              <div className="flex justify-between items-center pb-4 border-b border-white/10">
                <div>
                  <h3 className="font-extrabold text-white text-lg flex items-center gap-2">
                    <CloudUpload className="text-amber-400" size={22} />
                    <span>{t('ऑडिओ फाइल AWS S3 वर अपलोड करा (Publish Song)', 'Upload Audio to AWS S3 & Publish')}</span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    {t('एमपी३/ऑडिओ फाइल थेट क्लाउड S3 मध्ये साठवा', 'Upload audio files directly to AWS S3 storage')}
                  </p>
                </div>
                <button
                  onClick={() => setShowSaintModal(true)}
                  className="px-3 py-2 rounded-xl bg-amber-500/20 border border-amber-500/40 hover:bg-amber-500/30 text-amber-300 font-bold text-xs flex items-center gap-1.5"
                >
                  <Plus size={14} />
                  <span>{t('नवीन संत जोडा', '+ Add Saint')}</span>
                </button>
              </div>

              <form onSubmit={handleCreateAbhang} className="space-y-4">
                
                {/* File Upload Zone */}
                <div className="p-6 rounded-2xl bg-[#0B0F19] border-2 border-dashed border-amber-500/40 text-center space-y-3 relative">
                  <CloudUpload className="mx-auto text-amber-400 animate-pulse" size={40} />
                  <div>
                    <p className="text-sm font-bold text-white">
                      {t('ऑडिओ फाइल येथे ड्रॅग करा किंवा निवडा', 'Upload Audio Track to AWS S3')}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      Supports MP3, WAV, M4A audio files (Max 50MB)
                    </p>
                  </div>

                  <input
                    type="file"
                    accept="audio/*"
                    onChange={e => handleFileUpload(e, false)}
                    className="absolute inset-0 opacity-0 cursor-pointer"
                    disabled={isUploading}
                  />

                  {isUploading && (
                    <p className="text-xs text-amber-400 font-bold animate-pulse">{uploadProgress}</p>
                  )}

                  {newAbhang.audio_url && (
                    <div className="p-3 rounded-xl bg-amber-500/20 border border-amber-500/40 text-left space-y-2">
                      <p className="text-xs text-amber-300 font-bold flex items-center gap-2 truncate">
                        <CheckCircle2 size={16} className="text-emerald-400 flex-shrink-0" />
                        <span className="truncate">S3 URL: {newAbhang.audio_url}</span>
                      </p>
                      <audio controls src={newAbhang.audio_url} className="w-full h-8" />
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-extrabold text-slate-300 mb-1">
                      {t('अभंग शीर्षक (Marathi Title) *', 'Marathi Title *')}
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="उदा. रूप सुंदर सावळा तो हा"
                      value={newAbhang.marathi_title}
                      onChange={e => setNewAbhang({ ...newAbhang, marathi_title: e.target.value })}
                      className="w-full px-4 py-2.5 rounded-xl bg-[#0B0F19] border border-white/10 text-white text-xs font-semibold focus:border-amber-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-extrabold text-slate-300 mb-1">
                      {t('इंग्रजी शीर्षक (English Title) *', 'English Title *')}
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Rupe Sunder Sawala"
                      value={newAbhang.title}
                      onChange={e => setNewAbhang({ ...newAbhang, title: e.target.value })}
                      className="w-full px-4 py-2.5 rounded-xl bg-[#0B0F19] border border-white/10 text-white text-xs font-semibold focus:border-amber-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-extrabold text-slate-300 mb-1">
                      {t('वारकरी संत (Select Saint)', 'Saint / Author')}
                    </label>
                    <select
                      value={newAbhang.saint}
                      onChange={e => setNewAbhang({ ...newAbhang, saint: e.target.value })}
                      className="w-full px-4 py-2.5 rounded-xl bg-[#0B0F19] border border-white/10 text-white text-xs font-semibold focus:border-amber-500 focus:outline-none"
                    >
                      <option value="">-- General / Traditional --</option>
                      {saints.map(s => (
                        <option key={s.id} value={s.id}>{s.marathi_name || s.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-extrabold text-slate-300 mb-1">
                      {t('वर्ग (Category)', 'Category')}
                    </label>
                    <select
                      value={newAbhang.category}
                      onChange={e => setNewAbhang({ ...newAbhang, category: e.target.value })}
                      className="w-full px-4 py-2.5 rounded-xl bg-[#0B0F19] border border-white/10 text-white text-xs font-semibold focus:border-amber-500 focus:outline-none"
                    >
                      {CATEGORIES.filter(c => c !== 'All').map(c => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-extrabold text-slate-300 mb-1">
                      {t('गायक (Singer / Artist)', 'Singer / Artist')}
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Lata Mangeshkar"
                      value={newAbhang.artist}
                      onChange={e => setNewAbhang({ ...newAbhang, artist: e.target.value })}
                      className="w-full px-4 py-2.5 rounded-xl bg-[#0B0F19] border border-white/10 text-white text-xs font-semibold focus:border-amber-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-extrabold text-slate-300 mb-1">
                    {t('अभंग शब्द (Marathi Lyrics)', 'Marathi Lyrics')}
                  </label>
                  <textarea
                    rows={4}
                    placeholder="येथे अभंगाचे शब्द लिहा..."
                    value={newAbhang.lyrics}
                    onChange={e => setNewAbhang({ ...newAbhang, lyrics: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#0B0F19] border border-white/10 text-white text-xs font-semibold focus:border-amber-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-extrabold text-slate-300 mb-1">
                    {t('इंग्रजी अर्थ (English Translation)', 'English Translation')}
                  </label>
                  <textarea
                    rows={2}
                    placeholder="Enter English meaning/translation..."
                    value={newAbhang.translation}
                    onChange={e => setNewAbhang({ ...newAbhang, translation: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#0B0F19] border border-white/10 text-white text-xs font-semibold focus:border-amber-500 focus:outline-none"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isUploading}
                  className="w-full py-3 rounded-2xl bg-gradient-to-r from-orange-600 to-amber-500 hover:from-orange-500 hover:to-amber-400 text-white font-extrabold text-sm shadow-xl flex items-center justify-center gap-2 transition-all"
                >
                  <Upload size={18} />
                  <span>{t('अभंग प्रकाशित करा (Publish Abhang)', 'Publish to App & Web')}</span>
                </button>

              </form>
            </div>

            {/* Existing Contents Management Table (Right 1 Column) */}
            <div className="p-6 rounded-3xl bg-[#131B2E] border border-white/10 space-y-4 shadow-xl">
              <h3 className="font-extrabold text-white text-base flex items-center gap-2">
                <Layers className="text-amber-400" size={20} />
                <span>{t('प्रसिद्ध गाणी (Published Tracks)', 'Published Audio Catalog')} ({abhangs.length})</span>
              </h3>

              <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
                {abhangs.map(a => (
                  <div key={a.id} className="p-3.5 rounded-2xl bg-[#0B0F19] border border-white/10 space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-extrabold text-[9px]">
                          {a.category}
                        </span>
                        <h4 className="font-bold text-xs text-white mt-1">{a.marathi_title}</h4>
                        <p className="text-[10px] text-slate-400">{a.saint_marathi_name || 'Traditional'}</p>
                      </div>
                      <button
                        onClick={() => handleDeleteAbhang(a.id)}
                        className="p-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-all"
                        title="Delete track"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                    {a.audio_url && (
                      <div className="pt-2 border-t border-white/5 flex items-center justify-between text-[10px]">
                        <span className="text-amber-400/80 truncate max-w-[180px]">S3: {a.audio_url}</span>
                        <button
                          onClick={() => handlePlayAbhang(a)}
                          className="text-amber-400 font-bold flex items-center gap-1 hover:underline"
                        >
                          <Play size={10} /> Test Play
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

          </div>

        </div>
      )}

      {/* Add Saint Modal */}
      {showSaintModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-lg p-6 rounded-3xl bg-[#131B2E] border border-amber-500/40 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-3 border-b border-white/10">
              <h3 className="font-black text-white text-base flex items-center gap-2">
                <User className="text-amber-400" size={20} />
                <span>{t('नवीन संत माहिती जोडा', 'Add New Saint Record')}</span>
              </h3>
              <button onClick={() => setShowSaintModal(false)} className="text-slate-400 hover:text-white">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateSaint} className="space-y-3">
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">Marathi Name *</label>
                <input
                  type="text"
                  required
                  placeholder="उदा. संत ज्ञानेश्वर महाराज"
                  value={newSaint.marathi_name}
                  onChange={e => setNewSaint({ ...newSaint, marathi_name: e.target.value })}
                  className="w-full px-4 py-2 rounded-xl bg-[#0B0F19] border border-white/10 text-white text-xs font-semibold"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">English Name *</label>
                <input
                  type="text"
                  required
                  placeholder="Sant Dnyaneshwar Maharaj"
                  value={newSaint.name}
                  onChange={e => setNewSaint({ ...newSaint, name: e.target.value })}
                  className="w-full px-4 py-2 rounded-xl bg-[#0B0F19] border border-white/10 text-white text-xs font-semibold"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Title</label>
                  <input
                    type="text"
                    placeholder="Mauli"
                    value={newSaint.title}
                    onChange={e => setNewSaint({ ...newSaint, title: e.target.value })}
                    className="w-full px-4 py-2 rounded-xl bg-[#0B0F19] border border-white/10 text-white text-xs font-semibold"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Era & Location</label>
                  <input
                    type="text"
                    placeholder="1275 – 1296 CE • Alandi"
                    value={newSaint.era}
                    onChange={e => setNewSaint({ ...newSaint, era: e.target.value })}
                    className="w-full px-4 py-2 rounded-xl bg-[#0B0F19] border border-white/10 text-white text-xs font-semibold"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">Biography / Info</label>
                <textarea
                  rows={3}
                  placeholder="Saint history..."
                  value={newSaint.biography}
                  onChange={e => setNewSaint({ ...newSaint, biography: e.target.value })}
                  className="w-full px-4 py-2 rounded-xl bg-[#0B0F19] border border-white/10 text-white text-xs font-semibold"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">Photo Upload (S3)</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={e => handleFileUpload(e, true)}
                  className="w-full text-xs text-slate-400"
                />
                {newSaint.image_url && <p className="text-[10px] text-amber-400 mt-1">Image S3: {newSaint.image_url}</p>}
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowSaintModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/10 text-slate-300 font-bold text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-orange-600 to-amber-500 text-white font-extrabold text-xs shadow-lg"
                >
                  Save Saint
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Lyrics Modal */}
      {lyricsModalAbhang && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-lg p-6 rounded-3xl bg-[#131B2E] border border-amber-500/40 space-y-4 shadow-2xl max-h-[85vh] overflow-y-auto">
            <div className="flex justify-between items-center pb-3 border-b border-white/10">
              <div>
                <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-extrabold text-[10px]">
                  {lyricsModalAbhang.category}
                </span>
                <h3 className="font-black text-white text-lg mt-0.5">{lyricsModalAbhang.marathi_title}</h3>
                <p className="text-xs text-amber-300">{lyricsModalAbhang.saint_marathi_name || lyricsModalAbhang.title}</p>
              </div>
              <button onClick={() => setLyricsModalAbhang(null)} className="text-slate-400 hover:text-white">
                <X size={22} />
              </button>
            </div>

            <div className="p-4 rounded-2xl bg-[#0B0F19] border border-white/10 space-y-3">
              <h4 className="text-xs font-black text-amber-400 uppercase tracking-wider">अभंग शब्द (Marathi Lyrics)</h4>
              <p className="text-sm font-semibold text-white leading-relaxed whitespace-pre-line">
                {lyricsModalAbhang.lyrics || 'शब्द उपलब्ध नाहीत.'}
              </p>
            </div>

            {lyricsModalAbhang.translation && (
              <div className="p-4 rounded-2xl bg-orange-500/10 border border-orange-500/20 space-y-2">
                <h4 className="text-xs font-black text-orange-300 uppercase tracking-wider">English Meaning & Translation</h4>
                <p className="text-xs text-slate-200 leading-relaxed">
                  {lyricsModalAbhang.translation}
                </p>
              </div>
            )}

            <div className="pt-2 flex justify-between items-center">
              <button
                onClick={() => {
                  handlePlayAbhang(lyricsModalAbhang);
                  setLyricsModalAbhang(null);
                }}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-orange-600 to-amber-500 text-white font-extrabold text-xs shadow-lg flex items-center gap-2"
              >
                <Play size={16} />
                <span>Play Audio Now</span>
              </button>
              <button
                onClick={() => setLyricsModalAbhang(null)}
                className="px-4 py-2 rounded-xl bg-white/10 text-slate-300 font-bold text-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
