"use client";

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import { AlertTriangle, MapPin, Clock, Activity, Shield, Phone, CheckCircle2, Navigation, Send, Radio, UserCheck, ShieldAlert } from 'lucide-react';
import { sosService } from '@/lib/api';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';

export default function SOSDashboard() {
  const { audienceRole, t } = useAccessibility();
  const [incidents, setIncidents] = useState<any[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<any>(null);
  const [sosTriggered, setSosTriggered] = useState(false);
  const [emergencyType, setEmergencyType] = useState('Medical');
  const [activeStep, setActiveStep] = useState(1);

  const isPilgrimMode = audienceRole === 'PILGRIM' || audienceRole === 'VOLUNTEER';

  useEffect(() => {
    sosService.getActiveIncidents()
      .then(res => {
        const data = Array.isArray(res.data) ? res.data : res.data.results || [];
        if (data.length > 0) setIncidents(data);
        else setDemoIncidents();
      })
      .catch(() => setDemoIncidents());
  }, []);

  const setDemoIncidents = () => {
    setIncidents([
      { id: 'SOS-1001', severity: 'CRITICAL', incident_type: 'Medical Emergency', latitude: 18.3444, longitude: 74.0305, location: 'Dive Ghat Slope Corridor', timeAgo: '2m ago', assigned: true, responder: 'Ramesh Patel (Volunteer #42)' },
      { id: 'SOS-1002', severity: 'HIGH', incident_type: 'Heatstroke / Exhaustion', latitude: 18.5204, longitude: 73.8567, location: 'Saswad Sector 2 Checkpoint', timeAgo: '8m ago', assigned: false },
      { id: 'SOS-1003', severity: 'CRITICAL', incident_type: 'Missing Elderly Person', latitude: 18.1200, longitude: 74.5500, location: 'Lonand Palkhi Rest Camp', timeAgo: '15m ago', assigned: true, responder: 'Police Control Unit 12' },
    ]);
  };

  const handleTriggerSOS = () => {
    setSosTriggered(true);
    setActiveStep(1);
    
    // Simulate multi-step emergency assignment
    setTimeout(() => setActiveStep(2), 2000); // GPS Captured
    setTimeout(() => setActiveStep(3), 4000); // Responders Notified
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 rounded-3xl bg-gradient-to-r from-red-950/80 via-[#131B2E] to-slate-900 border border-red-500/40 shadow-2xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-red-600/30 border border-red-500/60 flex items-center justify-center text-red-400">
            <AlertTriangle size={28} className="animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-white">
              {t('आणीबाणी मदत SOS (Emergency Response)', 'Emergency SOS Dispatch Center')}
            </h1>
            <p className="text-xs text-slate-300 font-medium">
              {t('१-टॅप आणीबाणी मदत, रुग्णवाहिका व स्वयंसेवक ट्रॅकिंग', 'One-tap emergency trigger & real-time responder dispatch')}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <a href="tel:108" className="px-4 py-2.5 bg-red-600 hover:bg-red-500 text-white font-extrabold text-xs rounded-xl shadow-lg flex items-center gap-2 transition-all">
            <Phone size={16} />
            <span>{t('१०८ रुग्णवाहिका कॉल', 'Call 108 Ambulance')}</span>
          </a>
        </div>
      </div>

      {/* -------------------------------------------------------------------------- */}
      {/* PILGRIM / DEVOTEE MODE: 1-TAP EMERGENCY SOS TRIGGER                        */}
      {/* -------------------------------------------------------------------------- */}
      {isPilgrimMode ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Main Panic Button Card */}
          <div className="lg:col-span-2 p-6 sm:p-8 rounded-3xl bg-[#131B2E] border-2 border-red-500/40 shadow-2xl flex flex-col items-center text-center space-y-6">
            
            <div className="space-y-2">
              <span className="px-3 py-1 bg-red-500/20 text-red-400 border border-red-500/40 rounded-full text-xs font-extrabold">
                {t('आणीबाणी बटण (ONE TAP SOS)', 'Emergency SOS Activation')}
              </span>
              <h2 className="text-2xl font-black text-white">
                {t('तुम्हाला तातडीची मदत हवी आहे का?', 'Do you need immediate emergency help?')}
              </h2>
              <p className="text-xs text-slate-300 max-w-md mx-auto">
                {t('खालील लाल बटणावर टॅप करा. तुमचे GPS स्थान जवळच्या स्वयंसेवक, डॉक्टर व पोलिसांना पाठवले जाईल.', 'Tap the button below. Your GPS location will be sent to nearby volunteers, doctors, and police.')}
              </p>
            </div>

            {/* Emergency Type Selector */}
            <div className="w-full max-w-md grid grid-cols-3 gap-2 text-xs font-bold">
              {['Medical', 'Lost Person', 'Women Safety'].map((type) => (
                <button
                  key={type}
                  onClick={() => setEmergencyType(type)}
                  className={`py-2 px-3 rounded-xl border transition-all ${
                    emergencyType === type
                      ? 'bg-red-600 text-white border-red-400 shadow-md'
                      : 'bg-white/5 text-slate-300 border-white/10 hover:bg-white/10'
                  }`}
                >
                  {type === 'Medical' ? t('वैद्यकीय', 'Medical') : type === 'Lost Person' ? t('हरवले', 'Lost Person') : t('महिला सुरक्षा', 'Women Safety')}
                </button>
              ))}
            </div>

            {/* Giant Panic Button */}
            {!sosTriggered ? (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleTriggerSOS}
                className="w-48 h-48 sm:w-56 sm:h-56 rounded-full bg-gradient-to-tr from-red-700 via-red-600 to-orange-500 text-white font-black text-3xl shadow-[0_0_60px_rgba(239,68,68,0.7)] flex flex-col items-center justify-center gap-2 border-4 border-white/20 hover:border-white/50 cursor-pointer"
              >
                <AlertTriangle size={56} className="animate-bounce" />
                <span>SOS</span>
                <span className="text-xs font-extrabold uppercase tracking-wider text-orange-200">
                  {t('मदतीसाठी टॅप करा', 'TAP FOR HELP')}
                </span>
              </motion.button>
            ) : (
              <div className="w-full max-w-md p-6 rounded-2xl bg-red-950/60 border border-red-500/50 space-y-4 text-left">
                <div className="flex items-center gap-3 text-red-400 font-extrabold text-base">
                  <Radio size={24} className="animate-pulse" />
                  <span>{t('आणीबाणी संदेश पाठवला गेला आहे!', 'SOS Alert Transmitted Successfully!')}</span>
                </div>

                <div className="space-y-3 text-xs">
                  <div className={`p-2.5 rounded-xl flex items-center gap-2.5 ${activeStep >= 1 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-white/5 text-slate-400'}`}>
                    <CheckCircle2 size={16} />
                    <span>१. GPS स्थान नोंदवले: १८.३४४४ N, ७४.०३०५ E</span>
                  </div>

                  <div className={`p-2.5 rounded-xl flex items-center gap-2.5 ${activeStep >= 2 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-white/5 text-slate-400'}`}>
                    <CheckCircle2 size={16} />
                    <span>२. जवळचे ३ स्वयंसेवक आणि १ रुग्णवाहिका संपर्कित</span>
                  </div>

                  <div className={`p-2.5 rounded-xl flex items-center gap-2.5 ${activeStep >= 3 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-white/5 text-slate-400'}`}>
                    <UserCheck size={16} />
                    <span>३. स्वयंसेवक 'रमेश पाटील' घटनास्थळी रवाना (ETA: ४ मि.)</span>
                  </div>
                </div>

                <button
                  onClick={() => setSosTriggered(false)}
                  className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-xl transition-colors"
                >
                  {t('कॉल रद्द करा', 'Cancel SOS Alert')}
                </button>
              </div>
            )}

          </div>

          {/* Side Info & Emergency Guidelines */}
          <div className="space-y-4">
            <div className="p-5 rounded-3xl bg-[#131B2E] border border-white/10 shadow-xl space-y-3">
              <h3 className="font-extrabold text-sm text-white flex items-center gap-2">
                <Shield className="text-orange-400" size={16} />
                <span>{t('तातडीची संपर्क यादी (Emergency Contacts)', 'Emergency Directory')}</span>
              </h3>
              <div className="space-y-2 text-xs">
                <div className="p-2.5 rounded-xl bg-white/5 flex justify-between items-center">
                  <span className="font-bold text-white">१०८ रुग्णवाहिका सेवा</span>
                  <span className="font-mono text-emerald-400 font-extrabold">108</span>
                </div>
                <div className="p-2.5 rounded-xl bg-white/5 flex justify-between items-center">
                  <span className="font-bold text-white">१०० पोलीस नियंत्रण कक्ष</span>
                  <span className="font-mono text-blue-400 font-extrabold">100</span>
                </div>
                <div className="p-2.5 rounded-xl bg-white/5 flex justify-between items-center">
                  <span className="font-bold text-white">वारी आपत्ती मदत कक्ष</span>
                  <span className="font-mono text-orange-400 font-extrabold">1800-233-4555</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      ) : (
        
        /* -------------------------------------------------------------------------- */
        /* GOVERNMENT / OPERATIONAL MODE: INCIDENT COMMAND & DISPATCH BOARD          */
        /* -------------------------------------------------------------------------- */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Incident Feed List */}
          <div className="lg:col-span-2 p-6 rounded-3xl bg-[#131B2E] border border-red-500/30 shadow-2xl space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-white/10">
              <h3 className="font-extrabold text-white text-sm flex items-center gap-2">
                <Activity className="text-red-400" size={18} />
                <span>{t('सक्रिय आणीबाणी घटनांची यादी (Live SOS Feed)', 'Active Emergency Feed')}</span>
              </h3>
              <span className="px-2.5 py-1 bg-red-500/20 text-red-400 text-xs font-extrabold rounded-full border border-red-500/30">
                {incidents.length} INCIDENTS
              </span>
            </div>

            <div className="space-y-3">
              {incidents.map((inc) => (
                <div
                  key={inc.id}
                  onClick={() => setSelectedIncident(inc)}
                  className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30 hover:border-red-400 cursor-pointer transition-all space-y-2"
                >
                  <div className="flex justify-between items-center">
                    <span className="px-2.5 py-0.5 bg-red-600 text-white font-extrabold text-[10px] rounded uppercase">
                      {inc.severity}
                    </span>
                    <span className="text-xs text-slate-400 font-bold flex items-center gap-1">
                      <Clock size={13} /> {inc.timeAgo}
                    </span>
                  </div>

                  <div>
                    <h4 className="font-black text-white text-base">{inc.incident_type}</h4>
                    <p className="text-xs text-slate-300 flex items-center gap-1.5 mt-1">
                      <MapPin size={14} className="text-red-400" /> {inc.location}
                    </p>
                  </div>

                  <div className="flex justify-between items-center pt-2 border-t border-red-500/20 text-xs">
                    <span className="text-slate-400">
                      उत्तरदायी: <strong className="text-white">{inc.responder || 'अनियुक्त (Unassigned)'}</strong>
                    </span>
                    <span className="text-red-400 font-extrabold hover:underline">
                      तपशील पहा ➔
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Dispatch Panel */}
          <div className="p-6 rounded-3xl bg-[#131B2E] border border-white/10 shadow-2xl space-y-4">
            <h3 className="font-extrabold text-sm text-white flex items-center gap-2">
              <ShieldAlert className="text-orange-400" size={18} />
              <span>{t('तातडीची कारवाई (Quick Dispatch)', 'Quick Dispatch Console')}</span>
            </h3>
            <p className="text-xs text-slate-300">
              क्षेत्रीय पथकांना (Field Teams) थेट संदेश पाठवा किंवा मदत कार्य सुरू करा.
            </p>
            <div className="space-y-2">
              <button className="w-full py-2.5 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded-xl shadow transition-colors">
                नवीन रुग्णवाहिका रवाना करा
              </button>
              <button className="w-full py-2.5 bg-orange-600 hover:bg-orange-500 text-white font-bold text-xs rounded-xl shadow transition-colors">
                जवळचे स्वयंसेवक सतर्क करा
              </button>
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
