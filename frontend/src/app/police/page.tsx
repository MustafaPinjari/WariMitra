"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, 
  Search, 
  Zap, 
  ChevronRight,
  Car,
  AlertTriangle
} from 'lucide-react';
import GoogleMapContainer from '@/components/maps/GoogleMapContainer';
import { policeService } from '@/lib/api';

export default function PoliceDispatchConsolePage() {
  const [corridorActive, setCorridorActive] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [patrolCount, setPatrolCount] = useState(18);

  useEffect(() => {
    policeService.getPatrolUnits()
      .then(res => {
        if (res.data) setPatrolCount(res.data.length || 18);
      })
      .catch(() => {});
  }, []);

  return (
    <div className="relative w-full h-[calc(100vh-4rem)] overflow-hidden bg-[#05080F]">
      {/* INTERACTIVE MAP BACKDROP */}
      <GoogleMapContainer activeRole="Police 911 CAD Dispatch Console" />

      {/* TOP HEADER OVERLAY */}
      <div className="absolute top-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-4 pointer-events-none">
        <div className="pointer-events-auto bg-[#0F1420]/90 backdrop-blur-2xl border border-indigo-500/40 px-4 py-2.5 rounded-2xl shadow-2xl flex items-center gap-3.5 max-w-full">
          <div className="p-2 bg-indigo-500/20 text-indigo-400 rounded-xl">
            <Shield size={20} />
          </div>
          <div>
            <p className="text-white font-extrabold text-xs tracking-tight flex items-center gap-2">
              <span>महाराष्ट्र पोलीस बंदोबस्त (POLICE CAD)</span>
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
            </p>
            <p className="text-slate-400 text-[10px]">
              {patrolCount} Patrol Units • 4 Diversions Active • 2 Search Operations
            </p>
          </div>
        </div>

        <div className="pointer-events-auto">
          <button
            onClick={() => setCorridorActive(!corridorActive)}
            className={`px-4 py-2.5 rounded-xl text-xs font-extrabold transition-all shadow-lg flex items-center gap-2 border active:scale-95 ${
              corridorActive 
                ? 'bg-red-600 text-white border-red-400 animate-pulse shadow-red-500/40' 
                : 'bg-[#0F1420] text-indigo-300 border-indigo-500/40 hover:bg-indigo-500/20'
            }`}
          >
            <Zap size={15} />
            <span>{corridorActive ? 'CLEAR EMERGENCY GREEN CORRIDOR' : 'ACTIVATE EMERGENCY GREEN CORRIDOR'}</span>
          </button>
        </div>
      </div>

      {/* RIGHT SIDE DRAWER: Missing Person Search & Patrol Units */}
      <AnimatePresence>
        <motion.div
          initial={{ x: 340, opacity: 0 }}
          animate={{ x: drawerOpen ? 0 : 320, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 280, damping: 28 }}
          className="absolute top-20 right-4 bottom-6 z-20 w-80 sm:w-96 bg-[#0B0F19]/95 backdrop-blur-2xl border border-indigo-500/30 p-4 rounded-3xl shadow-2xl flex flex-col space-y-4"
        >
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Search size={16} className="text-indigo-400" />
              <div>
                <p className="text-white font-extrabold text-xs">Missing Person Search Radius</p>
                <p className="text-slate-400 text-[10px]">हरवलेले व्यक्ती शोध मोहीम</p>
              </div>
            </div>
            <button 
              onClick={() => setDrawerOpen(!drawerOpen)}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors"
            >
              <ChevronRight size={16} className={`transition-transform duration-300 ${drawerOpen ? '' : 'rotate-180'}`} />
            </button>
          </div>

          {/* Active Missing Person Search Alert */}
          <div className="p-3.5 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 text-slate-200 space-y-2">
            <div className="flex justify-between items-center">
              <span className="font-extrabold text-xs text-indigo-300">Case #MP-2026-004</span>
              <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-400 font-extrabold text-[9px]">HIGH PRIORITY</span>
            </div>
            <p className="text-xs font-bold text-white">Anish Jadhav (8 yrs)</p>
            <p className="text-[11px] text-slate-300">Wearing Saffron Kurta. Separated near Alandi Water Point 2.</p>
            <div className="pt-2 border-t border-white/10 flex justify-between items-center text-[10px] text-slate-300">
              <span>Radius: 2.0 km Circle</span>
              <span className="text-indigo-400 font-extrabold">14 Patrols Deployed</span>
            </div>
          </div>

          {/* Patrol Units Stream */}
          <div className="space-y-2 flex-1 overflow-y-auto pr-1">
            <p className="text-slate-400 text-[10px] font-bold uppercase tracking-wider">Patrol Units Stream</p>
            
            <div className="p-3 rounded-2xl bg-[#131B2E] border border-white/10 flex justify-between items-center text-xs">
              <div className="flex items-center gap-2.5">
                <Car size={16} className="text-indigo-400" />
                <div>
                  <p className="font-bold text-white">Unit MH12-POL-4</p>
                  <p className="text-[10px] text-slate-400">Pune Sector 3 • 24 km/h</p>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">Patrolling</span>
            </div>

            <div className="p-3 rounded-2xl bg-[#131B2E] border border-white/10 flex justify-between items-center text-xs">
              <div className="flex items-center gap-2.5">
                <AlertTriangle size={16} className="text-amber-400" />
                <div>
                  <p className="font-bold text-white">Unit MH12-POL-9</p>
                  <p className="text-[10px] text-slate-400">Jejuri Slope Checkpoint</p>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 text-[10px] font-bold">Diversion Active</span>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
