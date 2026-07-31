"use client";

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { HeartHandshake, Package, Plus, Droplets, UtensilsCrossed, AlertTriangle, MapPin, CheckCircle2, Phone } from 'lucide-react';
import { ngoService } from '@/lib/api';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';

export default function NGOSupplyChainPage() {
  const { audienceRole, t } = useAccessibility();
  const isPilgrimMode = audienceRole === 'PILGRIM' || audienceRole === 'VOLUNTEER';

  const [tankers, setTankers] = useState<any[]>([]);
  const [statusMsg, setStatusMsg] = useState('');

  useEffect(() => {
    ngoService.getWaterTankers().then(res => {
      const data = Array.isArray(res.data) ? res.data : res.data.results || [];
      if (data.length > 0) setTankers(data);
      else setDemoTankers();
    }).catch(() => setDemoTankers());
  }, []);

  const setDemoTankers = () => {
    setTankers([
      { id: '1', name: 'पाणी टँकर #WT-01', location: 'सासवड रस्ता', capacity: '४०,००० लि.', status: 'सक्रिय' },
      { id: '2', name: 'पाणी टँकर #WT-02', location: 'जेजुरी चौक', capacity: '६०,००० लि.', status: 'सक्रिय' },
      { id: '3', name: 'अन्नछत्र #FC-05 (इस्कॉन)', location: 'लोणंद विसावा', capacity: '५,००० जेवण', status: 'कार्यरत' },
    ]);
  };

  const handleDispatch = () => {
    setStatusMsg(t('नवीन अन्न व पाणी गाडी रवाना झाली!', 'Relief Truck Dispatched Successfully!', 'राहत ट्रक रवाना हुआ!'));
    setTimeout(() => setStatusMsg(''), 4000);
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 rounded-3xl bg-[#131B2E] border border-pink-500/40 shadow-2xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-pink-500/20 border border-pink-500/40 flex items-center justify-center text-pink-400">
            <HeartHandshake size={28} />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-white">
              {t('अन्न, पाणी व निवारा सेवा (NGO Relief)', 'NGO Relief Camps & Supply Chain')}
            </h1>
            <p className="text-xs text-slate-300 font-medium">
              {t('मोफत महाप्रसाद, पाणी टँकर व निवारा केंद्रे', 'Free food camps, water tankers, and night shelters')}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {statusMsg && <span className="text-pink-400 font-extrabold text-xs bg-pink-500/20 px-3 py-1.5 rounded-xl border border-pink-500/40 animate-pulse">{statusMsg}</span>}
          {!isPilgrimMode && (
            <button onClick={handleDispatch} className="px-4 py-2.5 bg-pink-600 hover:bg-pink-500 text-white font-extrabold text-xs rounded-xl shadow-lg flex items-center gap-2 transition-all">
              <Plus size={16} />
              <span>{t('नवीन मदत गाडी रवाना करा', 'Dispatch Relief Truck')}</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Food Camps Card */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-pink-500/30 space-y-4 shadow-xl">
          <div className="flex justify-between items-center pb-3 border-b border-white/10">
            <h3 className="font-extrabold text-white text-base flex items-center gap-2">
              <UtensilsCrossed className="text-pink-400" size={20} />
              <span>{t('मोफत अन्नछत्र (Food Camps)', 'Free Food Camps')}</span>
            </h3>
            <span className="px-2.5 py-0.5 rounded bg-pink-500/20 text-pink-300 font-extrabold text-[10px]">
              ८५+ KITCHENS
            </span>
          </div>
          <p className="text-xs text-slate-300">
            {t('सकाळी नाश्ता, दुपारी व रात्री मोफत महाप्रसाद वाटप.', 'Free breakfast, lunch, and dinner thalis served 24x7.')}
          </p>
          <div className="p-3 rounded-xl bg-pink-500/10 border border-pink-500/20 text-xs font-bold text-pink-300">
            ✓ आज १५०,०००+ वारकऱ्यांना महाप्रसाद वाटप पूर्ण
          </div>
        </div>

        {/* Water Tanker Tracking */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-blue-500/30 space-y-4 shadow-xl">
          <div className="flex justify-between items-center pb-3 border-b border-white/10">
            <h3 className="font-extrabold text-white text-base flex items-center gap-2">
              <Droplets className="text-blue-400" size={20} />
              <span>{t('पाणी टँकर ट्रॅकिंग (Water Tankers)', 'Water Tanker Fleet')}</span>
            </h3>
            <span className="px-2.5 py-0.5 rounded bg-blue-500/20 text-blue-300 font-extrabold text-[10px]">
              १२०+ TANKERS
            </span>
          </div>
          <p className="text-xs text-slate-300">
            {t('पालखी मार्गावर फिरते पाणी टँकर थेट ट्रॅकिंग.', 'Live tracking of drinking water tankers along the Palkhi route.')}
          </p>
          <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs font-bold text-blue-300">
            ✓ सर्व पाणी टँकर साठा १००% पूर्ण
          </div>
        </div>

        {/* Shelter Capacity */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-purple-500/30 space-y-4 shadow-xl">
          <div className="flex justify-between items-center pb-3 border-b border-white/10">
            <h3 className="font-extrabold text-white text-base flex items-center gap-2">
              <Package className="text-purple-400" size={20} />
              <span>{t('विश्रांती गृह व निवारा (Night Shelters)', 'Night Shelters')}</span>
            </h3>
            <span className="px-2.5 py-0.5 rounded bg-purple-500/20 text-purple-300 font-extrabold text-[10px]">
              ४५+ SHELTERS
            </span>
          </div>
          <p className="text-xs text-slate-300">
            {t('महिला व वृद्धांसाठी स्वतंत्र सुरक्षित निवारा व्यवस्था.', 'Safe night stay shelters with washrooms and security for women & elderly.')}
          </p>
          <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-xs font-bold text-purple-300">
            ✓ ३,५०० बेड सध्या उपलब्ध आहेत
          </div>
        </div>

      </div>

    </div>
  );
}
