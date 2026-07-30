"use client";

import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { MapPin, RefreshCw } from 'lucide-react';
import { setOptions, importLibrary } from '@googlemaps/js-api-loader';

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
  const mapRef = useRef<HTMLDivElement>(null);
  const [activeMarker, setActiveMarker] = useState<MarkerItem | null>(DEMO_MAP_MARKERS[0]);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const filteredMarkers = DEMO_MAP_MARKERS.filter(
    m => selectedFilter === 'all' || m.type === selectedFilter
  );

  useEffect(() => {
    const initMap = async () => {
      try {
        setOptions({
          key: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
          v: 'weekly',
        });

        const { Map, Marker } = await importLibrary('maps') as any;

        if (!mapRef.current) return;

        const map = new Map(mapRef.current, {
          center: { lat: 18.2000, lng: 74.5000 },
          zoom: 8,
          disableDefaultUI: true,
          styles: [
            { elementType: "geometry", stylers: [{ color: "#0f172a" }] },
            { elementType: "labels.text.fill", stylers: [{ color: "#94a3b8" }] },
            { featureType: "road", elementType: "geometry", stylers: [{ color: "#1e293b" }] },
            { featureType: "water", elementType: "geometry", stylers: [{ color: "#0284c7" }] }
          ]
        });

        filteredMarkers.forEach((item) => {
          const marker = new Marker({
            position: { lat: item.lat, lng: item.lng },
            map: map,
            title: item.name,
          });

          marker.addListener('click', () => {
            setActiveMarker(item);
          });
        });
      } catch (err) {
        console.warn('[GCP Google Maps InteractiveMap]', err);
      }
    };

    initMap();
  }, [selectedFilter]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 800);
  };

  return (
    <div className="relative w-full h-[450px] rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-[#090D16]">
      {/* Header Overlay */}
      <div className="absolute top-4 left-4 z-20 flex items-center gap-3 bg-[#0B0F19]/80 backdrop-blur-xl border border-white/15 px-4 py-2 rounded-xl text-xs font-semibold text-white shadow-lg">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        <span>GCP Google Maps — Live GIS Layer</span>
        <button
          onClick={handleRefresh}
          className={`ml-2 p-1 hover:bg-white/10 rounded-lg transition-all ${isRefreshing ? 'animate-spin' : ''}`}
        >
          <RefreshCw size={13} className="text-slate-400 hover:text-white" />
        </button>
      </div>

      {/* Google Maps Container */}
      <div ref={mapRef} className="w-full h-full z-0 bg-[#070A12]" />

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
