"use client";

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, Search, Zap, Car, AlertTriangle, MapPin, Compass, CheckCircle2, Phone } from 'lucide-react';
import { policeService } from '@/lib/api';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';

export default function PoliceDispatchConsolePage() {
  const { t } = useAccessibility();
  const [corridorActive, setCorridorActive] = useState(false);
  const [patrolCount, setPatrolCount] = useState(18);

  useEffect(() => {
    policeService.getPatrolUnits()
      .then(res => {
        if (res.data) setPatrolCount(res.data.length || 18);
      })
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 rounded-3xl bg-[#131B2E] border border-indigo-500/40 shadow-2xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
            <Shield size={28} />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-white">
              {t('महाराष्ट्र पोलीस व वाहतूक बंदोबस्त (Police & Traffic)', 'Police Security & Traffic Control')}
            </h1>
            <p className="text-xs text-slate-300 font-medium">
              {t('रस्ता डायव्हर्जन, गस्त पथके व हरवलेले व्यक्ती शोध', 'Live traffic diversions, patrol unit tracking & missing person search')}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setCorridorActive(!corridorActive)}
            className={`px-4 py-2.5 rounded-xl text-xs font-extrabold transition-all shadow-lg flex items-center gap-2 border ${
              corridorActive 
                ? 'bg-red-600 text-white border-red-400 animate-pulse' 
                : 'bg-indigo-600 hover:bg-indigo-500 text-white border-indigo-400'
            }`}
          >
            <Zap size={16} />
            <span>{corridorActive ? t('रुग्णवाहिका कॉरिडॉर सक्रिय (GREEN CORRIDOR ACTIVE)', 'GREEN CORRIDOR ACTIVE') : t('इमर्जन्सी ग्रीन कॉरिडॉर सुरू करा', 'ACTIVATE GREEN CORRIDOR')}</span>
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Missing Person Search Board */}
        <div className="lg:col-span-2 p-6 rounded-3xl bg-[#131B2E] border border-white/10 shadow-2xl space-y-4">
          <div className="flex justify-between items-center pb-3 border-b border-white/10">
            <h3 className="font-extrabold text-white text-sm flex items-center gap-2">
              <Search className="text-indigo-400" size={18} />
              <span>{t('हरवलेल्या व्यक्तींचा शोध (Missing Person Search Operation)', 'Active Missing Person Searches')}</span>
            </h3>
            <span className="px-2.5 py-1 bg-indigo-500/20 text-indigo-300 text-xs font-extrabold rounded-full border border-indigo-500/40">
              2 SEARCHES ACTIVE
            </span>
          </div>

          <div className="p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-extrabold text-indigo-300">Case #MP-2026-004</span>
              <span className="px-2 py-0.5 rounded bg-red-600 text-white font-extrabold text-[10px]">HIGH PRIORITY</span>
            </div>
            <h4 className="font-black text-white text-base">अनिश जाधव (वय ८ वर्षे)</h4>
            <p className="text-xs text-slate-300">भगवा कुर्ता घातलेला मुलगा • आळंदी पाणी केंद्र क्र. २ जवळ विभक्त झाला.</p>
            <div className="pt-2 border-t border-indigo-500/20 flex justify-between items-center text-xs">
              <span className="text-slate-400">शोध क्षेत्र: <strong>२.० किमी परिसर</strong></span>
              <span className="text-emerald-400 font-extrabold">१४ पोलीस व स्वयंसेवक तैनात</span>
            </div>
          </div>
        </div>

        {/* Traffic Diversions & Patrol Streams */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-white/10 shadow-2xl space-y-4">
          <h3 className="font-extrabold text-sm text-white flex items-center gap-2">
            <Car className="text-indigo-400" size={18} />
            <span>{t('गस्त पथके (Active Patrol Units)', 'Active Patrol Units')}</span>
          </h3>

          <div className="space-y-2 text-xs">
            <div className="p-3 rounded-xl bg-[#0B0F19] border border-white/10 flex justify-between items-center">
              <div>
                <p className="font-bold text-white">पोलीस व्हॅन MH12-POL-4</p>
                <p className="text-[11px] text-slate-400">सासवड रोड • गस्त सुरू</p>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold text-[10px]">ACTIVE</span>
            </div>

            <div className="p-3 rounded-xl bg-[#0B0F19] border border-white/10 flex justify-between items-center">
              <div>
                <p className="font-bold text-white">वाहतूक पथक MH12-POL-9</p>
                <p className="text-[11px] text-slate-400">जेजुरी चौक • डायव्हर्जन कार्यरत</p>
              </div>
              <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold text-[10px]">DIVERSION</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
