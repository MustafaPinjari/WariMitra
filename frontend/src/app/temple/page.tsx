"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Tent, 
  Clock, 
  Sparkles, 
  Plus,
  ChevronRight
} from 'lucide-react';
import GoogleMapContainer from '@/components/maps/GoogleMapContainer';
import { templeService } from '@/lib/api';

export default function TempleQueueConsolePage() {
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [queueData, setQueueData] = useState({ gate1Wait: '260m', gate2Wait: '80m', totalTokens: 18500 });

  useEffect(() => {
    templeService.getQueueStatus()
      .then(res => {
        if (res.data) setQueueData(prev => ({ ...prev, ...res.data }));
      })
      .catch(() => {});
  }, []);

  return (
    <div className="relative w-full h-[calc(100vh-4rem)] overflow-hidden bg-[#05080F]">
      {/* INTERACTIVE MAP BACKDROP */}
      <GoogleMapContainer activeRole="Pandharpur Temple Queue & Crowd Flow Console" />

      {/* TOP HEADER OVERLAY */}
      <div className="absolute top-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-4 pointer-events-none">
        <div className="pointer-events-auto bg-[#0F1420]/90 backdrop-blur-2xl border border-purple-500/40 px-4 py-2.5 rounded-2xl shadow-2xl flex items-center gap-3.5 max-w-full">
          <div className="p-2 bg-purple-500/20 text-purple-400 rounded-xl">
            <Tent size={20} />
          </div>
          <div>
            <p className="text-white font-extrabold text-xs tracking-tight flex items-center gap-2">
              <span>श्री विठ्ठल मंदिर दर्शन रांग (TEMPLE QUEUE FLOW)</span>
              <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
            </p>
            <p className="text-slate-400 text-[10px]">
              Gate 1: {queueData.gate1Wait} Wait • Gate 2: {queueData.gate2Wait} Wait • {queueData.totalTokens.toLocaleString()} Tokens Today
            </p>
          </div>
        </div>
      </div>

      {/* RIGHT SIDE DRAWER: Gate Capacity & Darshan ETAs */}
      <AnimatePresence>
        <motion.div
          initial={{ x: 340, opacity: 0 }}
          animate={{ x: drawerOpen ? 0 : 320, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 280, damping: 28 }}
          className="absolute top-20 right-4 bottom-6 z-20 w-80 sm:w-96 bg-[#0B0F19]/95 backdrop-blur-2xl border border-purple-500/30 p-4 rounded-3xl shadow-2xl flex flex-col space-y-4"
        >
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Sparkles size={16} className="text-purple-400" />
              <div>
                <p className="text-white font-extrabold text-xs">Live Gate Capacity & Queue Flow</p>
                <p className="text-slate-400 text-[10px]">मंदिर प्रवेश व दर्शन वेळेचा अंदाज</p>
              </div>
            </div>
            <button 
              onClick={() => setDrawerOpen(!drawerOpen)}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors"
            >
              <ChevronRight size={16} className={`transition-transform duration-300 ${drawerOpen ? '' : 'rotate-180'}`} />
            </button>
          </div>

          {/* Gate 1 Card */}
          <div className="p-3.5 rounded-2xl bg-red-500/10 border border-red-500/30 text-slate-200 space-y-2">
            <div className="flex justify-between items-center">
              <span className="font-extrabold text-xs text-white">Gate 1 — Main Entrance (मुख्य प्रवेश)</span>
              <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-400 font-extrabold text-[9px]">FULL (98%)</span>
            </div>
            <p className="text-[11px] text-slate-300">General Queue • 3,200 Pilgrims • Wait: {queueData.gate1Wait}</p>
            <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
              <div className="bg-red-500 h-full w-[98%]" />
            </div>
          </div>

          {/* Gate 2 Card */}
          <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-slate-200 space-y-2">
            <div className="flex justify-between items-center">
              <span className="font-extrabold text-xs text-white">Gate 2 — Senior Citizens (ज्येष्ठ नागरिक)</span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-extrabold text-[9px]">OPEN (45%)</span>
            </div>
            <p className="text-[11px] text-slate-300">Senior Line • 450 Pilgrims • Wait: {queueData.gate2Wait}</p>
            <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
              <div className="bg-emerald-500 h-full w-[45%]" />
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
