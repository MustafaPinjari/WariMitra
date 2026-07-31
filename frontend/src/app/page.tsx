"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  AlertTriangle, Droplets, Utensils, Activity, Tent, Shield, HeartHandshake, 
  MapPin, Clock, ArrowRight, Sun, Sparkles, Navigation, Users, Search, Radio, CheckCircle2, ChevronRight, Phone, BookOpen
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';

export default function OverviewPage() {
  const { audienceRole, t, language } = useAccessibility();
  const [stats, setStats] = useState({
    totalPilgrims: 450000,
    activeSOS: 3,
    medicalCamps: 28,
    queueTimeMins: 45,
    waterPoints: 120,
    foodCamps: 85,
    volunteersOnGround: 1250,
  });

  const isPilgrimMode = audienceRole === 'PILGRIM' || audienceRole === 'VOLUNTEER';

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      
      {/* Top Banner: Warm Welcome & Mission Statement */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-orange-950/80 via-[#131B2E] to-slate-900 border border-orange-500/30 p-6 sm:p-8 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-64 h-64 bg-orange-600/20 rounded-full blur-3xl" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-orange-500/10 border border-orange-500/30 rounded-full text-orange-400 text-xs font-extrabold">
              <Sparkles size={14} />
              <span>{t('महाराष्ट्र शासन • आषाढी वारी डिजिटल साथी', 'Maharashtra Govt • Ashadhi Wari Digital Companion')}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-white tracking-tight">
              {isPilgrimMode 
                ? t('जय हरी विठ्ठल! वारीमित्र सेवा पोर्टल', 'Jai Hari Vitthal! WariMitra Service Portal')
                : t('वारीमित्र केंद्रीय नियंत्रण कक्ष', 'WariMitra Central Command Center')}
            </h1>
            <p className="text-slate-300 text-xs sm:text-sm max-w-2xl font-medium leading-relaxed">
              {t(
                'लाखो वारकऱ्यांच्या सुरक्षित, सुखकर आणि सुव्यवस्थित प्रवासासाठी एकमेव अधिकृत डिजिटल व्यासपीठ.',
                'The unified digital platform empowering millions of pilgrims, volunteers, medical teams, and government authorities.',
                'लाखों वारकरियों की सुरक्षित और सुखद यात्रा के लिए आधिकारिक डिजिटल मंच।'
              )}
            </p>
          </div>

          {/* Weather & Live Route Widget */}
          <div className="flex items-center gap-4 bg-white/5 border border-white/10 p-3.5 rounded-2xl backdrop-blur-md">
            <div className="w-12 h-12 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Sun size={26} className="animate-spin-slow" />
            </div>
            <div>
              <p className="text-xs text-slate-400 font-bold">{t('आजचा मुक्काम / तापमान', 'Today Stop & Weather')}</p>
              <p className="text-sm font-black text-white">वाखारी ➔ पंढरपूर • ३१°C</p>
              <p className="text-[11px] text-emerald-400 font-semibold flex items-center gap-1 mt-0.5">
                <CheckCircle2 size={12} />
                <span>{t('मार्ग मोकळा आहे (Route Clear)', 'Route Smooth')}</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* -------------------------------------------------------------------------- */}
      {/* AUDIENCE VIEW 1: PILGRIM / DEVOTEE ULTRA-ACCESSIBLE ACTION GRID            */}
      {/* -------------------------------------------------------------------------- */}
      {isPilgrimMode ? (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
              <Navigation className="text-orange-400" size={20} />
              <span>{t('वारकरी मुख्य सेवा (Quick Services for Pilgrims)', 'Primary Warkari Services')}</span>
            </h2>
            <span className="text-xs text-orange-400 font-bold bg-orange-500/10 px-3 py-1 rounded-full border border-orange-500/30">
              {t('मोठ्या बटणावर टॅप करा', 'Tap any large button')}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            {/* Water Locator */}
            <Link href="/crowd">
              <motion.div 
                whileHover={{ scale: 1.02 }}
                className="p-5 rounded-2xl bg-gradient-to-br from-blue-950/60 to-[#131B2E] border border-blue-500/30 hover:border-blue-400 transition-all shadow-xl cursor-pointer group"
              >
                <div className="w-12 h-12 rounded-xl bg-blue-500/20 border border-blue-500/40 flex items-center justify-center text-blue-400 mb-3 group-hover:scale-110 transition-transform">
                  <Droplets size={26} />
                </div>
                <h3 className="text-base font-black text-white group-hover:text-blue-300">
                  {t('पिण्याचे पाणी (Water)', 'Drinking Water')}
                </h3>
                <p className="text-xs text-slate-300 mt-1 font-medium">
                  {t('१२०+ मोफत पाणी वाटप केंद्रे शोधा', 'Locate 120+ free drinking water points')}
                </p>
                <div className="mt-3 flex items-center gap-1 text-xs font-bold text-blue-400">
                  <span>{t('नकाशा पहा', 'View Water Map')}</span>
                  <ArrowRight size={14} />
                </div>
              </motion.div>
            </Link>

            {/* Food Distribution */}
            <Link href="/ngo">
              <motion.div 
                whileHover={{ scale: 1.02 }}
                className="p-5 rounded-2xl bg-gradient-to-br from-pink-950/60 to-[#131B2E] border border-pink-500/30 hover:border-pink-400 transition-all shadow-xl cursor-pointer group"
              >
                <div className="w-12 h-12 rounded-xl bg-pink-500/20 border border-pink-500/40 flex items-center justify-center text-pink-400 mb-3 group-hover:scale-110 transition-transform">
                  <Utensils size={26} />
                </div>
                <h3 className="text-base font-black text-white group-hover:text-pink-300">
                  {t('मोफत अन्नछत्र (Food)', 'Free Food Camps')}
                </h3>
                <p className="text-xs text-slate-300 mt-1 font-medium">
                  {t('८५+ महाप्रसाद व नाश्ता केंद्रे', 'Locate 85+ food & tea distribution centers')}
                </p>
                <div className="mt-3 flex items-center gap-1 text-xs font-bold text-pink-400">
                  <span>{t('अन्नछत्र यादी', 'Locate Food')}</span>
                  <ArrowRight size={14} />
                </div>
              </motion.div>
            </Link>

            {/* Medical Camps & Ambulance */}
            <Link href="/medical">
              <motion.div 
                whileHover={{ scale: 1.02 }}
                className="p-5 rounded-2xl bg-gradient-to-br from-emerald-950/60 to-[#131B2E] border border-emerald-500/30 hover:border-emerald-400 transition-all shadow-xl cursor-pointer group"
              >
                <div className="w-12 h-12 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 mb-3 group-hover:scale-110 transition-transform">
                  <Activity size={26} />
                </div>
                <h3 className="text-base font-black text-white group-hover:text-emerald-300">
                  {t('वैद्यकीय केंद्र (Medical)', 'Medical Camps')}
                </h3>
                <p className="text-xs text-slate-300 mt-1 font-medium">
                  {t('२८+ मोफत आरोग्य शिबीर व रुग्णवाहिका', 'Find 28+ health camps & ambulances')}
                </p>
                <div className="mt-3 flex items-center gap-1 text-xs font-bold text-emerald-400">
                  <span>{t('आरोग्य मदत', 'Get Medical Help')}</span>
                  <ArrowRight size={14} />
                </div>
              </motion.div>
            </Link>

            {/* Temple Queue Status */}
            <Link href="/temple">
              <motion.div 
                whileHover={{ scale: 1.02 }}
                className="p-5 rounded-2xl bg-gradient-to-br from-purple-950/60 to-[#131B2E] border border-purple-500/30 hover:border-purple-400 transition-all shadow-xl cursor-pointer group"
              >
                <div className="w-12 h-12 rounded-xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-400 mb-3 group-hover:scale-110 transition-transform">
                  <Tent size={26} />
                </div>
                <h3 className="text-base font-black text-white group-hover:text-purple-300">
                  {t('दर्शन रांग (Darshan Queue)', 'Temple Darshan')}
                </h3>
                <p className="text-xs text-slate-300 mt-1 font-medium">
                  {t('श्री विठ्ठल मंदिर सध्याची वेळ: ४५ मि.', 'Current Pandharpur Darshan queue estimate')}
                </p>
                <div className="mt-3 flex items-center gap-1 text-xs font-bold text-purple-400">
                  <span>{t('रांग वेळ पहा', 'Check Queue Time')}</span>
                  <ArrowRight size={14} />
                </div>
              </motion.div>
            </Link>

            {/* Lost & Found */}
            <Link href="/lost-found">
              <motion.div 
                whileHover={{ scale: 1.02 }}
                className="p-5 rounded-2xl bg-gradient-to-br from-cyan-950/60 to-[#131B2E] border border-cyan-500/30 hover:border-cyan-400 transition-all shadow-xl cursor-pointer group"
              >
                <div className="w-12 h-12 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 mb-3 group-hover:scale-110 transition-transform">
                  <Search size={26} />
                </div>
                <h3 className="text-base font-black text-white group-hover:text-cyan-300">
                  {t('हरवलेले व्यक्ती व वस्तू', 'Lost & Found')}
                </h3>
                <p className="text-xs text-slate-300 mt-1 font-medium">
                  {t('नातेवाईक हरवले असल्यास फोटोसह नोंदवा', 'Report lost child/elderly with photo')}
                </p>
                <div className="mt-3 flex items-center gap-1 text-xs font-bold text-cyan-400">
                  <span>{t('शोध घ्या', 'Search & Report')}</span>
                  <ArrowRight size={14} />
                </div>
              </motion.div>
            </Link>

            {/* Vari Heritage */}
            <Link href="/heritage">
              <motion.div 
                whileHover={{ scale: 1.02 }}
                className="p-5 rounded-2xl bg-gradient-to-br from-amber-950/60 to-[#131B2E] border border-amber-500/30 hover:border-amber-400 transition-all shadow-xl cursor-pointer group"
              >
                <div className="w-12 h-12 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 mb-3 group-hover:scale-110 transition-transform">
                  <BookOpen size={26} />
                </div>
                <h3 className="text-base font-black text-white group-hover:text-amber-300">
                  {t('वारी वारसा व अभंग', 'Wari Heritage')}
                </h3>
                <p className="text-xs text-slate-300 mt-1 font-medium">
                  {t('पालखी मार्ग, अभंग गाथा व संत माहिती', 'Palkhi schedule & spiritual hymns')}
                </p>
                <div className="mt-3 flex items-center gap-1 text-xs font-bold text-amber-400">
                  <span>{t('माहिती वाचा', 'Explore Heritage')}</span>
                  <ArrowRight size={14} />
                </div>
              </motion.div>
            </Link>

            {/* Sanitation & Toilets */}
            <Link href="/sanitation">
              <motion.div 
                whileHover={{ scale: 1.02 }}
                className="p-5 rounded-2xl bg-gradient-to-br from-teal-950/60 to-[#131B2E] border border-teal-500/30 hover:border-teal-400 transition-all shadow-xl cursor-pointer group"
              >
                <div className="w-12 h-12 rounded-xl bg-teal-500/20 border border-teal-500/40 flex items-center justify-center text-teal-400 mb-3 group-hover:scale-110 transition-transform">
                  <Activity size={26} />
                </div>
                <h3 className="text-base font-black text-white group-hover:text-teal-300">
                  {t('स्वच्छतागृह (Toilets)', 'Sanitation & Toilets')}
                </h3>
                <p className="text-xs text-slate-300 mt-1 font-medium">
                  {t('जवळची मोबाईल स्वच्छतागृहे व स्वच्छता तक्रार', 'Find mobile toilets & report cleanup')}
                </p>
                <div className="mt-3 flex items-center gap-1 text-xs font-bold text-teal-400">
                  <span>{t('स्वच्छतागृह शोधा', 'Locate Toilets')}</span>
                  <ArrowRight size={14} />
                </div>
              </motion.div>
            </Link>

            {/* Emergency SOS High Priority */}
            <Link href="/sos">
              <motion.div 
                whileHover={{ scale: 1.02 }}
                className="p-5 rounded-2xl bg-gradient-to-br from-red-950/80 to-[#131B2E] border-2 border-red-500/60 hover:border-red-400 transition-all shadow-2xl cursor-pointer group relative overflow-hidden"
              >
                <div className="w-12 h-12 rounded-xl bg-red-600/30 border border-red-500/60 flex items-center justify-center text-red-400 mb-3 group-hover:scale-110 transition-transform">
                  <AlertTriangle size={26} className="animate-pulse" />
                </div>
                <h3 className="text-base font-black text-white group-hover:text-red-300">
                  {t('आणीबाणी SOS (Emergency)', 'Emergency SOS')}
                </h3>
                <p className="text-xs text-slate-300 mt-1 font-medium">
                  {t('एक टॅप करा! स्वयंसेवक व रुग्णवाहिका येईल', 'One tap alerts volunteers & police')}
                </p>
                <div className="mt-3 flex items-center gap-1 text-xs font-extrabold text-red-400">
                  <span>{t('तात्काळ मदत मागा', 'Trigger SOS Now')}</span>
                  <ArrowRight size={14} />
                </div>
              </motion.div>
            </Link>

          </div>
        </div>
      ) : (
        
        /* -------------------------------------------------------------------------- */
        /* AUDIENCE VIEW 2: GOVERNMENT / OPERATIONAL COMMAND DASHBOARD                */
        /* -------------------------------------------------------------------------- */
        <div className="space-y-6">
          
          {/* Executive Stats Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-[#131B2E] border border-orange-500/30 shadow-lg">
              <div className="flex items-center justify-between text-slate-400 text-xs font-bold mb-1">
                <span>{t('एकूण वारकरी संख्या', 'Total Pilgrims')}</span>
                <Users size={16} className="text-orange-400" />
              </div>
              <p className="text-2xl font-black text-white">{stats.totalPilgrims.toLocaleString()}</p>
              <p className="text-[11px] text-emerald-400 font-semibold mt-1">↑ +१२,००० आज नवीन प्रविष्ट</p>
            </div>

            <div className="p-4 rounded-2xl bg-[#131B2E] border border-red-500/30 shadow-lg">
              <div className="flex items-center justify-between text-slate-400 text-xs font-bold mb-1">
                <span>{t('सक्रिय आणीबाणी SOS', 'Active SOS Calls')}</span>
                <AlertTriangle size={16} className="text-red-400" />
              </div>
              <p className="text-2xl font-black text-red-400">{stats.activeSOS}</p>
              <p className="text-[11px] text-orange-300 font-semibold mt-1">३ पथके घटनास्थळी रवाना</p>
            </div>

            <div className="p-4 rounded-2xl bg-[#131B2E] border border-emerald-500/30 shadow-lg">
              <div className="flex items-center justify-between text-slate-400 text-xs font-bold mb-1">
                <span>{t('वैद्यकीय शिबीरे', 'Health Camps Active')}</span>
                <Activity size={16} className="text-emerald-400" />
              </div>
              <p className="text-2xl font-black text-white">{stats.medicalCamps}</p>
              <p className="text-[11px] text-emerald-400 font-semibold mt-1">१००% औषध साठा उपलब्ध</p>
            </div>

            <div className="p-4 rounded-2xl bg-[#131B2E] border border-purple-500/30 shadow-lg">
              <div className="flex items-center justify-between text-slate-400 text-xs font-bold mb-1">
                <span>{t('दर्शन रांग वेळ', 'Darshan Wait Time')}</span>
                <Clock size={16} className="text-purple-400" />
              </div>
              <p className="text-2xl font-black text-purple-300">{stats.queueTimeMins} मि.</p>
              <p className="text-[11px] text-slate-400 font-semibold mt-1">पंढरपूर मुख्य मंदिर परिसर</p>
            </div>
          </div>

          {/* Middle Grid: GIS Live Map Preview & AI Predictions */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* GIS Live Map Placeholder */}
            <div className="lg:col-span-2 p-5 rounded-3xl bg-[#131B2E] border border-white/10 shadow-2xl flex flex-col justify-between space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-extrabold text-base text-white flex items-center gap-2">
                    <MapPin className="text-orange-400" size={18} />
                    <span>{t('थेट वारी मार्ग व गर्दीची स्थिती (Live GIS Stream)', 'Live GIS Route & Density')}</span>
                  </h3>
                  <p className="text-xs text-slate-400 font-medium">पुणे ➔ सासवड ➔ लोणंद ➔ पंढरपूर मार्ग</p>
                </div>
                <Link href="/crowd" className="px-3 py-1.5 bg-orange-500/10 border border-orange-500/30 text-orange-300 hover:text-white rounded-xl text-xs font-bold transition-colors">
                  {t('पूर्ण नकाशा उघडा', 'Open Full Map')}
                </Link>
              </div>

              {/* Simulated Map Visual */}
              <div className="h-64 rounded-2xl bg-slate-900 border border-white/10 relative overflow-hidden flex items-center justify-center">
                <div className="absolute inset-0 opacity-30 bg-[radial-gradient(#e85d04_1px,transparent_1px)] [background-size:16px_16px]" />
                <div className="relative z-10 text-center space-y-2 p-4">
                  <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/20 border border-emerald-500/40 rounded-full text-emerald-400 text-xs font-bold">
                    <Radio size={14} className="animate-pulse" />
                    <span>थेट GPS ट्रॅकिंग सुरू (Live GPS Syncing)</span>
                  </div>
                  <p className="text-xs text-slate-300 font-semibold max-w-sm">
                    १,२५०+ नोंदणीकृत स्वयंसेवक आणि १५०+ रुग्णवाहिका नकाशावर थेट दृश्यमान आहेत.
                  </p>
                </div>
              </div>
            </div>

            {/* AI Predictions & Alerts Widget */}
            <div className="p-5 rounded-3xl bg-[#131B2E] border border-orange-500/30 shadow-2xl space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-white/10">
                <Sparkles className="text-orange-400" size={20} />
                <h3 className="font-extrabold text-base text-white">
                  {t('AI भाकीत व शिफारसी', 'AI Predictions & Action Items')}
                </h3>
              </div>

              <div className="space-y-3">
                <div className="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-xs space-y-1">
                  <p className="font-bold text-amber-300">⚠️ गर्दीचा दाब इशारा (Crowd Surge Risk)</p>
                  <p className="text-slate-300">पुढील ४० मिनिटांत वाखारी चौकात गर्दी १५% ने वाढण्याची शक्यता आहे.</p>
                  <p className="text-[11px] text-orange-400 font-semibold">शिफारस: अतिरिक्त स्वयंसेवक तुकडी क्र. ४ पाठवा.</p>
                </div>

                <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/30 text-xs space-y-1">
                  <p className="font-bold text-blue-300">💧 पाणी साठा इशारा (Water Demand)</p>
                  <p className="text-slate-300">भंडारा डोंगर परिसरात पाणी साठा २५% खाली आला आहे.</p>
                  <p className="text-[11px] text-blue-400 font-semibold">शिफारस: २ नवीन टँकर तत्काळ रवाना करा.</p>
                </div>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* Persistent Emergency Hotline Banner */}
      <div className="p-4 rounded-2xl bg-gradient-to-r from-red-950/60 via-[#131B2E] to-slate-900 border border-red-500/30 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-red-600/20 border border-red-500/40 flex items-center justify-center text-red-400">
            <Phone size={20} />
          </div>
          <div>
            <p className="text-xs font-extrabold text-white">
              {t('२४x७ शासकीय हेल्पलाइन क्र.', '24x7 Government Helpline Number')}
            </p>
            <p className="text-sm font-black text-red-400">१०८ (वैद्यकीय) • १०० (पोलीस) • १८००-२३३-४५५५ (वारी मदत)</p>
          </div>
        </div>
        <Link href="/sos" className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-extrabold text-xs rounded-xl transition-colors shadow-lg">
          {t('आणीबाणी कक्ष उघडा', 'Open Emergency Hub')}
        </Link>
      </div>

    </div>
  );
}
