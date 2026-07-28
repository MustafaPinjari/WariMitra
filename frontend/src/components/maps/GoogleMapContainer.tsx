"use client";

import { useEffect, useRef, useState } from 'react';
import { 
  MapPin, 
  Navigation, 
  Activity, 
  Shield, 
  HeartHandshake, 
  Tent, 
  Radio
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Live Wari Entities across Maharashtra Route (Actual Lat/Lng Coordinates)
interface Entity {
  id: string;
  title: string;
  marathiTitle: string;
  type: 'Volunteer' | 'Police' | 'Ambulance' | 'NGO Tanker' | 'Medical Camp' | 'Temple' | 'Shelter';
  lat: number;
  lng: number;
  color: string;
  status: string;
  details: string;
  isMoving: boolean;
  dLat?: number;
  dLng?: number;
}

const INITIAL_ENTITIES: Entity[] = [
  { id: 'temple-1', title: 'Pandharpur Shri Vitthal Temple', marathiTitle: 'श्री विठ्ठल-रुक्मिणी मंदिर, पंढरपूर', type: 'Temple', lat: 17.6775, lng: 75.3283, color: '#8B5CF6', status: 'Active Queue (1.2h)', details: 'Main Pilgrimage Destination', isMoving: false },
  { id: 'alandi-1', title: 'Alandi Sant Dnyaneshwar Palkhi Start', marathiTitle: 'आळंदी (पालखी प्रस्थान)', type: 'Shelter', lat: 18.6769, lng: 73.8967, color: '#E85D04', status: 'Palkhi Dispatched', details: 'Dnyaneshwar Maharaj Palkhi', isMoving: false },
  { id: 'pune-1', title: 'Pune City Transit Hub', marathiTitle: 'पुणे शहर विश्राम स्थळ', type: 'Shelter', lat: 18.5204, lng: 73.8567, color: '#EAB308', status: 'High Footfall', details: 'Sector 2 Halt Point', isMoving: false },
  { id: 'med-1', title: 'Dive Ghat Medical Emergency Post', marathiTitle: 'दिवे घाट वैद्यकीय केंद्र', type: 'Medical Camp', lat: 18.3444, lng: 74.0305, color: '#10B981', status: 'Operational (24x7)', details: '15 Triage Beds • 4 Doctors', isMoving: false },
  { id: 'pol-1', title: 'Police Patrol Unit MH12-POL-4', marathiTitle: 'पोलीस गस्त पथक ४', type: 'Police', lat: 18.3450, lng: 74.0280, color: '#6366F1', status: 'Patrolling Slope Corridor', details: 'Traffic Diversion Active', isMoving: true, dLat: 0.0008, dLng: 0.0006 },
  { id: 'amb-1', title: 'Ambulance Unit MH12-WM-1001', marathiTitle: 'रुग्णवाहिका १०-१', type: 'Ambulance', lat: 18.3480, lng: 74.0250, color: '#EF4444', status: 'Dispatched to SOS', details: 'ETA: 3 mins to Dive Ghat', isMoving: true, dLat: -0.0006, dLng: -0.0004 },
  { id: 'ngo-1', title: 'NGO Water Tanker #WT-04', marathiTitle: 'अन्न व पाणी पुरवठा टँकर', type: 'NGO Tanker', lat: 18.0417, lng: 74.1833, color: '#EC4899', status: 'Refilling Saswad Stn 2', details: '50,000L ORS Water Tank', isMoving: true, dLat: 0.0005, dLng: 0.0003 },
  { id: 'vol-1', title: 'Warkari Volunteer Patrol (Priya S.)', marathiTitle: 'वारकरी स्वयंसेवक पथक', type: 'Volunteer', lat: 18.5220, lng: 73.8580, color: '#F97316', status: 'Escorting Dindi #42', details: 'Sector 2 Crowd Management', isMoving: true, dLat: 0.0004, dLng: 0.0004 },
];

// Palkhi GPS Coordinates (Alandi to Pandharpur Route)
const PALKHI_ROUTE_COORDS: [number, number][] = [
  [18.6769, 73.8967], // Alandi
  [18.5204, 73.8567], // Pune
  [18.3444, 74.0305], // Dive Ghat
  [18.3450, 74.0300], // Saswad
  [18.2778, 74.1583], // Jejuri
  [18.0417, 74.1833], // Lonand
  [17.6900, 75.2500], // Wakhari
  [17.6775, 75.3283], // Pandharpur
];

interface GoogleMapContainerProps {
  activeRole?: string;
}

export default function GoogleMapContainer({ activeRole = "Government Mission Control" }: GoogleMapContainerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const leafletMapRef = useRef<any>(null);
  const markersMapRef = useRef<Map<string, any>>(new Map());
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Load Leaflet CSS dynamically if not present
    if (!document.getElementById('leaflet-css')) {
      const link = document.createElement('link');
      link.id = 'leaflet-css';
      link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(link);
    }

    const initLeafletMap = () => {
      if (!containerRef.current || !(window as any).L || leafletMapRef.current) return;

      const L = (window as any).L;

      // Initialize Leaflet Map centered on Pandharpur Wari Route in Maharashtra
      const map = L.map(containerRef.current, {
        center: [18.2000, 74.5000],
        zoom: 9,
        zoomControl: false,
        attributionControl: false,
      });

      leafletMapRef.current = map;

      // Add CartoDB Dark Matter tile layer (100% Free real interactive street map tiles)
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        subdomains: 'abcd',
      }).addTo(map);

      // Add Zoom Control to Top Left
      L.control.zoom({ position: 'topleft' }).addTo(map);

      // Draw Palkhi Route Polyline with Glowing Bhagwa Saffron stroke
      const polyline = L.polyline(PALKHI_ROUTE_COORDS, {
        color: '#E85D04',
        weight: 5,
        opacity: 0.9,
        dashArray: '10, 8',
        lineCap: 'round',
      }).addTo(map);

      // Fit bounds to show entire route
      map.fitBounds(polyline.getBounds(), { padding: [50, 50] });

      // Create Custom Circle Markers for Entities
      INITIAL_ENTITIES.forEach(entity => {
        const marker = L.circleMarker([entity.lat, entity.lng], {
          radius: entity.isMoving ? 9 : 11,
          fillColor: entity.color,
          color: '#FFFFFF',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.9,
        }).addTo(map);

        // Bind interactive tooltip and click handler
        marker.bindTooltip(`<b>${entity.title}</b><br><span style="color:#F97316;">${entity.marathiTitle}</span>`, {
          direction: 'top',
          offset: [0, -10],
          className: 'leaflet-custom-tooltip',
        });

        marker.on('click', () => {
          setSelectedEntity(entity);
        });

        markersMapRef.current.set(entity.id, marker);
      });
    };

    // Load Leaflet JS dynamically
    if ((window as any).L) {
      initLeafletMap();
    } else {
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
      script.async = true;
      script.onload = initLeafletMap;
      document.head.appendChild(script);
    }

    return () => {
      if (leafletMapRef.current) {
        leafletMapRef.current.remove();
        leafletMapRef.current = null;
      }
    };
  }, []);

  // Live Animation Loop for Moving Vehicles/Units
  useEffect(() => {
    const interval = setInterval(() => {
      INITIAL_ENTITIES.forEach(entity => {
        if (entity.isMoving && entity.dLat && entity.dLng) {
          entity.lat += entity.dLat * 0.02;
          entity.lng += entity.dLng * 0.02;

          // Bounce back within bounds
          if (entity.lat > 18.7 || entity.lat < 17.6) entity.dLat = -entity.dLat;
          if (entity.lng > 75.4 || entity.lng < 73.8) entity.dLng = -entity.dLng;

          const marker = markersMapRef.current.get(entity.id);
          if (marker) {
            marker.setLatLng([entity.lat, entity.lng]);
          }
        }
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 w-screen h-screen z-0 bg-[#070A12] overflow-hidden select-none">
      {/* Real Interactive Leaflet + OpenStreetMap Tile Engine */}
      <div ref={containerRef} className="w-full h-full z-0" />

      {/* Floating Status Indicator */}
      <div className="absolute top-20 left-6 z-10 hidden sm:flex items-center gap-2 px-3.5 py-1.5 bg-[#0F1420]/90 backdrop-blur-2xl border border-orange-500/40 rounded-xl text-xs font-extrabold text-orange-300 shadow-2xl">
        <Radio size={14} className="text-orange-400 animate-pulse" />
        <span>OpenStreetMap • Wari Live GIS Active</span>
      </div>

      {/* Interactive Entity Detail Popover Modal */}
      <AnimatePresence>
        {selectedEntity && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="absolute bottom-20 left-6 z-30 w-80 bg-[#0F1420]/95 backdrop-blur-2xl border border-orange-500/40 p-4 rounded-2xl shadow-2xl space-y-2 text-xs"
          >
            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <div className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: selectedEntity.color }} 
                />
                <span className="font-extrabold text-white text-xs">{selectedEntity.type}</span>
              </div>
              <button 
                onClick={() => setSelectedEntity(null)}
                className="text-slate-400 hover:text-white font-bold px-1.5 py-0.5 rounded bg-white/5"
              >
                ✕
              </button>
            </div>

            <div>
              <p className="text-white font-bold text-sm">{selectedEntity.title}</p>
              <p className="text-orange-400 font-medium text-[11px]">{selectedEntity.marathiTitle}</p>
            </div>

            <div className="p-2.5 bg-white/5 rounded-xl border border-white/5 space-y-1">
              <p className="text-slate-300 font-semibold flex justify-between">
                <span>Status:</span>
                <span className="text-emerald-400 font-bold">{selectedEntity.status}</span>
              </p>
              <p className="text-slate-400 text-[10px]">{selectedEntity.details}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
