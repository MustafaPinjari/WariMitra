"use client";

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Tent, Clock, Sparkles, Plus, CheckCircle2, UserCheck, ShieldCheck, ArrowRight } from 'lucide-react';
import { templeService } from '@/lib/api';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';

export default function TempleQueueConsolePage() {
  const { audienceRole, t } = useAccessibility();
  const isPilgrimMode = audienceRole === 'PILGRIM' || audienceRole === 'VOLUNTEER';

  const [queueData, setQueueData] = useState({ gate1Wait: '45 मि.', gate2Wait: '20 मि.', totalTokens: 18500 });
  const [bookingSuccess, setBookingSuccess] = useState(false);

  useEffect(() => {
    templeService.getQueueStatus().then(res => {
      if (res.data) setQueueData(prev => ({ ...prev, ...res.data }));
    }).catch(() => {});
  }, []);

  const handleBookSlot = () => {
    setBookingSuccess(true);
    setTimeout(() => setBookingSuccess(false), 5000);
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 rounded-3xl bg-[#131B2E] border border-purple-500/40 shadow-2xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-400">
            <Tent size={28} />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-white">
              {t('श्री विठ्ठल दर्शन रांग व वेळ (Temple Queue)', 'Pandharpur Temple Darshan & Queue Control')}
            </h1>
            <p className="text-xs text-slate-300 font-medium">
              {t('थेट दर्शन वेळ, प्रवेश द्वार व ज्येष्ठ नागरिक रांग', 'Live darshan wait times, entry gate status & e-pass slots')}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-full bg-purple-500/20 border border-purple-500/40 text-purple-300 text-xs font-extrabold flex items-center gap-2">
            <Clock size={14} className="animate-spin-slow" />
            {t('सध्याचा रांगेचा वेळ: ४५ मि.', 'Live Queue: 45 Mins')}
          </span>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* Gate 1 Card: Main Entry */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-red-500/30 space-y-4 shadow-xl">
          <div className="flex justify-between items-start">
            <span className="px-2.5 py-0.5 rounded bg-red-500/20 text-red-300 font-extrabold text-[10px]">
              मुख्य दर्शन रांग (GATE 1)
            </span>
            <span className="text-xs font-extrabold text-red-400">
              ४५ मि. वाट पहा
            </span>
          </div>

          <div>
            <h3 className="font-black text-white text-lg">{t('द्वार क्र. १ — सर्वसामान्य रांग', 'Gate 1 — General Queue')}</h3>
            <p className="text-xs text-slate-300 mt-1">
              {t('पदस्पर्श दर्शन व मुख दर्शन रांग सुरू आहे.', 'Foot touch & Mukha darshan lines active.')}
            </p>
          </div>

          <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden">
            <div className="bg-red-500 h-full w-[85%]" />
          </div>

          <p className="text-[11px] text-slate-400 font-medium">
            {t('रांगेची लांबी: अंदाजे ३,२०० वारकरी', 'Current Line Length: 3,200 Pilgrims')}
          </p>
        </div>

        {/* Gate 2 Card: Senior Citizens & Divyang */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-emerald-500/30 space-y-4 shadow-xl">
          <div className="flex justify-between items-start">
            <span className="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-extrabold text-[10px]">
              ज्येष्ठ नागरिक / दिव्यांग (GATE 2)
            </span>
            <span className="text-xs font-extrabold text-emerald-400">
              २० मि. वाट पहा
            </span>
          </div>

          <div>
            <h3 className="font-black text-white text-lg">{t('द्वार क्र. २ — ज्येष्ठ व दिव्यांग', 'Gate 2 — Senior & Divyang')}</h3>
            <p className="text-xs text-slate-300 mt-1">
              {t('६० वर्षांवरील नागरिक व दिव्यांगांसाठी जलद रांग.', 'Fast-track queue for senior citizens and disabled pilgrims.')}
            </p>
          </div>

          <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden">
            <div className="bg-emerald-500 h-full w-[40%]" />
          </div>

          <p className="text-[11px] text-slate-400 font-medium">
            {t('रांगेची लांबी: अंदाजे ४५० वारकरी', 'Current Line Length: 450 Pilgrims')}
          </p>
        </div>

        {/* E-Pass / Slot Booking */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-purple-500/30 space-y-4 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-start mb-3">
              <span className="px-2.5 py-0.5 rounded bg-purple-500/20 text-purple-300 font-extrabold text-[10px]">
                ई-पास वेळ (E-PASS SLOT)
              </span>
              <Sparkles className="text-purple-400" size={18} />
            </div>

            <h3 className="font-black text-white text-lg">{t('डिजिटल दर्शन पास बुकिंग', 'Digital Darshan Pass')}</h3>
            <p className="text-xs text-slate-300 mt-1">
              {t('रांगेत न थांबता थेट दर्शनासाठी पास बुक करा.', 'Book a time slot to skip general queue waiting.')}
            </p>
          </div>

          {bookingSuccess ? (
            <div className="p-3.5 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-bold text-center">
              ✓ {t('तुमचा दर्शन पास यशस्वीरित्या बुक झाला आहे! वेळ: दुपारी ४:०० ते ५:००', 'Darshan Pass Booked for Today 4:00 PM!')}
            </div>
          ) : (
            <button
              onClick={handleBookSlot}
              className="w-full py-2.5 bg-purple-600 hover:bg-purple-500 text-white font-extrabold text-xs rounded-xl shadow-lg transition-all"
            >
              {t('आजचा दर्शन पास मिळवा', 'Get Free E-Pass')}
            </button>
          )}
        </div>

      </div>

    </div>
  );
}
