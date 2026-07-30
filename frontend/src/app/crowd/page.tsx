"use client";

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, TrendingUp, AlertTriangle, MapPin, Compass } from 'lucide-react';
import InteractiveMap from '@/components/maps/InteractiveMap';
import { aiPredictionService } from '@/lib/api';

export default function CrowdIntelPage() {
  const [filter, setFilter] = useState('all');
  const [forecasts, setForecasts] = useState<any[]>([]);

  useEffect(() => {
    aiPredictionService.getCrowdForecasts()
      .then(res => {
        const data = Array.isArray(res.data) ? res.data : res.data.results || [];
        setForecasts(data);
      })
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-6 pb-12 p-4 sm:p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center bg-[#0F1420] border border-orange-500/30 p-5 rounded-2xl shadow-xl gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-white tracking-tight flex items-center gap-3">
            <Users className="text-orange-400" />
            गर्दी नियंत्रण व माहिती (CROWD INTEL)
          </h1>
          <p className="text-slate-400 text-xs mt-1">Real-time crowd density, bottleneck forecasts, and route diversion management</p>
        </div>
        <div className="flex gap-2">
          <span className="px-3.5 py-1.5 rounded-xl bg-orange-500/20 border border-orange-500/40 text-orange-400 text-xs font-extrabold flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-orange-400 animate-pulse" />
            AI Surge Predictor Active
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#0F1420] border border-white/10 p-4 sm:p-5 rounded-2xl shadow-lg">
          <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">एकूण वारकरी (Live Footfall)</p>
          <h3 className="text-2xl sm:text-3xl font-black text-white mt-1">1,240,500</h3>
          <p className="text-emerald-400 text-xs mt-2 flex items-center gap-1 font-bold">
            <TrendingUp size={14} /> +8.4% vs yesterday
          </p>
        </div>
        <div className="bg-[#0F1420] border border-white/10 p-4 sm:p-5 rounded-2xl shadow-lg">
          <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">सर्वोच्च घनता (Peak Density)</p>
          <h3 className="text-2xl sm:text-3xl font-black text-amber-400 mt-1">4.2 p/m²</h3>
          <p className="text-amber-400/80 text-xs mt-2 font-medium">Alandi Temple Approach</p>
        </div>
        <div className="bg-[#0F1420] border border-white/10 p-4 sm:p-5 rounded-2xl shadow-lg">
          <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">मार्ग बदल (Active Diversions)</p>
          <h3 className="text-2xl sm:text-3xl font-black text-blue-400 mt-1">3 Routes</h3>
          <p className="text-slate-400 text-xs mt-2 font-medium">Diverting 4,500/hr via Route B</p>
        </div>
        <div className="bg-[#0F1420] border border-white/10 p-4 sm:p-5 rounded-2xl shadow-lg">
          <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">गर्दीचा धोका (Congestion Risk)</p>
          <h3 className="text-2xl sm:text-3xl font-black text-emerald-400 mt-1">Low (18%)</h3>
          <p className="text-emerald-400/80 text-xs mt-2 font-medium">Flow steady across sectors</p>
        </div>
      </div>

      {/* GIS Interactive Heatmap */}
      <div className="space-y-3">
        <h2 className="text-base sm:text-lg font-bold text-white flex items-center gap-2">
          <MapPin size={18} className="text-orange-400" />
          पालखी मार्ग व घनता नकाशा (Live GIS & Density Map)
        </h2>
        <InteractiveMap selectedFilter="queue" />
      </div>

      {/* Bottleneck Alerts & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#0F1420] border border-white/10 p-5 rounded-2xl space-y-4 shadow-lg">
          <h3 className="text-sm sm:text-base font-bold text-white flex items-center gap-2">
            <AlertTriangle className="text-amber-400" size={18} />
            AI Bottleneck Surge Alerts (एआय इशारा)
          </h3>
          <div className="space-y-3">
            <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-slate-200">
              <div className="flex justify-between items-start">
                <span className="font-extrabold text-xs sm:text-sm text-amber-300">Sector 4 — Dehu Bridge</span>
                <span className="text-[9px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-extrabold">Predicted in 25m</span>
              </div>
              <p className="text-xs text-slate-300 mt-1">Flow rate exceeding 120/min. Recommend opening Gate 2 overflow bypass.</p>
            </div>
            <div className="p-3.5 rounded-xl bg-blue-500/10 border border-blue-500/30 text-slate-200">
              <div className="flex justify-between items-start">
                <span className="font-extrabold text-xs sm:text-sm text-blue-300">Sector 9 — Pandharpur Ring Road</span>
                <span className="text-[9px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 font-extrabold">Predicted in 50m</span>
              </div>
              <p className="text-xs text-slate-300 mt-1">Evening footfall expected to reach 180,000. Deploy 10 extra volunteers.</p>
            </div>
          </div>
        </div>

        <div className="bg-[#0F1420] border border-white/10 p-5 rounded-2xl space-y-4 shadow-lg">
          <h3 className="text-sm sm:text-base font-bold text-white flex items-center gap-2">
            <Compass className="text-emerald-400" size={18} />
            Route Diversion Controls (वाहतूक डायव्हर्जन)
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3.5 rounded-xl bg-[#131B2E] border border-white/10">
              <div>
                <p className="text-xs sm:text-sm font-bold text-white">Route A (Main Highway)</p>
                <p className="text-[11px] text-slate-400">Current Load: 82% (High)</p>
              </div>
              <button className="px-3.5 py-1.5 text-xs font-bold rounded-lg bg-orange-500/20 text-orange-400 border border-orange-500/40 hover:bg-orange-500/30 transition-all">
                Divert Traffic
              </button>
            </div>
            <div className="flex items-center justify-between p-3.5 rounded-xl bg-[#131B2E] border border-white/10">
              <div>
                <p className="text-xs sm:text-sm font-bold text-white">Route B (Bypass Corridor)</p>
                <p className="text-[11px] text-slate-400">Current Load: 34% (Normal)</p>
              </div>
              <button className="px-3.5 py-1.5 text-xs font-bold rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 hover:bg-emerald-500/30 transition-all">
                Active Bypass
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
