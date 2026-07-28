"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Radio, 
  Zap, 
  ChevronRight, 
  Play, 
  Pause, 
  RotateCcw,
  CloudSun,
  ShieldAlert,
  Flame,
  Activity,
  MapPin
} from 'lucide-react';
import GoogleMapContainer from '@/components/maps/GoogleMapContainer';

export default function GovernmentMissionControlPage() {
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [isPlaying, setIsPlaying] = useState(true);

  return (
    <div className="relative w-full h-[calc(100vh-4rem)] overflow-hidden bg-[#05080F]">
      {/* MAP BACKDROP */}
      <GoogleMapContainer activeRole="Government Mission Control" />

      {/* TOP OVERLAY BAR: Non-colliding Grid Header */}
      <div className="absolute top-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-4 pointer-events-none">
        
        {/* Left Telemetry HUD */}
        <div className="pointer-events-auto bg-[#0F1420]/90 backdrop-blur-2xl border border-orange-500/40 px-4 py-2.5 rounded-2xl shadow-2xl flex items-center gap-4 max-w-full">
          <div className="flex items-center gap-2.5">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-orange-500"></span>
            </span>
            <div>
              <p className="text-white font-black text-xs tracking-tight uppercase flex items-center gap-1.5">
                <span>पंढरपूर वारी मिशन कंट्रोल</span>
                <span className="text-orange-400 font-mono text-[10px]">(GOVT GIS)</span>
              </p>
              <p className="text-slate-400 text-[10px]">Real-Time Operational Command</p>
            </div>
          </div>

          <div className="h-6 w-px bg-white/15 hidden sm:block" />

          <div className="hidden sm:flex items-center gap-5 text-xs">
            <div>
              <p className="text-slate-400 font-bold text-[9px] uppercase tracking-wider">एकूण वारकरी (Footfall)</p>
              <p className="text-white font-extrabold text-xs">1,240,500 <span className="text-emerald-400 text-[10px]">(+8.4%)</span></p>
            </div>
            <div>
              <p className="text-slate-400 font-bold text-[9px] uppercase tracking-wider">सर्वोच्च घनता (Density)</p>
              <p className="text-amber-400 font-extrabold text-xs">4.2 p/m² <span className="text-slate-400 text-[9px]">(Alandi)</span></p>
            </div>
            <div>
              <p className="text-slate-400 font-bold text-[9px] uppercase tracking-wider">आणीबाणी (Active SOS)</p>
              <p className="text-red-400 font-extrabold text-xs">2 Critical</p>
            </div>
            <div className="hidden lg:flex items-center gap-2 pl-2 border-l border-white/10 text-slate-300">
              <CloudSun size={15} className="text-amber-400" />
              <div>
                <p className="text-[10px] font-bold">34°C • Sunny</p>
                <p className="text-[9px] text-slate-400">Humidity 45%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right AI Surge Recommendation Banner */}
        <div className="pointer-events-auto bg-[#0F1420]/90 backdrop-blur-2xl border border-amber-500/40 px-3.5 py-2 rounded-2xl text-xs flex items-center gap-3 shadow-xl">
          <Zap className="text-amber-400 animate-bounce flex-shrink-0" size={16} />
          <div className="hidden md:block">
            <p className="text-amber-300 font-bold text-xs">AI Surge Alert: Dehu Bridge Bottleneck</p>
            <p className="text-slate-300 text-[10px]">Flow rate exceeding 120/min. Recommend opening Gate 2 overflow bypass.</p>
          </div>
          <button className="px-3 py-1 bg-orange-500 hover:bg-orange-600 text-white font-extrabold rounded-xl text-[10px] transition-all shadow-md flex-shrink-0">
            Execute Bypass
          </button>
        </div>

      </div>

      {/* RIGHT SIDE DRAWER: Live Incident Feed (Clean non-overlapping bounds) */}
      <AnimatePresence>
        <motion.div
          initial={{ x: 340, opacity: 0 }}
          animate={{ x: drawerOpen ? 0 : 320, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 280, damping: 28 }}
          className="absolute top-20 right-4 bottom-20 z-20 w-80 sm:w-96 bg-[#0B0F19]/95 backdrop-blur-2xl border border-orange-500/30 p-4 rounded-3xl shadow-2xl flex flex-col space-y-3"
        >
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Radio size={15} className="text-red-500 animate-pulse" />
              <div>
                <p className="text-white font-extrabold text-xs">Live Operational Incident Feed</p>
                <p className="text-slate-400 text-[10px]">प्रत्यक्ष घटना अपडेट्स</p>
              </div>
            </div>
            <button 
              onClick={() => setDrawerOpen(!drawerOpen)}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors"
            >
              <ChevronRight size={16} className={`transition-transform duration-300 ${drawerOpen ? '' : 'rotate-180'}`} />
            </button>
          </div>

          {/* Incident Feed Items */}
          <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 text-xs">
            <div className="p-3 rounded-2xl bg-red-500/10 border border-red-500/40 text-slate-200">
              <div className="flex justify-between items-start">
                <span className="font-bold text-red-400 flex items-center gap-1.5 text-xs">
                  <ShieldAlert size={14} /> Medical Emergency SOS
                </span>
                <span className="text-[9px] bg-red-500/20 px-2 py-0.5 rounded font-bold text-red-300">2m ago</span>
              </div>
              <p className="text-[11px] text-slate-300 mt-1">Unresponsive pilgrim (Dive Ghat). Ambulance MH12-WM-1001 dispatched (ETA: 3m).</p>
            </div>

            <div className="p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/40 text-slate-200">
              <div className="flex justify-between items-start">
                <span className="font-bold text-indigo-300 flex items-center gap-1.5 text-xs">
                  <MapPin size={14} /> Traffic Diversion Active
                </span>
                <span className="text-[9px] bg-indigo-500/20 px-2 py-0.5 rounded font-bold text-indigo-300">8m ago</span>
              </div>
              <p className="text-[11px] text-slate-300 mt-1">Jejuri Slope Corridor redirected via Bypass Route B.</p>
            </div>

            <div className="p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/40 text-slate-200">
              <div className="flex justify-between items-start">
                <span className="font-bold text-emerald-400 flex items-center gap-1.5 text-xs">
                  <Activity size={14} /> NGO Water Refill Complete
                </span>
                <span className="text-[9px] bg-emerald-500/20 px-2 py-0.5 rounded font-bold text-emerald-300">14m ago</span>
              </div>
              <p className="text-[11px] text-slate-300 mt-1">Tanker #WT-04 delivered 50,000L ORS water to Saswad Station 2.</p>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>

      {/* BOTTOM CENTER: Timeline Scrubber Panel */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 pointer-events-none">
        <div className="pointer-events-auto bg-[#0F1420]/95 backdrop-blur-2xl border border-orange-500/30 px-5 py-2 rounded-full shadow-2xl flex items-center gap-3.5 text-xs">
          <button 
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-2 bg-orange-500 text-white rounded-full hover:bg-orange-600 transition-all shadow-md flex-shrink-0"
          >
            {isPlaying ? <Pause size={13} /> : <Play size={13} />}
          </button>
          <button className="text-slate-400 hover:text-white transition-colors flex-shrink-0">
            <RotateCcw size={13} />
          </button>
          <div className="flex items-center gap-3">
            <span className="text-slate-400 text-[10px] font-mono">08:00 AM</span>
            <div className="w-44 sm:w-64 bg-white/10 h-1.5 rounded-full overflow-hidden relative">
              <div className="bg-orange-500 h-full w-[65%]" />
            </div>
            <span className="text-orange-400 text-[10px] font-mono font-bold">14:30 PM (LIVE)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
