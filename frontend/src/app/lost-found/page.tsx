"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, QrCode, Plus, UserCheck, AlertTriangle, MapPin, Camera, CheckCircle2, ShieldCheck } from 'lucide-react';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';

export default function LostFoundPage() {
  const { t } = useAccessibility();
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const [items] = useState([
    { id: '1', title: 'अनिश जाधव (वय ८ वर्षे) — लहान मुलगा', category: 'हरवलेले व्यक्ती (Child)', location: 'आळंदी पाणी केंद्र', status: 'शोध मोहीम सुरू', qr_claim_code: 'WM-MISS-99201', time: '१० मिनिटांपूर्वी' },
    { id: '2', title: 'काळया रंगाचे पाकीट व आधार कार्ड', category: 'वस्तू (Wallet / ID)', location: 'सासवड विसावा', status: 'सापडले (FOUND)', qr_claim_code: 'WM-LF-99202', time: '२५ मिनिटांपूर्वी' },
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setReportModalOpen(false);
    }, 3000);
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 rounded-3xl bg-[#131B2E] border border-cyan-500/40 shadow-2xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
            <Search size={28} />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-white">
              {t('हरवलेले व्यक्ती व वस्तू केंद्र (Lost & Found Hub)', 'Lost & Found Center')}
            </h1>
            <p className="text-xs text-slate-300 font-medium">
              {t('हरवलेल्या लहान मुलांचा व ज्येष्ठांचा तात्काळ शोध व क्यूआर पडताळणी', 'Rapid missing person search & QR verification for belongings')}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setReportModalOpen(true)}
            className="px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-cyan-500/30 transition-all flex items-center gap-2"
          >
            <Plus size={16} />
            <span>{t('हरवलेले / सापडलेले नोंदवा', 'Report Lost or Found')}</span>
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Missing Person Search Board */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-cyan-500/30 space-y-4 shadow-xl">
          <div className="flex justify-between items-center pb-3 border-b border-white/10">
            <h3 className="font-extrabold text-white text-base flex items-center gap-2">
              <AlertTriangle className="text-amber-400" size={20} />
              <span>{t('हरवलेले व्यक्ती शोध (Missing Persons Feed)', 'Missing Persons Feed')}</span>
            </h3>
            <span className="px-2.5 py-0.5 rounded bg-red-500/20 text-red-300 font-extrabold text-[10px]">
              १ सक्रिय शोध
            </span>
          </div>

          <div className="space-y-3">
            {items.map(item => (
              <div key={item.id} className="p-4 rounded-2xl bg-[#0B0F19] border border-white/10 space-y-2 text-xs">
                <div className="flex justify-between items-center">
                  <span className="font-black text-white text-sm">{item.title}</span>
                  <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-bold text-[10px]">
                    {item.status}
                  </span>
                </div>
                <p className="text-slate-300">प्रवर्ग: {item.category} • स्थान: {item.location}</p>
                <div className="pt-2 border-t border-white/10 flex justify-between items-center text-slate-400">
                  <span className="font-mono text-cyan-400 font-bold">QR Code: {item.qr_claim_code}</span>
                  <span>{item.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* QR Verification & Claim System */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-white/10 space-y-4 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-start mb-3">
              <span className="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-extrabold text-[10px]">
                क्यूआर कोड पडताळणी (QR CLAIM)
              </span>
              <QrCode className="text-cyan-400" size={20} />
            </div>

            <h3 className="font-black text-white text-lg">{t('सापडलेल्या वस्तूंची खात्रीशीर मालकी', 'QR Verified Claim System')}</h3>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">
              {t('अन्नछत्र किंवा पोलिसांना सापडलेली वस्तू मूळ मालकाला देण्यापूर्वी क्यूआर कोड किंवा ओळखपत्राने अचूक पडताळणी केली जाते.', 'Items found by volunteers are linked with unique QR claim codes for verified handover.')}
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 text-xs font-bold text-cyan-300 space-y-2">
            <p>✓ सर्व हरवलेल्या लहान मुलांची नोंदणी थेट पोलीस वायरलेस कक्षाला पाठवली जाते.</p>
          </div>
        </div>

      </div>

      {/* Report Modal */}
      {reportModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-3xl bg-[#0F172A] border-2 border-cyan-500/40 text-white space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-3 border-b border-white/10">
              <h3 className="font-extrabold text-base">{t('हरवलेल्या व्यक्ती / वस्तूची नोंदणी', 'Report Missing Person / Item')}</h3>
              <button onClick={() => setReportModalOpen(false)} className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">✕</button>
            </div>

            {submitted ? (
              <div className="p-4 rounded-2xl bg-emerald-500/20 text-emerald-300 text-xs font-bold text-center">
                ✓ नोंदणी यशस्वी झाली आहे! शोध पथक सतर्क झाले आहे.
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-3 text-xs">
                <div>
                  <label className="block font-bold text-slate-300 mb-1">नाव / वस्तूचे वर्णन (Name / Description)</label>
                  <input required type="text" placeholder="उदा. अनिश जाधव किंवा काळे पाकीट" className="w-full p-2.5 rounded-xl bg-white/5 border border-white/15 text-white outline-none focus:border-cyan-400" />
                </div>

                <div>
                  <label className="block font-bold text-slate-300 mb-1">हरवलेले स्थान (Last Seen Location)</label>
                  <input required type="text" placeholder="उदा. सासवड पालखी तंबू जवळ" className="w-full p-2.5 rounded-xl bg-white/5 border border-white/15 text-white outline-none focus:border-cyan-400" />
                </div>

                <button type="submit" className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 text-white font-extrabold rounded-xl transition-all shadow">
                  नोंदवा व शोध सुरू करा
                </button>
              </form>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
