"use client";

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { MapPin, AlertTriangle, Activity, Tent, Shield, RefreshCw } from 'lucide-react';

interface MarkerItem {
  id: string;
  name: string;
  lat: number;
  lng: number;
  type: 'medical' | 'sos' | 'queue' | 'police' | 'water';
  status: string;
  details?: string;
}

const DEMO_MAP_MARKERS: MarkerItem[] = [
  { id: '1', name: 'Camp Alpha — Alandi Chowk', lat: 18.6824, lng: 73.8973, type: 'medical', status: 'Active', details: '4 Doctors, 12 Beds' },
  { id: '2', name: 'Critical Medical SOS', lat: 18.6721, lng: 73.8889, type: 'sos', status: 'Critical', details: 'Unresponsive pilgrim near Gate 3' },
  { id: '3', name: 'Main Darshan Queue — Gate 1', lat: 17.6806, lng: 75.3316, type: 'queue', status: 'Full', details: 'Wait time: 260 mins' },
  { id: '4', name: 'Traffic Checkpoint 4', lat: 18.7301, lng: 73.7621, type: 'police', status: 'Active', details: 'Diversion active' },
  { id: '5', name: 'Water Tanker Station 2', lat: 18.7100, lng: 73.8100, type: 'water', status: 'Available', details: '50,000L Capacity' },
];

export default function InteractiveMap({ selectedFilter = 'all' }: { selectedFilter?: string }) {
  const [activeMarker, setActiveMarker] = useState<MarkerItem | null>(DEMO_MAP_MARKERS[0]);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const filteredMarkers = DEMO_MAP_MARKERS.filter(
    m => selectedFilter === 'all' || m.type === selectedFilter
  );

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 800);
  };

  return (
    <div className="relative w-full h-[450px] rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-[#090D16]">
      {/* Map Header Overlay */}
      <div className="absolute top-4 left-4 z-20 flex items-center gap-3 bg-[#0B0F19]/80 backdrop-blur-xl border border-white/15 px-4 py-2 rounded-xl text-xs font-semibold text-white shadow-lg">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        <span>Live GIS Feed — Maharashtra Route</span>
        <button
          onClick={handleRefresh}
          className={`ml-2 p-1 hover:bg-white/10 rounded-lg transition-all ${isRefreshing ? 'animate-spin' : ''}`}
        >
          <RefreshCw size={13} className="text-slate-400 hover:text-white" />
        </button>
      </div>

      {/* Styled Vector Canvas Simulation (Dark Cartographic Map) */}
      <div className="w-full h-full relative bg-gradient-to-br from-[#0B0F19] via-[#0D1322] to-[#080B12] flex items-center justify-center overflow-hidden">
        {/* Map Grid Lines */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:40px_40px]" />
        
        # Route Polyline Glow Curve
        <svg className="absolute inset-0 w-full h-full stroke-orange-500/30" fill="none">
          <path d="M 80 320 Q 250 180 450 260 T 800 120" strokeWidth="4" strokeDasharray="8 6" />
          <path d="M 80 320 Q 250 180 450 260 T 800 120" strokeWidth="8" className="stroke-orange-500/10 blur-sm" />
        </svg>

        {/* Interactive GIS Markers */}
        <div className="absolute inset-0 p-8 flex items-center justify-around">
          {filteredMarkers.map((marker, idx) => {
            const isSelected = activeMarker?.id === marker.id;
            return (
              <motion.div
                key={marker.id}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: idx * 0.1, type: 'spring', stiffness: 260, damping: 20 }}
                onClick={() => setActiveMarker(marker)}
                className={`relative cursor-pointer group flex flex-col items-center z-10`}
              >
                {/* Marker Pulse Halo */}
                {isSelected && (
                  <span className="absolute -inset-3 rounded-full bg-orange-500/20 animate-ping opacity-75" />
                )}

                {/* Marker Badge */}
                <div className={`w-10 h-10 rounded-full flex items-center justify-center border shadow-xl transition-all transform duration-300 ${
                  marker.type === 'sos' ? 'bg-red-500/20 border-red-500 text-red-400' :
                  marker.type === 'medical' ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400' :
                  marker.type === 'queue' ? 'bg-purple-500/20 border-purple-500 text-purple-400' :
                  marker.type === 'police' ? 'bg-indigo-500/20 border-indigo-500 text-indigo-400' :
                  'bg-orange-500/20 border-orange-500 text-orange-400'
                } ${isSelected ? 'scale-125 ring-4 ring-orange-500/40' : 'group-hover:scale-110'}`}>
                  {marker.type === 'sos' && <AlertTriangle size={18} />}
                  {marker.type === 'medical' && <Activity size={18} />}
                  {marker.type === 'queue' && <Tent size={18} />}
                  {marker.type === 'police' && <Shield size={18} />}
                  {marker.type === 'water' && <MapPin size={18} />}
                </div>

                <span className="text-[10px] font-bold text-slate-300 mt-1.5 bg-black/60 px-2 py-0.5 rounded-full border border-white/10 backdrop-blur-md whitespace-nowrap">
                  {marker.name.split('—')[0]}
                </span>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Selected Marker Detail Card */}
      {activeMarker && (
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          key={activeMarker.id}
          className="absolute bottom-4 left-4 right-4 z-20 bg-[#0B0F19]/90 backdrop-blur-2xl border border-white/15 p-4 rounded-xl flex items-center justify-between text-slate-200 shadow-2xl"
        >
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-xl ${
              activeMarker.type === 'sos' ? 'bg-red-500/20 text-red-400' : 'bg-orange-500/20 text-orange-400'
            }`}>
              <MapPin size={20} />
            </div>
            <div>
              <p className="text-sm font-bold text-white">{activeMarker.name}</p>
              <p className="text-xs text-slate-400 mt-0.5">{activeMarker.details}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className={`px-2.5 py-1 text-xs font-bold rounded-lg border ${
              activeMarker.status === 'Critical' ? 'bg-red-500/20 border-red-500/40 text-red-400' : 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400'
            }`}>
              {activeMarker.status}
            </span>
          </div>
        </motion.div>
      )}
    </div>
  );
}
