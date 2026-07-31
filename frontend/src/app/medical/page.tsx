"use client";

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Stethoscope, Plus, Clock, HeartPulse, Syringe, BedDouble, Phone, CheckCircle2, MapPin, ArrowRight } from 'lucide-react';
import { medicalService } from '@/lib/api';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';

export default function MedicalOperationsPage() {
  const { audienceRole, t } = useAccessibility();
  const isPilgrimMode = audienceRole === 'PILGRIM' || audienceRole === 'VOLUNTEER';

  const [camps, setCamps] = useState<any[]>([]);
  const [ambulances, setAmbulances] = useState<any[]>([]);
  const [dispatching, setDispatching] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');

  useEffect(() => {
    medicalService.getCamps().then(res => {
      const data = Array.isArray(res.data) ? res.data : res.data.results || [];
      if (data.length > 0) setCamps(data);
      else setDemoData();
    }).catch(() => setDemoData());
  }, []);

  const setDemoData = () => {
    setCamps([
      { id: '1', name: 'Health Camp Alpha (सासवड)', doctors: 4, beds: 15, location: 'Saswad Sector 2', phone: '020-24551122' },
      { id: '2', name: 'Health Camp Beta (लोणंद)', doctors: 6, beds: 20, location: 'Lonand Palkhi Stop', phone: '02169-224411' },
      { id: '3', name: 'Pandharpur Temple ICU Unit', doctors: 12, beds: 45, location: 'Near Temple Gate 1', phone: '02186-223344' },
    ]);
  };

  const handleDispatch = async () => {
    setDispatching(true);
    setStatusMsg(t('रुग्णवाहिका रवाना होत आहे...', 'Dispatching Ambulance...', 'एम्बुलेंस भेजी जा रही है...'));
    setTimeout(() => {
      setDispatching(false);
      setStatusMsg(t('रुग्णवाहिका MH12-WM-1001 तत्काळ रवाना झाली!', 'Ambulance MH12-WM-1001 Dispatched!', 'एम्बुलेंस MH12-WM-1001 रवाना हो गई!'));
      setTimeout(() => setStatusMsg(''), 4000);
    }, 1500);
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 rounded-3xl bg-[#131B2E] border border-emerald-500/40 shadow-2xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
            <Activity size={28} />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-white">
              {t('वैद्यकीय मदत व रुग्णवाहिका (Medical Ops)', 'Medical Operations & Health Camps')}
            </h1>
            <p className="text-xs text-slate-300 font-medium">
              {t('मोफत औषधे, रुग्णवाहिका आणि आरोग्य शिबीर सेवा', '24x7 Free medical treatment, health camps, and ambulances')}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {statusMsg && <span className="text-emerald-400 font-extrabold text-xs bg-emerald-500/20 px-3 py-1.5 rounded-xl border border-emerald-500/40 animate-pulse">{statusMsg}</span>}
          <a href="tel:108" className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl shadow-lg flex items-center gap-2 transition-all">
            <Phone size={16} />
            <span>{t('१०८ रुग्णवाहिका कॉल', 'Call 108 Ambulance')}</span>
          </a>
        </div>
      </div>

      {/* PILGRIM / DEVOTEE MODE: Easy Medical Locators */}
      {isPilgrimMode ? (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-base sm:text-lg font-bold text-white flex items-center gap-2">
              <Stethoscope className="text-emerald-400" size={20} />
              <span>{t('उपलब्ध मोफत आरोग्य शिबीरे (Free Health Camps Nearby)', 'Available Free Health Camps')}</span>
            </h2>
            <span className="text-xs text-emerald-400 font-bold bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/30">
              {camps.length} {t('शिबीरे मोकळी आहेत', 'Camps Active')}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {camps.map((c) => (
              <div key={c.id} className="p-5 rounded-3xl bg-[#131B2E] border border-emerald-500/30 space-y-3 shadow-xl hover:border-emerald-400 transition-all">
                <div className="flex justify-between items-start">
                  <span className="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-extrabold border border-emerald-500/40">
                    {t('मोफत उपचार', 'FREE CARE')}
                  </span>
                  <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
                    <BedDouble size={14} className="text-emerald-400" /> {c.beds} Beds
                  </span>
                </div>

                <div>
                  <h3 className="font-black text-white text-base">{c.name}</h3>
                  <p className="text-xs text-slate-300 mt-1 flex items-center gap-1">
                    <MapPin size={14} className="text-emerald-400 shrink-0" /> {c.location}
                  </p>
                </div>

                <div className="pt-3 border-t border-white/10 flex items-center justify-between text-xs">
                  <span className="text-slate-300 font-bold">डॉक्टर: {c.doctors} उपस्थित</span>
                  <a href={`tel:${c.phone}`} className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold rounded-lg transition-colors flex items-center gap-1">
                    <Phone size={12} /> Call
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        
        /* OPERATIONAL / DOCTOR MODE: Triage Queue & Ambulance Console */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 p-6 rounded-3xl bg-[#131B2E] border border-white/10 shadow-2xl space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-white/10">
              <h3 className="font-extrabold text-white text-sm flex items-center gap-2">
                <HeartPulse className="text-red-400" size={18} />
                <span>{t('रुग्ण ट्रायज आणि आणीबाणी केसेस (Patient Triage Queue)', 'Patient Triage Queue')}</span>
              </h3>
              <button onClick={handleDispatch} disabled={dispatching} className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl shadow transition-all flex items-center gap-1.5">
                <Plus size={14} />
                <span>{dispatching ? 'Dispatching...' : 'Dispatch Ambulance'}</span>
              </button>
            </div>

            <div className="space-y-3">
              <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30 space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold text-white flex items-center gap-2">
                    <Activity size={16} className="text-red-400" />
                    रमेश जाधव (वय ६२ वर्ष) — तीव्र उष्माघात (Heatstroke)
                  </span>
                  <span className="px-2 py-0.5 rounded bg-red-600 text-white font-extrabold text-[10px]">HIGH PRIORITY</span>
                </div>
                <p className="text-xs text-slate-300">स्थान: वाखारी पालखी थांबा • रुग्णवाहिका MH12-WM-1001 रवाना (ETA: ३ मिनिटे)</p>
              </div>

              <div className="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/30 space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold text-white flex items-center gap-2">
                    <Activity size={16} className="text-blue-400" />
                    सुनीता शिंदे (वय ४५ वर्ष) — पायाचे फोड व थकवा
                  </span>
                  <span className="px-2 py-0.5 rounded bg-blue-600 text-white font-extrabold text-[10px]">NORMAL</span>
                </div>
                <p className="text-xs text-slate-300">स्थान: सासवड आरोग्य शिबीर Alpha • मलम व प्राथमिक उपचार पूर्ण</p>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-3xl bg-[#131B2E] border border-white/10 shadow-2xl space-y-4">
            <h3 className="font-extrabold text-sm text-white flex items-center gap-2">
              <Syringe className="text-emerald-400" size={18} />
              <span>{t('औषध साठा स्थिती (Medicine Stock)', 'Medicine Inventory')}</span>
            </h3>
            <div className="space-y-2.5 text-xs">
              <div className="p-3 rounded-xl bg-[#0B0F19] flex justify-between items-center">
                <span className="text-white font-bold">ORS पॅकेट्स</span>
                <span className="text-emerald-400 font-mono font-extrabold">१२,५०० units</span>
              </div>
              <div className="p-3 rounded-xl bg-[#0B0F19] flex justify-between items-center">
                <span className="text-white font-bold">पेनकिलर व बँडेज</span>
                <span className="text-emerald-400 font-mono font-extrabold">८,२०० kits</span>
              </div>
              <div className="p-3 rounded-xl bg-[#0B0F19] flex justify-between items-center">
                <span className="text-white font-bold">सलाईन बॉटल्स (IV Fluids)</span>
                <span className="text-amber-400 font-mono font-extrabold">४५० remaining</span>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
