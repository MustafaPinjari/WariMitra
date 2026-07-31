"use client";

import React, { useState } from 'react';
import { Mic, MicOff, X, Volume2, Sparkles, Navigation, AlertTriangle, Droplets, Utensils, Activity, Tent } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';
import { useRouter } from 'next/navigation';

export default function VoiceAssistantModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const { t, language } = useAccessibility();
  const router = useRouter();
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState<string | null>(null);

  const quickCommands = [
    { label: t('जवळचे पाणी', 'Nearest Water', 'निकटतम पानी'), icon: Droplets, href: '/crowd', reply: t('जवळचे पाणी केंद्र ३५० मीटर अंतरावर आहे.', 'Nearest water point is 350m ahead on the left.') },
    { label: t('वैद्यकीय मदत', 'Medical Help', 'चिकित्सा सहायता'), icon: Activity, href: '/medical', reply: t('जवळचे वैद्यकीय शिबीर ५०० मीटर वर रुग्णवाहिकेसह उपलब्ध आहे.', 'Nearest medical camp is 500m ahead with ambulance.') },
    { label: t('दर्शन रांग वेळ', 'Temple Queue', 'दर्शन कतार समय'), icon: Tent, href: '/temple', reply: t('पंढरपूर मंदिर सध्याची दर्शन वेळ अंदाजे ४५ मिनिटे आहे.', 'Current Pandharpur Darshan queue estimate is 45 minutes.') },
    { label: t('आणीबाणी SOS', 'Emergency SOS', 'आपातकालीन SOS'), icon: AlertTriangle, href: '/sos', reply: t('आणीबाणी टीम आणि स्वयंसेवक तात्काळ सतर्क केले जात आहेत.', 'Emergency team and nearby volunteers are being alerted.') },
  ];

  const toggleListening = () => {
    if (isListening) {
      setIsListening(false);
    } else {
      setIsListening(true);
      setTranscript(t('ऐकत आहे... कृपया बोला...', 'Listening... Speak now...', 'सुन रहा हूँ... बोलिए...'));
      setResponse(null);

      // Simulate Speech Recognition AI Processing
      setTimeout(() => {
        setIsListening(false);
        setTranscript(t('"जवळचे पाणी कुठे आहे?"', '"Where is the nearest water point?"', '"पास में पानी कहाँ है?"'));
        setResponse(t('३५० मीटर समोर डाव्या बाजूला मोफत पाणी वाटप केंद्र आहे.', 'Free drinking water point is 350 meters ahead on the left.', '350 मीटर आगे बाईं ओर पीने का पानी उपलब्ध है।'));
      }, 3000);
    }
  };

  const handleCommandClick = (cmd: typeof quickCommands[0]) => {
    setTranscript(`"${cmd.label}"`);
    setResponse(cmd.reply);
    setTimeout(() => {
      onClose();
      router.push(cmd.href);
    }, 2000);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-md"
            onClick={onClose}
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="relative w-full max-w-lg bg-[#0F172A] border-2 border-orange-500/40 rounded-3xl p-6 shadow-2xl z-50 text-white overflow-hidden"
          >
            {/* Bhagwa Glow background */}
            <div className="absolute -top-24 -right-24 w-48 h-48 bg-orange-600/30 rounded-full blur-3xl" />
            <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-amber-500/20 rounded-full blur-3xl" />

            <div className="flex items-center justify-between pb-4 border-b border-white/10">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-orange-500/20 border border-orange-500/40 flex items-center justify-center text-orange-400">
                  <Sparkles size={20} />
                </div>
                <div>
                  <h3 className="font-extrabold text-base text-white">
                    {t('वारीमित्र आवाज सहाय्यक', 'WariMitra Voice Assistant', 'वारीमित्र आवाज सहायक')}
                  </h3>
                  <p className="text-[11px] text-orange-300 font-medium">
                    {t('बोलून माहिती मिळवा किंवा मदत मागा', 'Speak to ask questions or get help', 'बोलकर जानकारी प्राप्त करें')}
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-slate-300 transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Mic Animation Section */}
            <div className="my-8 flex flex-col items-center justify-center text-center">
              <button
                onClick={toggleListening}
                className={`relative w-24 h-24 rounded-full flex items-center justify-center transition-all ${
                  isListening
                    ? 'bg-gradient-to-tr from-red-600 to-orange-500 shadow-[0_0_40px_rgba(239,68,68,0.7)] scale-110'
                    : 'bg-gradient-to-tr from-orange-600 to-amber-500 shadow-xl shadow-orange-500/30 hover:scale-105'
                }`}
              >
                {isListening && (
                  <span className="absolute inset-0 rounded-full bg-orange-500/40 animate-ping" />
                )}
                {isListening ? <Mic size={40} className="text-white animate-pulse" /> : <Mic size={40} className="text-white" />}
              </button>

              <p className="mt-4 text-xs font-bold text-slate-300">
                {isListening ? t('माईक सुरू आहे...', 'Microphone Active...', 'माइक सक्रिय है...') : t('माईकवर टॅप करून बोला', 'Tap Mic to Start Speaking', 'माइक पर टैप करके बोलें')}
              </p>
            </div>

            {/* Transcript & Response Area */}
            <AnimatePresence>
              {transcript && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-6 p-4 rounded-2xl bg-white/5 border border-white/10 text-center"
                >
                  <p className="text-xs font-semibold text-orange-300 italic mb-2">{transcript}</p>
                  {response && (
                    <div className="flex items-start gap-2.5 p-3 rounded-xl bg-orange-500/20 border border-orange-500/30 text-left">
                      <Volume2 size={18} className="text-orange-400 flex-shrink-0 mt-0.5" />
                      <p className="text-xs font-bold text-white leading-relaxed">{response}</p>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Quick Command Suggestions */}
            <div>
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2.5">
                {t('त्वरित आवाज आज्ञा (Quick Commands):', 'Quick Voice Commands:', 'त्वरित कमांड्स:')}
              </p>
              <div className="grid grid-cols-2 gap-2">
                {quickCommands.map((cmd, i) => {
                  const Icon = cmd.icon;
                  return (
                    <button
                      key={i}
                      onClick={() => handleCommandClick(cmd)}
                      className="flex items-center gap-2.5 p-3 rounded-xl bg-white/5 hover:bg-orange-500/20 border border-white/10 hover:border-orange-500/40 text-left transition-all group"
                    >
                      <Icon size={16} className="text-orange-400 group-hover:scale-110 transition-transform" />
                      <span className="text-xs font-bold text-slate-200 group-hover:text-white">{cmd.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
