"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, MapPin, Search, Clock, CheckCircle2, Activity, Shield } from 'lucide-react';
import GoogleMapContainer from '@/components/maps/GoogleMapContainer';
import { sosService } from '@/lib/api';

export default function SOSDashboard() {
  const [incidents, setIncidents] = useState<any[]>([]);

  useEffect(() => {
    // Attempt API fetch with fallback to demo SOS records
    sosService.getActiveIncidents()
      .then(res => {
        if (res.data && Array.isArray(res.data)) {
          setIncidents(res.data);
        }
      })
      .catch(() => {
        // Default demo SOS data
        setIncidents([
          { id: 'SOS-1001', severity: 'CRITICAL', incident_type: 'Medical Emergency', latitude: 18.3444, longitude: 74.0305, location: 'Dive Ghat Slope Corridor', timeAgo: '2m ago', assigned: false },
          { id: 'SOS-1002', severity: 'HIGH', incident_type: 'Heatstroke / Fainting', latitude: 18.5204, longitude: 73.8567, location: 'Pune Sector 2 Checkpoint', timeAgo: '12m ago', assigned: true },
        ]);
      });

    // Connect to Django Channels WebSocket if available
    try {
      const ws = new WebSocket('ws://localhost:8000/ws/sos/');
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'new_incident') {
          setIncidents(prev => [data.incident, ...prev]);
        }
      };
      return () => ws.close();
    } catch (e) {}
  }, []);

  return (
    <div className="relative w-full h-[calc(100vh-4rem)] overflow-hidden bg-[#05080F]">
      {/* MAP BACKDROP */}
      <GoogleMapContainer activeRole="Emergency SOS Console" />

      {/* TOP HEADER OVERLAY */}
      <div className="absolute top-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-4 pointer-events-none">
        <div className="pointer-events-auto bg-[#0F1420]/90 backdrop-blur-2xl border border-red-500/40 px-4 py-2.5 rounded-2xl shadow-2xl flex items-center gap-3.5 max-w-full">
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

        <div className="pointer-events-auto">
          <button className="px-4 py-2.5 bg-red-600 hover:bg-red-500 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-red-500/40 transition-all flex items-center gap-2 active:scale-95">
            <AlertTriangle size={16} />
            <span>Broadcast Emergency Alert</span>
          </button>
        </div>
      </div>

      {/* RIGHT SIDE DRAWER: Live SOS Incident Feed */}
      <div className="absolute top-20 right-4 bottom-6 z-20 w-80 sm:w-96 bg-[#0B0F19]/95 backdrop-blur-2xl border border-red-500/30 p-4 rounded-3xl shadow-2xl flex flex-col space-y-3">
        <div className="flex justify-between items-center pb-3 border-b border-white/10">
          <h3 className="font-extrabold text-white text-xs flex items-center gap-2">
            <Activity className="text-red-500" size={16} />
            Live SOS Incident Feed (प्रत्यक्ष आणीबाणी)
          </h3>
          <span className="px-2 py-0.5 bg-red-500/20 text-red-400 text-[10px] font-extrabold rounded-full border border-red-500/30">
            {incidents.length} ACTIVE
          </span>
        </div>

        <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
          <AnimatePresence mode="popLayout">
            {incidents.map((inc: any, i: number) => (
              <motion.div 
                layout
                initial={{ opacity: 0, scale: 0.95, y: -10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.2 }}
                key={inc.id || i} 
                className="p-3.5 rounded-2xl border border-red-500/40 bg-red-500/10 text-slate-200 space-y-2 shadow-lg"
              >
                <div className="flex justify-between items-start">
                  <span className="px-2 py-0.5 bg-red-500 text-white text-[9px] font-extrabold rounded uppercase">
                    {inc.severity || 'CRITICAL'} • {inc.incident_type || 'SOS Alert'}
                  </span>
                  <span className="text-[10px] text-red-300 font-bold flex items-center gap-1">
                    <Clock size={11} /> {inc.timeAgo || 'Just now'}
                  </span>
                </div>
                <div>
                  <h4 className="font-bold text-white text-xs">Incident #{inc.id}</h4>
                  <p className="text-[11px] text-slate-300 mt-0.5 flex items-center gap-1">
                    <MapPin size={12} className="text-red-400" /> {inc.location || `GPS: ${inc.latitude}, ${inc.longitude}`}
                  </p>
                </div>
                <div className="pt-2 border-t border-red-500/20 flex justify-between items-center text-xs">
                  <span className="text-[10px] text-red-300 font-bold">
                    {inc.assigned ? 'Unit Dispatched' : 'Unassigned'}
                  </span>
                  <button className="text-[10px] bg-red-600 hover:bg-red-500 text-white px-3 py-1 rounded-lg font-bold transition-colors shadow">
                    Dispatch Responder
                  </button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
