"use client";

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, TrendingUp, AlertTriangle, MapPin, Compass, Droplets, Navigation, CheckCircle2 } from 'lucide-react';
import InteractiveMap from '@/components/maps/InteractiveMap';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';

export default function CrowdIntelPage() {
  const { audienceRole, t } = useAccessibility();
  const isPilgrimMode = audienceRole === 'PILGRIM' || audienceRole === 'VOLUNTEER';

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-[#131B2E] border border-orange-500/30 p-6 rounded-3xl shadow-xl gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-white tracking-tight flex items-center gap-3">
            <Users className="text-orange-400" size={24} />
            <span>{t('गर्दी व रस्ता नकाशा (Crowd & Route Map)', 'Crowd Intelligence & Live GIS')}</span>
          </h1>
          <p className="text-slate-300 text-xs mt-1 font-medium">
            {t('पालखी मार्ग, मोफत पाणी केंद्रे, अन्नछत्र व गर्दीची स्थिती', 'Real-time crowd density, Palkhi route, free water & food centers')}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-xs font-extrabold flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            {t('नकाशा सक्रिय (GIS Active)', 'AI Surge Predictor Active')}
          </span>
        </div>
      </div>

      {/* PILGRIM MODE: Quick Route Info & Water Locator Header */}
      {isPilgrimMode && (
        <div className="p-4 rounded-2xl bg-orange-500/10 border border-orange-500/30 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2.5">
            <Droplets className="text-blue-400" size={20} />
            <div>
              <p className="font-extrabold text-white">{t('तुमच्या जवळ १२०+ पिण्याचे पाणी केंद्रे उपलब्ध आहेत', '120+ Drinking Water Points Available Nearby')}</p>
              <p className="text-slate-300">{t('निळ्या रंगाच्या चिन्हावर टॅप करून मार्ग मिळवा', 'Tap any blue marker on map for directions')}</p>
            </div>
          </div>
          <button className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl transition-all shadow">
            {t('पाणी केंद्र शोधा', 'Find Water')}
          </button>
        </div>
      )}

      {/* KPI Cards (Operational / Government Mode) */}
      {!isPilgrimMode && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-[#131B2E] border border-white/10 p-5 rounded-2xl shadow-lg">
            <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">{t('एकूण वारकरी (Live Footfall)', 'Total Footfall')}</p>
            <h3 className="text-2xl sm:text-3xl font-black text-white mt-1">१,२४०,५००</h3>
            <p className="text-emerald-400 text-xs mt-2 flex items-center gap-1 font-bold">
              <TrendingUp size={14} /> +8.4% vs yesterday
            </p>
          </div>
          <div className="bg-[#131B2E] border border-white/10 p-5 rounded-2xl shadow-lg">
            <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">{t('सर्वोच्च घनता (Peak Density)', 'Peak Density')}</p>
            <h3 className="text-2xl sm:text-3xl font-black text-amber-400 mt-1">4.2 p/m²</h3>
            <p className="text-amber-400/80 text-xs mt-2 font-medium">Alandi Temple Approach</p>
          </div>
          <div className="bg-[#131B2E] border border-white/10 p-5 rounded-2xl shadow-lg">
            <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">{t('मार्ग बदल (Active Diversions)', 'Active Diversions')}</p>
            <h3 className="text-2xl sm:text-3xl font-black text-blue-400 mt-1">3 Routes</h3>
            <p className="text-slate-400 text-xs mt-2 font-medium">Diverting 4,500/hr via Route B</p>
          </div>
          <div className="bg-[#131B2E] border border-white/10 p-5 rounded-2xl shadow-lg">
            <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">{t('गर्दीचा धोका (Congestion Risk)', 'Congestion Risk')}</p>
            <h3 className="text-2xl sm:text-3xl font-black text-emerald-400 mt-1">Low (18%)</h3>
            <p className="text-emerald-400/80 text-xs mt-2 font-medium">Flow steady across sectors</p>
          </div>
        </div>
      )}

      {/* GIS Interactive Heatmap */}
      <div className="space-y-3">
        <h2 className="text-base sm:text-lg font-bold text-white flex items-center gap-2">
          <MapPin size={18} className="text-orange-400" />
          <span>{t('पालखी मार्ग व घनता नकाशा (Live GIS & Density Map)', 'Live GIS & Route Map')}</span>
        </h2>
        <InteractiveMap selectedFilter="queue" />
      </div>

      {/* Bottleneck Alerts & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#131B2E] border border-white/10 p-6 rounded-3xl space-y-4 shadow-xl">
          <h3 className="text-sm sm:text-base font-bold text-white flex items-center gap-2">
            <AlertTriangle className="text-amber-400" size={18} />
            <span>{t('एआय गर्दीचा इशारा (AI Bottleneck Surge Alerts)', 'AI Bottleneck Alerts')}</span>
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

        <div className="bg-[#131B2E] border border-white/10 p-6 rounded-3xl space-y-4 shadow-xl">
          <h3 className="text-sm sm:text-base font-bold text-white flex items-center gap-2">
            <Compass className="text-emerald-400" size={18} />
            <span>{t('मार्ग बदल (Route Diversion Controls)', 'Route Diversion Controls')}</span>
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3.5 rounded-xl bg-[#0B0F19] border border-white/10">
              <div>
                <p className="text-xs sm:text-sm font-bold text-white">Route A (Main Highway)</p>
                <p className="text-[11px] text-slate-400">Current Load: 82% (High)</p>
              </div>
              <button className="px-3.5 py-1.5 text-xs font-bold rounded-xl bg-orange-500/20 text-orange-300 border border-orange-500/40 hover:bg-orange-500/30 transition-all">
                {t('डायव्हर्जन करा', 'Divert Traffic')}
              </button>
            </div>
            <div className="flex items-center justify-between p-3.5 rounded-xl bg-[#0B0F19] border border-white/10">
              <div>
                <p className="text-xs sm:text-sm font-bold text-white">Route B (Bypass Corridor)</p>
                <p className="text-[11px] text-slate-400">Current Load: 34% (Normal)</p>
              </div>
              <button className="px-3.5 py-1.5 text-xs font-bold rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-500/30 transition-all">
                {t('बायपास सुरू', 'Active Bypass')}
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
