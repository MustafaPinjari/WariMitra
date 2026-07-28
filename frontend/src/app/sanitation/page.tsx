"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Trash2, Plus, ChevronRight, CheckCircle2, Droplets } from 'lucide-react';
import dynamic from 'next/dynamic';
const GoogleMapContainer = dynamic(() => import('@/components/maps/GoogleMapContainer'), { ssr: false });

export default function SanitationPage() {
  const [drawerOpen, setDrawerOpen] = useState(true);

  return (
    <div className="relative w-full h-[calc(100vh-4rem)] overflow-hidden bg-[#05080F]">
      {/* INTERACTIVE MAP BACKDROP */}
      <GoogleMapContainer activeRole="Sanitation & Waste Management Control" />

      {/* TOP HEADER OVERLAY */}
      <div className="absolute top-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-4 pointer-events-none">
        <div className="pointer-events-auto bg-[#0F1420]/90 backdrop-blur-2xl border border-teal-500/40 px-4 py-2.5 rounded-2xl shadow-2xl flex items-center gap-3.5 max-w-full">
          <div className="p-2 bg-teal-500/20 text-teal-400 rounded-xl">
            <Trash2 size={20} />
          </div>
          <div>
            <p className="text-white font-extrabold text-xs tracking-tight flex items-center gap-2">
              <span>स्वच्छता व शौचालय व्यवस्थापन (WASTE & SANITATION)</span>
              <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
            </p>
            <p className="text-slate-400 text-[10px]">142 Public Toilets Tracked • Municipality Cleaning Crew Active</p>
          </div>
        </div>

        <div className="pointer-events-auto">
          <button className="px-4 py-2.5 bg-teal-600 hover:bg-teal-500 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-teal-500/30 transition-all flex items-center gap-2 active:scale-95">
            <Plus size={16} />
            <span>Dispatch Cleaning Crew</span>
          </button>
        </div>
      </div>

      {/* RIGHT SIDE DRAWER: Public Toilets & Waste Alerts */}
      <AnimatePresence>
        <motion.div
          initial={{ x: 340, opacity: 0 }}
          animate={{ x: drawerOpen ? 0 : 320, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 280, damping: 28 }}
          className="absolute top-20 right-4 bottom-6 z-20 w-80 sm:w-96 bg-[#0B0F19]/95 backdrop-blur-2xl border border-teal-500/30 p-4 rounded-3xl shadow-2xl flex flex-col space-y-4"
        >
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Droplets size={16} className="text-teal-400" />
              <div>
                <p className="text-white font-extrabold text-xs">Public Toilet & Cleaning Status</p>
                <p className="text-slate-400 text-[10px]">सार्वजनिक स्वच्छतागृह व कचरा व्यवस्थापन</p>
              </div>
            </div>
            <button 
              onClick={() => setDrawerOpen(!drawerOpen)}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors"
            >
              <ChevronRight size={16} className={`transition-transform duration-300 ${drawerOpen ? '' : 'rotate-180'}`} />
            </button>
          </div>

          <div className="p-3.5 rounded-2xl bg-teal-500/10 border border-teal-500/30 text-slate-200 space-y-2">
            <div className="flex justify-between items-center">
              <span className="font-extrabold text-xs text-teal-300">Alandi Shelter Block A Toilet</span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-extrabold text-[9px]">92% CLEAN</span>
            </div>
            <p className="text-[11px] text-slate-300">Unisex / Accessible • Water Supply Active</p>
          </div>

          <div className="p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-slate-200 space-y-2">
            <div className="flex justify-between items-center">
              <span className="font-extrabold text-xs text-amber-300">Dive Ghat Rest Stop Waste Bin</span>
              <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-extrabold text-[9px]">DISPATCHED</span>
            </div>
            <p className="text-[11px] text-slate-300">Plastic Bottle Overflow • Municipality Crew #4 En Route</p>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
