"use client";

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import { AlertTriangle, MapPin, Search, Clock, CheckCircle2, Activity, Shield } from 'lucide-react';
import { sosService } from '@/lib/api';
import { sosIncidentSocket } from '@/lib/ws_client';
import dynamic from 'next/dynamic';
import { useVirtualizer } from '@tanstack/react-virtual';

const GoogleMapContainer = dynamic(() => import('@/components/maps/GoogleMapContainer'), { ssr: false });

export default function SOSDashboard() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [latestIncident, setLatestIncident] = useState<any>(null);
  const [selectedIncident, setSelectedIncident] = useState<any>(null);
  const [highContrast, setHighContrast] = useState(false);
  const [isFrozen, setIsFrozen] = useState(false);
  
  const shouldReduceMotion = useReducedMotion();
  const parentRef = useRef<HTMLDivElement>(null);
  const queuedIncidents = useRef<any[]>([]);
  const isFrozenRef = useRef(false);

  const toggleFreeze = () => {
    if (isFrozen) {
      // Unfreeze: flush queued incidents
      setIsFrozen(false);
      isFrozenRef.current = false;
      if (queuedIncidents.current.length > 0) {
        setIncidents(prev => {
          const newIncidents = [...queuedIncidents.current, ...prev].slice(0, 500);
          queuedIncidents.current = [];
          return newIncidents;
        });
      }
    } else {
      setIsFrozen(true);
      isFrozenRef.current = true;
    }
  };

  const virtualizer = useVirtualizer({
    count: incidents.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 140, // Estimated pixel height of each incident card
    overscan: 5,
  });

  const handleResolve = async (id: string) => {
    try {
      await sosService.updateStatus(id, 'RESOLVED');
    } catch (_) {}
    setIncidents(prev => prev.filter(item => item.id !== id));
  };

  useEffect(() => {
    // Attempt API fetch with fallback to demo SOS records
    sosService.getActiveIncidents()
      .then(res => {
        const data = Array.isArray(res.data) ? res.data : res.data.results || [];
        if (data.length > 0) {
          setIncidents(data);
        } else {
          setIncidents([
            { id: 'SOS-1001', severity: 'CRITICAL', incident_type: 'Medical Emergency', latitude: 18.3444, longitude: 74.0305, location: 'Dive Ghat Slope Corridor', timeAgo: '2m ago', assigned: false },
            { id: 'SOS-1002', severity: 'HIGH', incident_type: 'Heatstroke / Fainting', latitude: 18.5204, longitude: 73.8567, location: 'Pune Sector 2 Checkpoint', timeAgo: '12m ago', assigned: true },
          ]);
        }
      })
      .catch(() => {
        setIncidents([
          { id: 'SOS-1001', severity: 'CRITICAL', incident_type: 'Medical Emergency', latitude: 18.3444, longitude: 74.0305, location: 'Dive Ghat Slope Corridor', timeAgo: '2m ago', assigned: false },
          { id: 'SOS-1002', severity: 'HIGH', incident_type: 'Heatstroke / Fainting', latitude: 18.5204, longitude: 73.8567, location: 'Pune Sector 2 Checkpoint', timeAgo: '12m ago', assigned: true },
        ]);
      });

    // Connect to Django Channels WebSocket using robust client
    sosIncidentSocket.connect();
    
    const unsubscribe = sosIncidentSocket.subscribe((data: any) => {
      if (data.type === 'new_incident') {
        setLatestIncident(data.incident);
        if (isFrozenRef.current) {
          queuedIncidents.current = [data.incident, ...queuedIncidents.current];
        } else {
          setIncidents(prev => {
            const newIncidents = [data.incident, ...prev];
            return newIncidents.slice(0, 500);
          });
        }
      }
    });

    return () => {
      unsubscribe();
      sosIncidentSocket.disconnect();
    };
  }, []);

  return (
    <div className={`relative w-full h-[calc(100vh-4rem)] overflow-hidden ${highContrast ? 'bg-black' : 'bg-[#05080F]'}`}>
      {/* Visually hidden aria-live region for screen readers */}
      <div className="sr-only" aria-live="assertive" aria-atomic="true">
        {latestIncident ? `New Emergency: ${latestIncident.incident_type} at ${latestIncident.location}` : ''}
      </div>

      {/* MAP BACKDROP */}
      <GoogleMapContainer activeRole="Emergency SOS Console" />

      {/* TOP HEADER OVERLAY */}
      <div className="absolute top-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-4 pointer-events-none">
        <div className={`pointer-events-auto px-4 py-2.5 rounded-2xl flex items-center gap-3.5 max-w-full ${
          highContrast ? 'bg-black border-2 border-white shadow-none' : 'bg-[#0F1420]/90 backdrop-blur-2xl border border-red-500/40 shadow-2xl'
        }`}>
          <div className="p-2 bg-red-500/20 text-red-400 rounded-xl">
            <AlertTriangle size={20} className="animate-pulse" />
          </div>
          <div>
            <p className="text-white font-extrabold text-xs tracking-tight flex items-center gap-2">
              <span>आणीबाणी SOS ऑपरेशन्स (EMERGENCY SOS)</span>
              <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
            </p>
            <p className="text-slate-400 text-[10px]">
              {incidents.length} Active Emergencies • Live Responder Dispatch Center
            </p>
          </div>
        </div>

        <div className="pointer-events-auto flex items-center gap-2">
          <button 
            onClick={() => setHighContrast(!highContrast)}
            className="px-3 py-2.5 bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs rounded-xl shadow transition-all border border-slate-600"
            aria-label="Toggle High Contrast Mode"
          >
            {highContrast ? 'Disable High Contrast' : 'High Contrast'}
          </button>
          <button className="px-4 py-2.5 bg-red-600 hover:bg-red-500 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-red-500/40 transition-all flex items-center gap-2 active:scale-95">
            <AlertTriangle size={16} />
            <span>Broadcast Emergency Alert</span>
          </button>
        </div>
      </div>

      {/* RIGHT SIDE DRAWER: Live SOS Incident Feed */}
      <div className={`absolute top-20 right-4 bottom-6 z-20 w-80 sm:w-96 p-4 rounded-3xl flex flex-col space-y-3 ${
        highContrast ? 'bg-black border-2 border-white shadow-none' : 'bg-[#0B0F19]/95 backdrop-blur-2xl border border-red-500/30 shadow-2xl'
      }`}>
        <div className="flex justify-between items-center pb-3 border-b border-white/10">
          <h3 className="font-extrabold text-white text-xs flex items-center gap-2">
            <Activity className="text-red-500" size={16} />
            Live SOS Incident Feed (प्रत्यक्ष आणीबाणी)
          </h3>
          <div className="flex items-center gap-2">
            <button 
              onClick={toggleFreeze}
              className={`px-2 py-1 text-[10px] font-bold rounded-lg border transition-colors ${
                isFrozen 
                  ? 'bg-orange-500 text-white border-orange-400 animate-pulse shadow-[0_0_10px_rgba(249,115,22,0.5)]' 
                  : 'bg-transparent text-slate-300 border-slate-600 hover:bg-slate-800'
              }`}
            >
              {isFrozen ? `Unfreeze (${queuedIncidents.current.length} Queued)` : 'Freeze Feed'}
            </button>
            <span className="px-2 py-0.5 bg-red-500/20 text-red-400 text-[10px] font-extrabold rounded-full border border-red-500/30">
              {incidents.length} ACTIVE
            </span>
          </div>
        </div>

        <div 
          ref={parentRef}
          className="flex-1 overflow-y-auto space-y-2.5 pr-1"
        >
          <div
            style={{
              height: `${virtualizer.getTotalSize()}px`,
              width: '100%',
              position: 'relative',
            }}
          >
            <AnimatePresence>
              {virtualizer.getVirtualItems().map((virtualItem) => {
                const inc = incidents[virtualItem.index];
                return (
                  <motion.div 
                    initial={{ opacity: 0, scale: shouldReduceMotion ? 1 : 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: shouldReduceMotion ? 1 : 0.9 }}
                    transition={{ duration: shouldReduceMotion ? 0 : 0.2 }}
                    key={inc.id || virtualItem.index} 
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      transform: `translateY(${virtualItem.start}px)`,
                    }}
                    className={`p-3.5 rounded-2xl space-y-2 mb-2.5 cursor-pointer transition-all active:scale-95 ${
                      highContrast 
                        ? 'border-2 border-red-500 bg-black text-white hover:bg-red-900/50' 
                        : 'border border-red-500/40 bg-red-500/10 text-slate-200 shadow-lg hover:bg-red-500/20'
                    }`}
                    onClick={() => setSelectedIncident(inc)}
                  >
                    <div className="flex justify-between items-start">
                      <span className="px-3 py-1 bg-red-500 text-white text-[10px] font-extrabold rounded uppercase">
                        {inc.severity || 'CRITICAL'}
                      </span>
                      <span className="text-[10px] text-red-300 font-bold flex items-center gap-1">
                        <Clock size={12} /> {inc.timeAgo || 'Just now'}
                      </span>
                    </div>
                    <div>
                      <h4 className="font-bold text-white text-sm">{inc.incident_type || 'SOS Alert'}</h4>
                      <p className="text-xs text-slate-300 mt-1 flex items-center gap-1 truncate">
                        <MapPin size={12} className="text-red-400 shrink-0" /> {inc.location || `GPS: ${inc.latitude}, ${inc.longitude}`}
                      </p>
                    </div>
                    <div className="pt-2 mt-2 border-t border-red-500/20 text-center">
                      <span className="text-[11px] text-red-400 font-bold w-full block py-1">
                        Tap for Details & Dispatch
                      </span>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* INCIDENT DETAILS MODAL */}
      <AnimatePresence>
        {selectedIncident && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
            <motion.div 
              initial={{ opacity: 0, scale: shouldReduceMotion ? 1 : 0.9, y: shouldReduceMotion ? 0 : 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: shouldReduceMotion ? 1 : 0.9, y: shouldReduceMotion ? 0 : 20 }}
              className={`w-full max-w-md p-6 rounded-3xl shadow-2xl flex flex-col gap-4 ${
                highContrast ? 'bg-black border-2 border-white' : 'bg-[#0B0F19] border border-red-500/40'
              }`}
            >
              <div className="flex justify-between items-center border-b border-white/10 pb-4">
                <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
                  <AlertTriangle className="text-red-500" />
                  Incident Details
                </h2>
                <button 
                  onClick={() => setSelectedIncident(null)}
                  className="w-11 h-11 bg-white/10 hover:bg-white/20 rounded-full text-white font-bold flex items-center justify-center transition-colors"
                  aria-label="Close modal"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-3 text-sm text-slate-300">
                <p className="flex justify-between border-b border-white/5 pb-2">
                  <strong className="text-white">ID:</strong> 
                  <span>{selectedIncident.id}</span>
                </p>
                <p className="flex justify-between border-b border-white/5 pb-2">
                  <strong className="text-white">Type:</strong> 
                  <span className="font-bold text-red-300">{selectedIncident.incident_type || 'SOS Alert'}</span>
                </p>
                <p className="flex justify-between border-b border-white/5 pb-2">
                  <strong className="text-white">Severity:</strong> 
                  <span className="text-red-500 font-extrabold bg-red-500/20 px-2 py-0.5 rounded">{selectedIncident.severity || 'CRITICAL'}</span>
                </p>
                <p className="flex flex-col gap-1 border-b border-white/5 pb-2">
                  <strong className="text-white">Location:</strong> 
                  <span className="text-xs">{selectedIncident.location}</span>
                </p>
                <p className="flex justify-between border-b border-white/5 pb-2">
                  <strong className="text-white">Coordinates:</strong> 
                  <span className="text-xs font-mono">{selectedIncident.latitude}, {selectedIncident.longitude}</span>
                </p>
                <p className="flex justify-between border-b border-white/5 pb-2">
                  <strong className="text-white">Time:</strong> 
                  <span>{selectedIncident.timeAgo || 'Just now'}</span>
                </p>
                <p className="flex justify-between pb-2">
                  <strong className="text-white">Status:</strong> 
                  <span className={selectedIncident.assigned ? 'text-green-400' : 'text-orange-400 font-bold'}>
                    {selectedIncident.assigned ? 'Unit Dispatched' : 'Unassigned'}
                  </span>
                </p>
              </div>

              <div className="mt-4 flex gap-3">
                <button 
                  onClick={() => setSelectedIncident(null)}
                  className="flex-1 min-h-[44px] bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-xl transition-colors"
                >
                  Close
                </button>
                <button className="flex-1 min-h-[44px] bg-red-600 hover:bg-red-500 text-white font-extrabold rounded-xl shadow-lg transition-all active:scale-95">
                  Dispatch Responder
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
