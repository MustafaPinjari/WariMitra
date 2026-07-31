"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Bell, Search, UserCircle, LogOut, ChevronDown, ShieldCheck, Flag, Mic, AlertTriangle, Globe, Type } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAccessibility, AudienceRole, Language } from '@/components/providers/AccessibilityProvider';
import VoiceAssistantModal from '@/components/common/VoiceAssistantModal';

export default function Topbar() {
  const router = useRouter();
  const { language, setLanguage, fontSize, setFontSize, audienceRole, setAudienceRole, t } = useAccessibility();
  
  const [user, setUser] = useState<{ username: string; role: string; title: string } | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);
  const [langDropdownOpen, setLangDropdownOpen] = useState(false);
  const [voiceModalOpen, setVoiceModalOpen] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('warimitra_user');
    if (saved) {
      try {
        setUser(JSON.parse(saved));
      } catch (e) {
        setUser(null);
      }
    } else {
      setUser({
        username: 'warkari_devotee',
        role: audienceRole,
        title: 'Pandharpur Wari Participant',
      });
    }
  }, [audienceRole]);

  const handleLogout = () => {
    localStorage.removeItem('warimitra_user');
    localStorage.removeItem('warimitra_token');
    setUser(null);
    setDropdownOpen(false);
    router.push('/login');
  };

  const roleOptions: { key: AudienceRole; label: string; marathi: string; icon: string }[] = [
    { key: 'PILGRIM', label: 'Pilgrim / Devotee', marathi: '🚩 वारकरी भक्त', icon: '🚩' },
    { key: 'VOLUNTEER', label: 'Ground Volunteer', marathi: '🤝 स्वयंसेवक', icon: '🤝' },
    { key: 'MEDICAL', label: 'Medical Operations', marathi: '🚑 वैद्यकीय पथक', icon: '🚑' },
    { key: 'POLICE', label: 'Police & Security', marathi: '🚓 पोलीस बंदोबस्त', icon: '<ctrl42>' },
    { key: 'NGO', label: 'NGO Relief Camps', marathi: '🍲 अन्न व निवारा', icon: '🍲' },
    { key: 'TEMPLE', label: 'Temple Management', marathi: '🛕 दर्शन व्यवस्थापन', icon: '🛕' },
    { key: 'GOVERNMENT', label: 'Government Command', marathi: '🏛️ मुख्य शासन नियंत्रण', icon: '🏛️' },
  ];

  const activeRoleObj = roleOptions.find((r) => r.key === audienceRole) || roleOptions[0];

  return (
    <>
      <header className="h-16 bg-[#0B0F19]/95 backdrop-blur-2xl border-b border-orange-500/20 flex items-center justify-between px-3 sm:px-6 sticky top-0 z-40 w-full shadow-xl">
        
        {/* Left: Dynamic Search */}
        <div className="flex items-center gap-3 flex-1 max-w-xs sm:max-w-md">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-orange-400" size={15} />
            <input 
              type="text" 
              placeholder={t('शोधा... पाणी, अन्न, औषध, मंदिर रांग...', 'Search water, food, medical, queue...', 'खोजें... पानी, भोजन, चिकित्सा...')}
              className="w-full pl-9 pr-3 py-1.5 bg-[#131B2E] border border-white/15 text-white placeholder-slate-400 text-xs rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all"
            />
          </div>
        </div>

        {/* Center: Target Audience Role Selector Pill */}
        <div className="relative hidden md:block">
          <button
            onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
            className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-orange-600/20 to-amber-500/20 border border-orange-500/40 rounded-full hover:border-orange-400 transition-all select-none"
          >
            <span className="text-sm">{activeRoleObj.icon}</span>
            <span className="text-xs font-extrabold text-orange-300">
              {language === 'mr' ? activeRoleObj.marathi : activeRoleObj.label}
            </span>
            <ChevronDown size={13} className={`text-orange-400 transition-transform duration-200 ${roleDropdownOpen ? 'rotate-180' : ''}`} />
          </button>

          <AnimatePresence>
            {roleDropdownOpen && (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.95 }}
                className="absolute left-1/2 -translate-x-1/2 mt-2 w-64 bg-[#0F1420] border border-orange-500/40 p-2 rounded-2xl shadow-2xl z-50 space-y-1"
              >
                <p className="px-3 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  {t('भूमिका निवडा (Target Role):', 'Select Target Role:', 'भूमिका चुनें:')}
                </p>
                {roleOptions.map((opt) => (
                  <button
                    key={opt.key}
                    onClick={() => {
                      setAudienceRole(opt.key);
                      setRoleDropdownOpen(false);
                    }}
                    className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-bold text-left transition-colors ${
                      audienceRole === opt.key
                        ? 'bg-orange-500/20 text-orange-300 border border-orange-500/40'
                        : 'text-slate-300 hover:bg-white/5 hover:text-white'
                    }`}
                  >
                    <span>{opt.icon}</span>
                    <span>{language === 'mr' ? opt.marathi : opt.label}</span>
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        
        {/* Right: Accessibility Controls, Voice, Emergency SOS, Profile */}
        <div className="flex items-center gap-2 sm:gap-3">
          
          {/* Language Switcher */}
          <div className="relative">
            <button
              onClick={() => setLangDropdownOpen(!langDropdownOpen)}
              className="flex items-center gap-1.5 px-2.5 py-1.5 bg-white/5 border border-white/10 hover:bg-white/10 rounded-xl text-xs font-bold text-slate-200 transition-colors"
            >
              <Globe size={14} className="text-orange-400" />
              <span className="uppercase">{language}</span>
            </button>

            <AnimatePresence>
              {langDropdownOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 8 }}
                  className="absolute right-0 mt-2 w-32 bg-[#0F1420] border border-white/15 p-1.5 rounded-xl shadow-2xl z-50 space-y-1"
                >
                  <button
                    onClick={() => { setLanguage('mr'); setLangDropdownOpen(false); }}
                    className={`w-full text-left px-3 py-1.5 text-xs font-bold rounded-lg ${language === 'mr' ? 'bg-orange-500/20 text-orange-300' : 'text-slate-300 hover:bg-white/5'}`}
                  >
                    मराठी (Marathi)
                  </button>
                  <button
                    onClick={() => { setLanguage('hi'); setLangDropdownOpen(false); }}
                    className={`w-full text-left px-3 py-1.5 text-xs font-bold rounded-lg ${language === 'hi' ? 'bg-orange-500/20 text-orange-300' : 'text-slate-300 hover:bg-white/5'}`}
                  >
                    हिंदी (Hindi)
                  </button>
                  <button
                    onClick={() => { setLanguage('en'); setLangDropdownOpen(false); }}
                    className={`w-full text-left px-3 py-1.5 text-xs font-bold rounded-lg ${language === 'en' ? 'bg-orange-500/20 text-orange-300' : 'text-slate-300 hover:bg-white/5'}`}
                  >
                    English
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Font Size Toggle for Elderly Users */}
          <button
            onClick={() => setFontSize(fontSize === 'normal' ? 'large' : 'normal')}
            title="Toggle Senior Citizen Large Text"
            className={`p-2 rounded-xl border text-xs font-extrabold flex items-center gap-1 transition-all ${
              fontSize === 'large'
                ? 'bg-amber-500/20 border-amber-500/50 text-amber-300'
                : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
            }`}
          >
            <Type size={14} />
            <span className="hidden sm:inline">Aa+</span>
          </button>

          {/* Voice Assistant Button */}
          <button
            onClick={() => setVoiceModalOpen(true)}
            className="p-2 bg-gradient-to-tr from-amber-500/20 to-orange-500/20 border border-orange-500/40 text-orange-300 hover:text-white rounded-xl transition-all flex items-center gap-1.5 text-xs font-bold"
          >
            <Mic size={16} className="text-orange-400 animate-pulse" />
            <span className="hidden lg:inline">{t('आवाज सहाय्यक', 'Voice Assist', 'आवाज सहायक')}</span>
          </button>

          {/* Direct 1-Tap SOS Emergency Button */}
          <button
            onClick={() => router.push('/sos')}
            className="px-3 py-1.5 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-red-600/30 flex items-center gap-1.5 transition-all"
          >
            <AlertTriangle size={15} className="animate-bounce" />
            <span>SOS</span>
          </button>

          {/* User Profile Dropdown */}
          <div className="relative border-l border-white/10 pl-2">
            <div 
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-2 cursor-pointer select-none"
            >
              <div className="w-8 h-8 rounded-xl bg-orange-500/20 border border-orange-500/40 flex items-center justify-center text-orange-300 font-extrabold text-xs">
                {activeRoleObj.icon}
              </div>
            </div>

            <AnimatePresence>
              {dropdownOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 8, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 8, scale: 0.95 }}
                  className="absolute right-0 mt-3 w-56 bg-[#0F1420] border border-orange-500/30 p-2.5 rounded-2xl shadow-2xl z-50 space-y-1.5"
                >
                  <div className="p-2.5 bg-orange-500/10 rounded-xl border border-orange-500/20">
                    <p className="text-xs font-extrabold text-white flex items-center gap-1.5">
                      <ShieldCheck size={14} className="text-emerald-400" />
                      {user?.username || 'warkari_user'}
                    </p>
                    <p className="text-[10px] text-orange-300 mt-0.5">{activeRoleObj.marathi}</p>
                  </div>

                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-bold text-red-400 hover:bg-red-500/10 rounded-xl transition-colors text-left"
                  >
                    <LogOut size={15} />
                    <span>{t('लॉग आउट करा', 'Log Out', 'लॉग आउट')}</span>
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </header>

      {/* Voice Assistant Modal */}
      <VoiceAssistantModal isOpen={voiceModalOpen} onClose={() => setVoiceModalOpen(false)} />
    </>
  );
}
