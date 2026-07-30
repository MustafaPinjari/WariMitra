"use client";

import React, { useEffect, useRef, useState } from 'react';
import { 
  MapPin, 
  Navigation, 
  Activity, 
  Shield, 
  Tent, 
  Radio,
  Search,
  Crosshair
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { setOptions, importLibrary } from '@googlemaps/js-api-loader';

// Live Wari Entities across Maharashtra Route
interface Entity {
  id: string;
  title: string;
  marathiTitle: string;
  type: 'Volunteer' | 'Police' | 'Ambulance' | 'NGO Tanker' | 'Medical Camp' | 'Temple' | 'Shelter' | 'SOS';
  lat: number;
  lng: number;
  color: string;
  status: string;
  details: string;
  isMoving: boolean;
}

const INITIAL_ENTITIES: Entity[] = [
  { id: 'temple-1', title: 'Pandharpur Shri Vitthal Temple', marathiTitle: 'श्री विठ्ठल-रुक्मिणी मंदिर, पंढरपूर', type: 'Temple', lat: 17.6775, lng: 75.3283, color: '#8B5CF6', status: 'Active Queue (1.2h)', details: 'Main Pilgrimage Destination', isMoving: false },
  { id: 'alandi-1', title: 'Alandi Sant Dnyaneshwar Palkhi Start', marathiTitle: 'आळंदी (पालखी प्रस्थान)', type: 'Shelter', lat: 18.6769, lng: 73.8967, color: '#E85D04', status: 'Palkhi Dispatched', details: 'Dnyaneshwar Maharaj Palkhi', isMoving: false },
  { id: 'pune-1', title: 'Pune City Transit Hub', marathiTitle: 'पुणे शहर विश्राम स्थळ', type: 'Shelter', lat: 18.5204, lng: 73.8567, color: '#EAB308', status: 'High Footfall', details: 'Sector 2 Halt Point', isMoving: false },
  { id: 'med-1', title: 'Dive Ghat Medical Emergency Post', marathiTitle: 'दिवे घाट वैद्यकीय केंद्र', type: 'Medical Camp', lat: 18.3444, lng: 74.0305, color: '#10B981', status: 'Operational (24x7)', details: '15 Triage Beds • 4 Doctors', isMoving: false },
  { id: 'pol-1', title: 'Police Patrol Unit MH12-POL-4', marathiTitle: 'पोलीस गस्त पथक ४', type: 'Police', lat: 18.3450, lng: 74.0280, color: '#6366F1', status: 'Patrolling Slope Corridor', details: 'Traffic Diversion Active', isMoving: true },
  { id: 'amb-1', title: 'Ambulance Unit MH12-WM-1001', marathiTitle: 'रुग्णवाहिका १०-१', type: 'Ambulance', lat: 18.3480, lng: 74.0250, color: '#EF4444', status: 'Dispatched to SOS', details: 'ETA: 3 mins to Dive Ghat', isMoving: true },
  { id: 'ngo-1', title: 'NGO Water Tanker #WT-04', marathiTitle: 'अन्न व पाणी पुरवठा टँकर', type: 'NGO Tanker', lat: 18.0417, lng: 74.1833, color: '#EC4899', status: 'Refilling Saswad Stn 2', details: '50,000L ORS Water Tank', isMoving: true },
  { id: 'vol-1', title: 'Warkari Volunteer Patrol (Priya S.)', marathiTitle: 'वारकरी स्वयंसेवक पथक', type: 'Volunteer', lat: 18.5220, lng: 73.8580, color: '#F97316', status: 'Escorting Dindi #42', details: 'Sector 2 Crowd Management', isMoving: true },
];

const PALKHI_ROUTE_COORDS = [
  { lat: 18.6769, lng: 73.8967 }, // Alandi
  { lat: 18.5204, lng: 73.8567 }, // Pune
  { lat: 18.3444, lng: 74.0305 }, // Dive Ghat
  { lat: 18.3450, lng: 74.0300 }, // Saswad
  { lat: 18.2778, lng: 74.1583 }, // Jejuri
  { lat: 18.0417, lng: 74.1833 }, // Lonand
  { lat: 17.6900, lng: 75.2500 }, // Wakhari
  { lat: 17.6775, lng: 75.3283 }, // Pandharpur
];

// GCP Google Maps Dark Style Preset
const DARK_MAP_STYLES = [
  { elementType: "geometry", stylers: [{ color: "#1d2c4d" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#8ec3b9" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#1a3646" }] },
  { featureType: "administrative.country", elementType: "geometry.stroke", stylers: [{ color: "#4b687a" }] },
  { featureType: "administrative.province", elementType: "geometry.stroke", stylers: [{ color: "#4b687a" }] },
  { featureType: "landscape.natural", elementType: "geometry", stylers: [{ color: "#023e8a" }] },
  { featureType: "poi", elementType: "geometry", stylers: [{ color: "#283d70" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#304a7d" }] },
  { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#1f2835" }] },
  { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#e85d04" }] },
  { featureType: "transit", elementType: "geometry", stylers: [{ color: "#2f3948" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#001845" }] },
  { featureType: "water", elementType: "labels.text.fill", stylers: [{ color: "#515c6d" }] }
];

interface GoogleMapContainerProps {
  activeRole?: string;
}

function GoogleMapContainer({ activeRole = "Government Mission Control" }: GoogleMapContainerProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const googleMapObj = useRef<any>(null);
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);

  useEffect(() => {
    const initMap = async () => {
      try {
        setOptions({
          key: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
          v: 'weekly',
        });

        const { Map, Polyline, Marker } = await importLibrary('maps') as any;
        const { Autocomplete } = await importLibrary('places') as any;

        if (!mapRef.current) return;

        const map = new Map(mapRef.current, {
          center: { lat: 18.2000, lng: 74.5000 },
          zoom: 9,
          styles: DARK_MAP_STYLES,
          disableDefaultUI: true,
          zoomControl: true,
        });

        googleMapObj.current = map;

        // Draw Palkhi Route
        new Polyline({
          path: PALKHI_ROUTE_COORDS,
          geodesic: true,
          strokeColor: "#E85D04",
          strokeOpacity: 0.9,
          strokeWeight: 4,
          map: map,
        });

        // Entity Markers
        INITIAL_ENTITIES.forEach((entity) => {
          const marker = new Marker({
            position: { lat: entity.lat, lng: entity.lng },
            map: map,
            title: entity.title,
          });

          marker.addListener('click', () => {
            setSelectedEntity(entity);
          });
        });

        // Places Autocomplete
        if (searchInputRef.current && Autocomplete) {
          const autocomplete = new Autocomplete(searchInputRef.current, {
            componentRestrictions: { country: "in" },
            fields: ["geometry", "name"],
          });

          autocomplete.addListener("place_changed", () => {
            const place = autocomplete.getPlace();
            if (place.geometry && place.geometry.location) {
              map.panTo(place.geometry.location);
              map.setZoom(14);
            }
          });
        }
      } catch (err) {
        console.warn('[GCP Google Maps]', err);
      }
    };

    initMap();
  }, []);

  const handleRecenter = () => {
    if (googleMapObj.current) {
      googleMapObj.current.panTo({ lat: 18.2000, lng: 74.5000 });
      googleMapObj.current.setZoom(9);
    }
  };

  return (
    <div className="fixed inset-0 w-screen h-screen z-0 bg-[#070A12] overflow-hidden select-none">
      {/* GCP Google Maps Container */}
      <div ref={mapRef} className="w-full h-full z-0" />

      {/* GCP Places Autocomplete & GIS Header */}
      <div className="absolute top-20 left-6 z-20 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
        <div className="flex items-center gap-2 px-3.5 py-2 bg-[#0F1420]/90 backdrop-blur-2xl border border-orange-500/40 rounded-2xl text-xs font-extrabold text-orange-300 shadow-2xl">
          <Radio size={14} className="text-orange-400 animate-pulse" />
          <span>GCP Google Maps • Places API Active</span>
        </div>

        {/* Places Search Input */}
        <div className="relative flex items-center min-w-[280px]">
          <Search size={15} className="absolute left-3 text-orange-400 pointer-events-none" />
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Search Places / Route Halts (Google Places API)..."
            className="w-full pl-9 pr-4 py-2 bg-[#0F1420]/95 backdrop-blur-2xl border border-orange-500/40 text-white placeholder-slate-400 text-xs rounded-2xl focus:ring-2 focus:ring-orange-500 outline-none shadow-2xl transition-all"
          />
        </div>

        <button
          onClick={handleRecenter}
          className="p-2 bg-[#0F1420]/95 backdrop-blur-2xl border border-orange-500/40 text-orange-400 hover:text-white rounded-2xl shadow-xl transition-all flex items-center justify-center gap-1.5 text-xs font-bold"
          title="Recenter Palkhi Route"
        >
          <Crosshair size={15} />
          <span className="hidden md:inline">Recenter Route</span>
        </button>
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

export default React.memo(GoogleMapContainer);
