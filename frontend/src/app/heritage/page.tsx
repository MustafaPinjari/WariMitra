"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Play, Pause, Sparkles, Volume2, Flag, Compass, Music, CheckCircle2 } from 'lucide-react';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';

const SAINTS = [
  {
    name: 'Sant Dnyaneshwar Maharaj',
    marathi: 'संत ज्ञानेश्वर महाराज (माउली)',
    location: 'आळंदी ➔ पंढरपूर मार्ग',
    desc: 'वारकरी संप्रदायाचे दैवत, "ज्ञानेश्वरी" व "पसायदान" चे रचनाकार.',
    abhang: 'रूप सुंदर सावळा तो हा विठ्ठल बरवा। तो हा विठ्ठल बरवा॥',
  },
  {
    name: 'Sant Tukaram Maharaj',
    marathi: 'संत तुकाराम महाराज (जगद्गुरु)',
    location: 'देहू ➔ पंढरपूर मार्ग',
    desc: 'अभंग गाथेचे प्रणेते व देहू गावाची वारकरी परंपरा.',
    abhang: 'आनंदाचे डोही आनंद तरंग। आनंदचि अंग आपुलिया॥',
  },
];

export default function HeritagePage() {
  const { t } = useAccessibility();
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeSaint, setActiveSaint] = useState(SAINTS[0]);

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 rounded-3xl bg-[#131B2E] border border-amber-500/40 shadow-2xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400">
            <BookOpen size={28} />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-white">
              {t('पालखी सोहळा वारसा व अभंग गाथा (Wari Heritage)', 'Vari Heritage & Spiritual Hymns')}
            </h1>
            <p className="text-xs text-slate-300 font-medium">
              {t('संत ज्ञानेश्वर व संत तुकाराम महाराज पालखी इतिहास व अभंग', 'Historical Palkhi itinerary & saint audio guide')}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={() => setIsPlaying(!isPlaying)}
            className="px-4 py-2.5 bg-gradient-to-r from-orange-600 to-amber-500 hover:from-orange-500 hover:to-amber-400 text-white font-extrabold text-xs rounded-xl shadow-lg flex items-center gap-2 transition-all"
          >
            {isPlaying ? <Pause size={16} /> : <Play size={16} />}
            <span>{isPlaying ? t('अभंग थांबवा', 'Pause Audio') : t('पसायदान व अभंग ऐका', 'Play Abhang Audio')}</span>
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Audio Player & Active Saint Card */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-amber-500/30 space-y-4 shadow-xl">
          <div className="flex justify-between items-center pb-3 border-b border-white/10">
            <h3 className="font-extrabold text-white text-base flex items-center gap-2">
              <Volume2 className="text-amber-400" size={20} />
              <span>{t('अभंग गाथा (Abhang Audio)', 'Abhang Audio Player')}</span>
            </h3>
            <span className="px-2.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-extrabold text-[10px]">
              AUDIO ACTIVE
            </span>
          </div>

          <div className="p-4 rounded-2xl bg-orange-500/10 border border-orange-500/30 space-y-3">
            <p className="text-xs text-orange-300 font-bold">{activeSaint.marathi}</p>
            <p className="text-sm font-black text-white">{activeSaint.abhang}</p>
            <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
              <div className={`bg-orange-500 h-full ${isPlaying ? 'w-[60%] animate-pulse' : 'w-0'}`} />
            </div>
          </div>
        </div>

        {/* Saint List */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-white/10 space-y-4 shadow-xl">
          <h3 className="font-extrabold text-white text-base flex items-center gap-2">
            <Sparkles className="text-amber-400" size={20} />
            <span>{t('वारकरी संप्रदाय संत (Patron Saints)', 'Patron Saints')}</span>
          </h3>

          <div className="space-y-3">
            {SAINTS.map(saint => (
              <div
                key={saint.name}
                onClick={() => setActiveSaint(saint)}
                className={`p-4 rounded-2xl border cursor-pointer transition-all space-y-1 ${
                  activeSaint.name === saint.name 
                    ? 'bg-orange-500/20 border-orange-500/50 text-white shadow-lg' 
                    : 'bg-[#0B0F19] border-white/10 text-slate-300 hover:bg-white/10'
                }`}
              >
                <p className="font-black text-sm text-white">{saint.marathi}</p>
                <p className="text-xs text-orange-300 font-bold">{saint.location}</p>
                <p className="text-xs text-slate-300">{saint.desc}</p>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}
