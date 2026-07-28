"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Play, Pause, Music, Compass, Sparkles, Flag, Volume2 } from 'lucide-react';
import GoogleMapContainer from '@/components/maps/GoogleMapContainer';

const SAINTS = [
  {
    name: 'Sant Dnyaneshwar Maharaj',
    marathi: 'संत ज्ञानेश्वर महाराज (माउली)',
    era: '1275 – 1296 CE • Alandi',
    desc: 'Patron saint of the Wari pilgrimage, author of Dnyaneshwari and Pasayadan.',
    abhang: 'रूप सुंदर सावळा तो हा विठ्ठल बरवा।',
  },
  {
    name: 'Sant Tukaram Maharaj',
    marathi: 'संत तुकाराम महाराज (जगद्गुरु)',
    era: '1598 – 1650 CE • Dehu',
    desc: 'Greatest Varkari poet saint whose Abhangas resonate across Maharashtra.',
    abhang: 'आनंदाचे डोही आनंद तरंग। आनंदचि अंग आपुलिया।',
  },
];

export default function HeritagePage() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeSaint, setActiveSaint] = useState(SAINTS[0]);

  return (
    <div className="relative w-full h-[calc(100vh-4rem)] overflow-hidden bg-[#05080F]">
      {/* INTERACTIVE MAP BACKDROP */}
      <GoogleMapContainer activeRole="Vari Heritage & Traditions Guide" />

      {/* TOP HEADER OVERLAY */}
      <div className="absolute top-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-4 pointer-events-none">
        <div className="pointer-events-auto bg-[#0F1420]/90 backdrop-blur-2xl border border-amber-500/40 px-4 py-2.5 rounded-2xl shadow-2xl flex items-center gap-3.5 max-w-full">
          <div className="p-2 bg-amber-500/20 text-amber-400 rounded-xl">
            <BookOpen size={20} />
          </div>
          <div>
            <p className="text-white font-extrabold text-xs tracking-tight flex items-center gap-2">
              <span>वारी परंपरा व अभंग दालन (VARI HERITAGE & ABHANGS)</span>
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            </p>
            <p className="text-slate-400 text-[10px]">Sant Dnyaneshwar & Tukaram Palkhi History • Audio Narration</p>
          </div>
        </div>

        <div className="pointer-events-auto">
          <button 
            onClick={() => setIsPlaying(!isPlaying)}
            className="px-4 py-2.5 bg-gradient-to-r from-orange-600 to-amber-500 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-orange-500/30 transition-all flex items-center gap-2 active:scale-95"
          >
            {isPlaying ? <Pause size={15} /> : <Play size={15} />}
            <span>{isPlaying ? 'Pause Audio Guide' : 'Play Mauli Abhang Narration'}</span>
          </button>
        </div>
      </div>

      {/* RIGHT SIDE DRAWER: Abhang Library & Saints */}
      <div className="absolute top-20 right-4 bottom-6 z-20 w-80 sm:w-96 bg-[#0B0F19]/95 backdrop-blur-2xl border border-amber-500/30 p-4 rounded-3xl shadow-2xl flex flex-col space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div className="flex items-center gap-2">
            <Sparkles size={16} className="text-amber-400" />
            <div>
              <p className="text-white font-extrabold text-xs">Abhang Library & Saint Timelines</p>
              <p className="text-slate-400 text-[10px]">संत चरित्र व अभंग गाथा</p>
            </div>
          </div>
        </div>

        {/* Audio Player Card */}
        <div className="p-3.5 rounded-2xl bg-orange-500/10 border border-orange-500/30 text-slate-200 space-y-2">
          <div className="flex justify-between items-center">
            <span className="font-extrabold text-xs text-orange-300 flex items-center gap-1.5">
              <Volume2 size={14} className="text-orange-400" />
              Now Playing: {activeSaint.name}
            </span>
            <span className="px-2 py-0.5 rounded bg-orange-500/20 text-orange-400 font-extrabold text-[9px]">AUDIO GUIDE</span>
          </div>
          <p className="text-xs text-white font-bold">{activeSaint.abhang}</p>
          <div className="w-full bg-white/10 h-1 rounded-full overflow-hidden">
            <div className={`bg-orange-500 h-full ${isPlaying ? 'w-[45%] animate-pulse' : 'w-0'}`} />
          </div>
        </div>

        {/* Saints Selection */}
        <div className="space-y-2.5 flex-1 overflow-y-auto pr-1">
          <p className="text-slate-400 text-[10px] font-bold uppercase tracking-wider">Patron Saints of Vari</p>

          {SAINTS.map(saint => (
            <div 
              key={saint.name}
              onClick={() => setActiveSaint(saint)}
              className={`p-3 rounded-2xl border cursor-pointer transition-all space-y-1 ${
                activeSaint.name === saint.name 
                  ? 'bg-orange-500/20 border-orange-500/50 text-white shadow-lg' 
                  : 'bg-[#131B2E] border-white/10 text-slate-300 hover:bg-white/10'
              }`}
            >
              <p className="font-extrabold text-xs text-white">{saint.name}</p>
              <p className="text-orange-400 text-[10px] font-bold">{saint.marathi}</p>
              <p className="text-[11px] text-slate-400 leading-tight">{saint.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
