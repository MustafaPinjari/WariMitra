"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Trash2, Plus, Droplets, CheckCircle2, MapPin, AlertTriangle } from 'lucide-react';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';

export default function SanitationPage() {
  const { audienceRole, t } = useAccessibility();
  const isPilgrimMode = audienceRole === 'PILGRIM' || audienceRole === 'VOLUNTEER';

  const [statusMsg, setStatusMsg] = useState('');

  const handleReportCleanup = () => {
    setStatusMsg(t('स्वच्छता तक्रार नोंदवली आहे! नगरपालिका पथक रवाना होत आहे.', 'Cleanup Report Logged! Municipal crew dispatched.', 'सफाई दल भेजा जा रहा है।'));
    setTimeout(() => setStatusMsg(''), 4000);
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 rounded-3xl bg-[#131B2E] border border-teal-500/40 shadow-2xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-teal-500/20 border border-teal-500/40 flex items-center justify-center text-teal-400">
            <Trash2 size={28} />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-white">
              {t('स्वच्छता व शौचालय शोधा (Sanitation & Toilets)', 'Sanitation & Mobile Toilets')}
            </h1>
            <p className="text-xs text-slate-300 font-medium">
              {t('जवळची मोफत स्वच्छतागृहे, पाणी उपलब्धता व स्वच्छता तक्रार', 'Find mobile toilets, check water supply, or report cleanup')}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {statusMsg && <span className="text-teal-400 font-extrabold text-xs bg-teal-500/20 px-3 py-1.5 rounded-xl border border-teal-500/40 animate-pulse">{statusMsg}</span>}
          <button onClick={handleReportCleanup} className="px-4 py-2.5 bg-teal-600 hover:bg-teal-500 text-white font-extrabold text-xs rounded-xl shadow-lg flex items-center gap-2 transition-all">
            <Plus size={16} />
            <span>{t('कचरा / स्वच्छता तक्रार करा', 'Report Cleanup')}</span>
          </button>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-teal-500/30 space-y-4 shadow-xl">
          <div className="flex justify-between items-start">
            <span className="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-extrabold text-[10px]">
              ९५% स्वच्छ
            </span>
            <Droplets className="text-teal-400" size={20} />
          </div>

          <div>
            <h3 className="font-black text-white text-lg">सासवड विसावा मोबाईल शौचालय (Block A)</h3>
            <p className="text-xs text-slate-300 mt-1 flex items-center gap-1">
              <MapPin size={14} className="text-teal-400" /> पालखी तंबू परिसर
            </p>
          </div>

          <p className="text-xs text-slate-300">
            ✓ महिला व पुरुषांसाठी स्वतंत्र कक्ष • सतत पाणी पुरवठा सुरू
          </p>
        </div>

        <div className="p-6 rounded-3xl bg-[#131B2E] border border-teal-500/30 space-y-4 shadow-xl">
          <div className="flex justify-between items-start">
            <span className="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-extrabold text-[10px]">
              ९०% स्वच्छ
            </span>
            <Droplets className="text-teal-400" size={20} />
          </div>

          <div>
            <h3 className="font-black text-white text-lg">लोणंद बस स्थानक मोबाईल स्वच्छतागृह</h3>
            <p className="text-xs text-slate-300 mt-1 flex items-center gap-1">
              <MapPin size={14} className="text-teal-400" /> मुख्य रस्त्याजवळ
            </p>
          </div>

          <p className="text-xs text-slate-300">
            ✓ दिव्यांगांसाठी विशेष सुलभ शौचालय उपलब्ध
          </p>
        </div>

        <div className="p-6 rounded-3xl bg-[#131B2E] border border-teal-500/30 space-y-4 shadow-xl">
          <div className="flex justify-between items-start">
            <span className="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-extrabold text-[10px]">
              ९८% स्वच्छ
            </span>
            <Droplets className="text-teal-400" size={20} />
          </div>

          <div>
            <h3 className="font-black text-white text-lg">पंढरपूर मंदिर परिसर स्वच्छतागृह (Block 1)</h3>
            <p className="text-xs text-slate-300 mt-1 flex items-center gap-1">
              <MapPin size={14} className="text-teal-400" /> द्वार क्र. १ जवळ
            </p>
          </div>

          <p className="text-xs text-slate-300">
            ✓ नगरपालिका पथकाद्वारे प्रति १५ मिनिटांनी स्वच्छता
          </p>
        </div>

      </div>

    </div>
  );
}
