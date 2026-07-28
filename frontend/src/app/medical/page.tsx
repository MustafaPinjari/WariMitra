"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  Stethoscope, 
  Plus, 
  Clock, 
  ChevronRight,
  HeartPulse,
  Syringe,
  BedDouble
} from 'lucide-react';
import GoogleMapContainer from '@/components/maps/GoogleMapContainer';
import { medicalService } from '@/lib/api';

export default function MedicalOperationsPage() {
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [stats, setStats] = useState({ camps: 5, ambulances: 4, freeBeds: 142 });

  useEffect(() => {
    // Attempt real API fetch with silent fallback
    medicalService.getCamps()
      .then(res => {
        if (res.data) setStats(prev => ({ ...prev, camps: res.data.length || prev.camps }));
      })
      .catch(() => {});
  }, []);

  return (
    <div className="relative w-full h-[calc(100vh-4rem)] overflow-hidden bg-[#05080F]">
      {/* INTERACTIVE MAP BACKDROP */}
      <GoogleMapContainer activeRole="Hospital Operations & Ambulance Dispatch" />

      {/* TOP HEADER OVERLAY */}
      <div className="absolute top-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-4 pointer-events-none">
        <div className="pointer-events-auto bg-[#0F1420]/90 backdrop-blur-2xl border border-emerald-500/40 px-4 py-2.5 rounded-2xl shadow-2xl flex items-center gap-3.5 max-w-full">
          <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-xl">
            <Activity size={20} />
          </div>
          <div>
            <p className="text-white font-extrabold text-xs tracking-tight flex items-center gap-2">
              <span>वैद्यकीय व रुग्णवाहिका केंद्र (MEDICAL OPS)</span>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            </p>
            <p className="text-slate-400 text-[10px]">
              {stats.camps} Health Camps • {stats.ambulances} Ambulances Available • {stats.freeBeds} Free Beds
            </p>
          </div>
        </div>

        <div className="pointer-events-auto">
          <button className="px-4 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-emerald-500/30 transition-all flex items-center gap-2 active:scale-95">
            <Plus size={16} />
            <span>Dispatch Emergency Ambulance</span>
          </button>
        </div>
      </div>

      {/* RIGHT SIDE DRAWER: Emergency Cases & ETAs */}
      <AnimatePresence>
        <motion.div
          initial={{ x: 340, opacity: 0 }}
          animate={{ x: drawerOpen ? 0 : 320, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 280, damping: 28 }}
          className="absolute top-20 right-4 bottom-6 z-20 w-80 sm:w-96 bg-[#0B0F19]/95 backdrop-blur-2xl border border-emerald-500/30 p-4 rounded-3xl shadow-2xl flex flex-col space-y-4"
        >
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Stethoscope size={16} className="text-emerald-400" />
              <div>
                <p className="text-white font-extrabold text-xs">Live Emergency Cases & ETAs</p>
                <p className="text-slate-400 text-[10px]">रुग्णवाहिका ट्रॅकिंग व ट्रायज</p>
              </div>
            </div>
            <button 
              onClick={() => setDrawerOpen(!drawerOpen)}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors"
            >
              <ChevronRight size={16} className={`transition-transform duration-300 ${drawerOpen ? '' : 'rotate-180'}`} />
            </button>
          </div>

          {/* Active Ambulance Unit ETA */}
          <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-slate-200 space-y-2">
            <div className="flex justify-between items-center">
              <span className="font-extrabold text-xs text-emerald-300">Ambulance MH12-WM-1001</span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-extrabold text-[9px]">EN ROUTE</span>
            </div>
            <p className="text-xs text-slate-300">Responding to Cardiac Emergency (Dive Ghat)</p>
            <div className="pt-2 border-t border-white/10 flex justify-between items-center text-xs font-bold">
              <span className="text-slate-400 text-[11px]">Target ETA:</span>
              <span className="text-emerald-400 flex items-center gap-1"><Clock size={13} /> 3 Minutes</span>
            </div>
          </div>

          {/* Patient Triage Queue */}
          <div className="space-y-2.5 flex-1 overflow-y-auto pr-1">
            <p className="text-slate-400 text-[10px] font-bold uppercase tracking-wider">Patient Triage Queue</p>

            <div className="p-3 rounded-2xl bg-[#131B2E] border border-white/10 space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="font-bold text-white flex items-center gap-1.5">
                  <HeartPulse size={14} className="text-red-400" />
                  Ramesh Jadhav (62/M)
                </span>
                <span className="text-amber-400 font-bold text-[10px]">High Priority</span>
              </div>
              <p className="text-[11px] text-slate-400">Severe Dehydration • Health Camp Alpha</p>
            </div>

            <div className="p-3 rounded-2xl bg-[#131B2E] border border-white/10 space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="font-bold text-white flex items-center gap-1.5">
                  <Activity size={14} className="text-blue-400" />
                  Sunita Shinde (45/F)
                </span>
                <span className="text-blue-400 font-bold text-[10px]">Low Priority</span>
              </div>
              <p className="text-[11px] text-slate-400">Foot Blisters • Health Camp Beta</p>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
