"use client";

import React, { useEffect, useRef, useState } from 'react';
import { 
  MapPin, 
  Plus, 
  Search, 
  RefreshCw, 
  Phone, 
  CheckCircle2, 
  Layers, 
  X,
  Droplets,
  Stethoscope,
  Utensils,
  Bath,
  Home,
  Shield,
  HelpCircle,
  Car
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { setOptions, importLibrary } from '@googlemaps/js-api-loader';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';

interface ServicePoint {
  id: string | number;
  name: string;
  category: 'Water' | 'Medical' | 'Food' | 'Toilets' | 'Shelter' | 'Police' | 'Help Desk' | 'Parking' | 'Other';
  details: string;
  latitude: number;
  longitude: number;
  address: string;
  contact_number: string;
  status: 'Active' | 'Available' | 'Busy' | 'Closed';
  capacity_info: string;
  created_at?: string;
}

const CATEGORIES = [
  { id: 'All', label: 'All Services', icon: Layers, color: '#F97316' },
  { id: 'Water', label: 'Water Taps', icon: Droplets, color: '#3B82F6' },
  { id: 'Medical', label: 'Medical Camp', icon: Stethoscope, color: '#10B981' },
  { id: 'Food', label: 'Food / Meals', icon: Utensils, color: '#F59E0B' },
  { id: 'Toilets', label: 'Public WC', icon: Bath, color: '#8B5CF6' },
  { id: 'Shelter', label: 'Rest Tents', icon: Home, color: '#14B8A6' },
  { id: 'Police', label: 'Police Desk', icon: Shield, color: '#6366F1' },
  { id: 'Help Desk', label: 'Information', icon: HelpCircle, color: '#EC4899' },
  { id: 'Parking', label: 'Parking Area', icon: Car, color: '#64748B' },
];

const INITIAL_FALLBACK_POINTS: ServicePoint[] = [
  {
    id: '1',
    name: 'Drinking Water Point 4 (Alandi Chowk)',
    category: 'Water',
    details: 'Continuous clean drinking water tanker with 10 taps and ORS distribution.',
    latitude: 18.6824,
    longitude: 73.8973,
    address: 'Alandi Chowk, Sector 1, Pune',
    contact_number: '+91 98230 11223',
    status: 'Active',
    capacity_info: '50,000L Reserve • Open 24x7',
  },
  {
    id: '2',
    name: 'Camp Alpha Primary Health Center',
    category: 'Medical',
    details: 'Primary medical triage, emergency first aid, heat stroke treatment, and free medicines.',
    latitude: 18.6721,
    longitude: 73.8889,
    address: 'Gate 3, Palkhi Transit Grounds, Alandi',
    contact_number: '+91 98221 44556',
    status: 'Active',
    capacity_info: '4 Doctors • 12 Beds • 2 Ambulances',
  },
  {
    id: '3',
    name: 'Saswad Annadhana & Food Camp',
    category: 'Food',
    details: 'Free hot Maharashtrian meals (Pithla Bhakri, Khichdi, Tea) served continuously.',
    latitude: 18.3450,
    longitude: 74.0300,
    address: 'Near Saswad Bus Stand, Saswad',
    contact_number: '+91 99700 88990',
    status: 'Available',
    capacity_info: 'Serves ~15,000 pilgrims/day',
  },
  {
    id: '4',
    name: 'Dive Ghat Emergency Mobile Clinic',
    category: 'Medical',
    details: 'Critical medical station for steep slope corridor emergency response.',
    latitude: 18.3444,
    longitude: 74.0305,
    address: 'Dive Ghat Slope Point, Pune-Saswad Highway',
    contact_number: '+91 98234 56789',
    status: 'Active',
    capacity_info: '15 Triage Beds • ICU Ambulance',
  },
  {
    id: '5',
    name: 'Hadapsar Public Sanitation Complex',
    category: 'Toilets',
    details: 'Clean eco-friendly mobile bio-toilets with continuous water supply.',
    latitude: 18.5020,
    longitude: 73.9280,
    address: 'Hadapsar Gadital, Pune',
    contact_number: '+91 98900 11223',
    status: 'Available',
    capacity_info: '30 Bio-Toilet Units',
  },
  {
    id: '6',
    name: 'Shelter Camp 12 — Night Stay Grounds',
    category: 'Shelter',
    details: 'Weatherproof waterproof tents, clean bedding, charging points.',
    latitude: 18.5204,
    longitude: 73.8567,
    address: 'PMC Grounds, Shivajinagar',
    contact_number: '+91 98212 99887',
    status: 'Available',
    capacity_info: '120 Beds Available',
  },
];

const DARK_MAP_STYLES = [
  { elementType: "geometry", stylers: [{ color: "#0f172a" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#94a3b8" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#0f172a" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#1e293b" }] },
  { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#ea580c" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#0284c7" }] }
];

export default function NearbyServicesPage() {
  const { t } = useAccessibility();
  const mapRef = useRef<HTMLDivElement>(null);
  const googleMapObj = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const clickMarkerRef = useRef<any>(null);

  const [points, setPoints] = useState<ServicePoint[]>(INITIAL_FALLBACK_POINTS);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedPoint, setSelectedPoint] = useState<ServicePoint | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const [newPoint, setNewPoint] = useState({
    name: '',
    category: 'Water',
    details: '',
    latitude: 18.5204,
    longitude: 73.8567,
    address: '',
    contact_number: '',
    status: 'Active',
    capacity_info: '',
  });

  const fetchServicePoints = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/maps/services/');
      if (res.ok) {
        const data = await res.json();
        const results = Array.isArray(data) ? data : (data.results || []);
        if (results.length > 0) {
          setPoints(results);
        }
      }
    } catch (e) {
      console.warn('Backend API offline, using local dataset.', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchServicePoints();
  }, []);

  const filteredPoints = points.filter(p => {
    const matchesCat = selectedCategory === 'All' || p.category === selectedCategory;
    const matchesSearch = 
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.details.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.address.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesSearch;
  });

  const getCategoryColor = (cat: string) => {
    const found = CATEGORIES.find(c => c.id === cat);
    return found ? found.color : '#F97316';
  };


  // Helper to reliably retrieve Google Maps classes
  const getGoogleMapsClasses = async () => {
    const g = (window as any).google;
    if (g?.maps?.Marker && g?.maps?.InfoWindow) {
      return {
        Marker: g.maps.Marker,
        InfoWindow: g.maps.InfoWindow,
        LatLngBounds: g.maps.LatLngBounds,
        Size: g.maps.Size,
        Point: g.maps.Point,
      };
    }

    const mapsLib = await importLibrary('maps') as any;
    let MarkerClass = mapsLib.Marker || g?.maps?.Marker;

    if (!MarkerClass) {
      try {
        const markerLib = await importLibrary('marker') as any;
        MarkerClass = markerLib.Marker || markerLib.AdvancedMarkerElement || g?.maps?.Marker;
      } catch (e) {}
    }

    return {
      Marker: MarkerClass || g?.maps?.Marker,
      InfoWindow: mapsLib.InfoWindow || g?.maps?.InfoWindow,
      LatLngBounds: mapsLib.LatLngBounds || g?.maps?.LatLngBounds,
      Size: mapsLib.Size || g?.maps?.Size,
      Point: mapsLib.Point || g?.maps?.Point,
    };
  };

  // Initialize Map & Markers
  useEffect(() => {
    const initMap = async () => {
      try {
        setOptions({
          key: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
          v: 'weekly',
        });

        const { Map } = await importLibrary('maps') as any;

        if (!mapRef.current) return;

        const map = new Map(mapRef.current, {
          center: { lat: 18.3444, lng: 74.0305 },
          zoom: 9,
          styles: DARK_MAP_STYLES,
          disableDefaultUI: true,
          zoomControl: true,
        });

        googleMapObj.current = map;

        // Click map to pick location and drop a red selection pin!
        map.addListener('click', async (e: any) => {
          const clickedLat = Number(e.latLng.lat().toFixed(5));
          const clickedLng = Number(e.latLng.lng().toFixed(5));

          setNewPoint(prev => ({
            ...prev,
            latitude: clickedLat,
            longitude: clickedLng,
            address: `Point @ ${clickedLat}, ${clickedLng}`
          }));

          try {
            const { Marker, InfoWindow } = await getGoogleMapsClasses();

            if (clickMarkerRef.current) {
              clickMarkerRef.current.setMap(null);
            }

            if (Marker) {
              const clickPinSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="40" viewBox="0 0 32 40">
                <path d="M16 0C7.16 0 0 7.16 0 16c0 12 16 24 16 24s16-12 16-24C32 7.16 24.84 0 16 0z" fill="#EF4444"/>
                <circle cx="16" cy="16" r="8" fill="#FFFFFF"/>
                <circle cx="16" cy="16" r="5" fill="#EF4444"/>
              </svg>`;

              const newMarker = new Marker({
                position: { lat: clickedLat, lng: clickedLng },
                map: googleMapObj.current,
                title: `Selected Location Pin`,
                icon: {
                  url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(clickPinSvg),
                }
              });

              if (InfoWindow) {
                const infoWindow = new InfoWindow({
                  content: `
                    <div style="padding:8px; color:#0F172A; font-family:sans-serif; text-align:center;">
                      <div style="font-weight:bold; font-size:12px; color:#EF4444; margin-bottom:4px;">📍 Selection Pin Dropped!</div>
                      <div style="font-size:11px; color:#475569;">Lat: ${clickedLat}, Lng: ${clickedLng}</div>
                      <div style="margin-top:6px; font-size:10px; font-weight:bold; color:#EA580C;">Click "+ Add Service Pin" to publish this point!</div>
                    </div>
                  `
                });

                infoWindow.open(googleMapObj.current, newMarker);
              }
              clickMarkerRef.current = newMarker;
            }

          } catch (err) {
            console.warn('Error creating click pin:', err);
          }

          showToast(`📍 Pin Dropped @ ${clickedLat}, ${clickedLng}`);
        });

      } catch (err) {
        console.warn('[Google Maps Init]', err);
      }
    };

    initMap();
  }, []);

  // Place markers on Google Map & Fit Bounds
  useEffect(() => {
    const updateMarkers = async () => {
      if (!googleMapObj.current) return;

      // Clear previous markers
      markersRef.current.forEach(m => m.setMap(null));
      markersRef.current = [];

      try {
        const { Marker, InfoWindow, LatLngBounds } = await getGoogleMapsClasses();
        const bounds = LatLngBounds ? new LatLngBounds() : null;
        let hasPoints = false;

        if (!Marker) return;

        filteredPoints.forEach((p) => {
          hasPoints = true;
          if (bounds) bounds.extend({ lat: p.latitude, lng: p.longitude });
          const color = getCategoryColor(p.category);

          const marker = new Marker({
            position: { lat: p.latitude, lng: p.longitude },
            map: googleMapObj.current,
            title: `${p.name} (${p.category})`,
          });

          if (InfoWindow) {
            const infoWindow = new InfoWindow({
              content: `
                <div style="padding:10px; color:#0F172A; font-family:sans-serif; max-width:220px;">
                  <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;">
                    <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:${color};"></span>
                    <span style="font-weight:800; font-size:11px; color:${color}; text-transform:uppercase;">${p.category}</span>
                  </div>
                  <h4 style="margin:0 0 4px 0; font-weight:bold; font-size:13px; color:#0F172A;">${p.name}</h4>
                  <p style="margin:0 0 6px 0; font-size:11px; color:#475569;">${p.details}</p>
                  <div style="font-size:10px; color:#0284C7; font-weight:bold;">${p.capacity_info || 'Operational'}</div>
                </div>
              `
            });

            marker.addListener('click', () => {
              setSelectedPoint(p);
              infoWindow.open(googleMapObj.current, marker);
              googleMapObj.current.panTo({ lat: p.latitude, lng: p.longitude });
            });
          }

          markersRef.current.push(marker);
        });

        if (hasPoints && bounds && googleMapObj.current) {
          googleMapObj.current.fitBounds(bounds);
        }

      } catch (err) {
        console.warn('Error placing markers:', err);
      }
    };

    updateMarkers();
  }, [filteredPoints]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPoint.name.trim()) return;

    setIsSubmitting(true);
    const pointPayload = {
      name: newPoint.name,
      category: newPoint.category,
      details: newPoint.details || 'Service point on Wari route.',
      latitude: newPoint.latitude,
      longitude: newPoint.longitude,
      address: newPoint.address || 'Wari Route',
      contact_number: newPoint.contact_number,
      status: newPoint.status,
      capacity_info: newPoint.capacity_info || 'Available',
    };

    try {
      const res = await fetch('http://localhost:8000/api/v1/maps/services/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pointPayload),
      });

      if (res.ok) {
        const created = await res.json();
        setPoints(prev => [created, ...prev]);
        showToast(`🎉 Service Point "${created.name}" created on Map!`);
      } else {
        const localCreated: ServicePoint = { ...pointPayload, id: Date.now() } as any;
        setPoints(prev => [localCreated, ...prev]);
        showToast(`🎉 Service Point "${localCreated.name}" saved!`);
      }
    } catch (_) {
      const localCreated: ServicePoint = { ...pointPayload, id: Date.now() } as any;
      setPoints(prev => [localCreated, ...prev]);
      showToast(`🎉 Service Point "${localCreated.name}" saved!`);
    } finally {
      setIsSubmitting(false);
      setIsAddModalOpen(false);
      setNewPoint({
        name: '',
        category: 'Water',
        details: '',
        latitude: 18.5204,
        longitude: 73.8567,
        address: '',
        contact_number: '',
        status: 'Active',
        capacity_info: '',
      });
    }
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-[#131B2E] border border-orange-500/30 p-6 rounded-3xl shadow-xl gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-white tracking-tight flex items-center gap-3">
            <MapPin className="text-orange-400" size={24} />
            <span>{t('नजीकच्या सुविधा व नकाशे (Nearby Services & Pins)', 'Nearby Services & GIS Map')}</span>
          </h1>
          <p className="text-slate-300 text-xs mt-1 font-medium">
            {t('वारी मार्गांवरील पाणी, वैद्यकीय शिबीर, अन्न व निवारा स्थानांचे नकाशे', 'Real-time location map of water points, medical camps, food stalls & shelters')}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-gradient-to-r from-orange-600 to-amber-500 hover:from-orange-500 hover:to-amber-400 text-white font-black text-xs shadow-lg shadow-orange-500/25 transition-all"
          >
            <Plus size={16} />
            <span>{t('नकाशावर बिंदू जोडा', '+ Add Service Pin')}</span>
          </button>
        </div>
      </div>

      {/* Overview Stat Counters */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-[#131B2E] border border-white/10 flex items-center justify-between shadow-lg">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Total Service Pins</p>
            <h3 className="text-2xl font-black text-white mt-1">{points.length}</h3>
          </div>
          <div className="w-10 h-10 rounded-xl bg-orange-500/20 flex items-center justify-center text-orange-400">
            <MapPin size={20} />
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-[#131B2E] border border-white/10 flex items-center justify-between shadow-lg">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Water Points</p>
            <h3 className="text-2xl font-black text-blue-400 mt-1">{points.filter(p => p.category === 'Water').length}</h3>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center text-blue-400">
            <Droplets size={20} />
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-[#131B2E] border border-white/10 flex items-center justify-between shadow-lg">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Medical Camps</p>
            <h3 className="text-2xl font-black text-emerald-400 mt-1">{points.filter(p => p.category === 'Medical').length}</h3>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center text-emerald-400">
            <Stethoscope size={20} />
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-[#131B2E] border border-white/10 flex items-center justify-between shadow-lg">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Active Facilities</p>
            <h3 className="text-2xl font-black text-amber-400 mt-1">{points.filter(p => p.status === 'Active' || p.status === 'Available').length}</h3>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center text-amber-400">
            <CheckCircle2 size={20} />
          </div>
        </div>
      </div>

      {/* Main Split View: Map + Cards List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left: Interactive Map Container (Takes 2 Columns) */}
        <div className="lg:col-span-2 bg-[#131B2E] border border-white/10 rounded-3xl p-4 flex flex-col shadow-xl min-h-[480px] relative overflow-hidden">
          
          {/* Map Sub-header */}
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <h3 className="text-xs font-black text-white uppercase tracking-wider">
                {t('पालखी मार्ग नकाशे', 'Live Wari Route GIS Layer')}
              </h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] text-slate-400 font-medium">Click map to pick pin location</span>
              <button
                onClick={fetchServicePoints}
                className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 transition-all border border-white/10"
                title="Refresh Map Points"
              >
                <RefreshCw size={13} className={isLoading ? 'animate-spin' : ''} />
              </button>
            </div>
          </div>

          {/* Map Canvas */}
          <div className="flex-1 w-full h-[380px] rounded-2xl overflow-hidden relative border border-white/10 bg-[#090D16]">
            <div ref={mapRef} className="w-full h-full z-0" />

            {/* Toast Notification */}
            <AnimatePresence>
              {toastMessage && (
                <motion.div
                  initial={{ opacity: 0, y: -15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                  className="absolute top-4 left-1/2 -translate-x-1/2 z-30 px-4 py-2 rounded-xl bg-[#0F1420]/95 border border-orange-500/40 text-xs font-bold text-white shadow-2xl backdrop-blur-xl"
                >
                  {toastMessage}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Selected Pin Bottom Info */}
          {selectedPoint && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-3 p-3.5 rounded-2xl bg-white/5 border border-orange-500/30 flex items-center justify-between gap-4"
            >
              <div className="flex items-center gap-3">
                <div 
                  className="w-9 h-9 rounded-xl flex items-center justify-center text-white font-bold"
                  style={{ backgroundColor: `${getCategoryColor(selectedPoint.category)}30`, color: getCategoryColor(selectedPoint.category) }}
                >
                  <MapPin size={18} />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-xs font-bold text-white">{selectedPoint.name}</h4>
                    <span className="px-2 py-0.5 text-[9px] font-bold rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      {selectedPoint.status}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5">{selectedPoint.details}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {selectedPoint.contact_number && (
                  <a 
                    href={`tel:${selectedPoint.contact_number}`}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-500/20 text-blue-400 border border-blue-500/30 text-xs font-bold hover:bg-blue-500/30"
                  >
                    <Phone size={12} />
                    <span>Call</span>
                  </a>
                )}
                <button
                  onClick={() => setSelectedPoint(null)}
                  className="p-1 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400"
                >
                  <X size={14} />
                </button>
              </div>
            </motion.div>
          )}

        </div>

        {/* Right: Service Cards & Filter Sidebar (1 Column) */}
        <div className="bg-[#131B2E] border border-white/10 rounded-3xl p-4 flex flex-col gap-4 shadow-xl max-h-[560px]">
          
          {/* Search Bar */}
          <div className="relative flex items-center">
            <Search size={14} className="absolute left-3 text-slate-400" />
            <input
              type="text"
              placeholder={t('सुविधा शोधा...', 'Search service pins...')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-white/5 border border-white/10 rounded-xl text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-orange-500"
            />
          </div>

          {/* Category Filter Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
            {CATEGORIES.map((cat) => {
              const isSelected = selectedCategory === cat.id;
              const Icon = cat.icon;
              return (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-bold whitespace-nowrap transition-all border ${
                    isSelected 
                      ? 'bg-orange-500 text-white border-orange-400 shadow-sm' 
                      : 'bg-white/5 text-slate-300 border-white/5 hover:bg-white/10'
                  }`}
                >
                  <Icon size={12} style={{ color: isSelected ? '#FFF' : cat.color }} />
                  <span>{cat.label}</span>
                </button>
              );
            })}
          </div>

          {/* Points List */}
          <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
            {filteredPoints.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                {t('कोणत्याही सुविधा सापडल्या नाहीत', 'No service points matching filter.')}
              </div>
            ) : (
              filteredPoints.map((p) => {
                const isSelected = selectedPoint?.id === p.id;
                const catColor = getCategoryColor(p.category);

                return (
                  <motion.div
                    key={p.id}
                    onClick={() => {
                      setSelectedPoint(p);
                      if (googleMapObj.current) {
                        googleMapObj.current.panTo({ lat: p.latitude, lng: p.longitude });
                        googleMapObj.current.setZoom(12);
                      }
                    }}
                    whileHover={{ scale: 1.01 }}
                    className={`p-3 rounded-2xl border transition-all cursor-pointer ${
                      isSelected 
                        ? 'bg-orange-500/15 border-orange-500/50 shadow-md' 
                        : 'bg-[#0B0F19] border-white/5 hover:border-white/20'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2.5">
                        <div 
                          className="w-8 h-8 rounded-xl flex items-center justify-center text-white flex-shrink-0"
                          style={{ backgroundColor: `${catColor}25`, color: catColor }}
                        >
                          <MapPin size={16} />
                        </div>
                        <div>
                          <h4 className="text-xs font-bold text-white line-clamp-1">{p.name}</h4>
                          <span className="text-[10px] text-slate-400 font-medium">{p.category} • {p.capacity_info || 'Active'}</span>
                        </div>
                      </div>

                      <span className="px-2 py-0.5 text-[9px] font-bold rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                        {p.status}
                      </span>
                    </div>
                  </motion.div>
                );
              })
            )}
          </div>

        </div>

      </div>

      {/* Modal Dialog for Adding Point */}
      <AnimatePresence>
        {isAddModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-lg bg-[#0F1420] border border-orange-500/40 rounded-3xl p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-orange-500/20 text-orange-400">
                    <Plus size={18} />
                  </div>
                  <div>
                    <h3 className="text-sm font-extrabold text-white">
                      {t('नकाशावर नवीन बिंदू जोडा', 'Add New Service Pin')}
                    </h3>
                    <p className="text-[11px] text-slate-400">
                      {t('नकाशावर क्लिक करा किंवा खाली माहिती टाका', 'Click map to pick pin coordinates')}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setIsAddModalOpen(false)}
                  className="p-1 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white"
                >
                  <X size={16} />
                </button>
              </div>

              <form onSubmit={handleAddSubmit} className="space-y-3 text-xs">
                
                <div>
                  <label className="block text-slate-300 font-bold mb-1">Service Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Drinking Water Tanker 5 or Camp Alpha Medical"
                    value={newPoint.name}
                    onChange={(e) => setNewPoint({ ...newPoint, name: e.target.value })}
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:ring-1 focus:ring-orange-500 outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-300 font-bold mb-1">Category *</label>
                    <select
                      value={newPoint.category}
                      onChange={(e) => setNewPoint({ ...newPoint, category: e.target.value as any })}
                      className="w-full px-3 py-2 bg-[#0F1420] border border-white/10 rounded-xl text-white focus:ring-1 focus:ring-orange-500 outline-none"
                    >
                      {CATEGORIES.filter(c => c.id !== 'All').map(c => (
                        <option key={c.id} value={c.id} className="bg-[#0F1420] text-white">
                          {c.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-300 font-bold mb-1">Status</label>
                    <select
                      value={newPoint.status}
                      onChange={(e) => setNewPoint({ ...newPoint, status: e.target.value as any })}
                      className="w-full px-3 py-2 bg-[#0F1420] border border-white/10 rounded-xl text-white focus:ring-1 focus:ring-orange-500 outline-none"
                    >
                      <option value="Active">Active</option>
                      <option value="Available">Available</option>
                      <option value="Busy">Busy</option>
                      <option value="Closed">Closed</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-300 font-bold mb-1">Latitude *</label>
                    <input
                      type="number"
                      step="any"
                      required
                      value={newPoint.latitude}
                      onChange={(e) => setNewPoint({ ...newPoint, latitude: parseFloat(e.target.value) || 0 })}
                      className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-white outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-300 font-bold mb-1">Longitude *</label>
                    <input
                      type="number"
                      step="any"
                      required
                      value={newPoint.longitude}
                      onChange={(e) => setNewPoint({ ...newPoint, longitude: parseFloat(e.target.value) || 0 })}
                      className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-white outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-slate-300 font-bold mb-1">Details & Capacity</label>
                  <input
                    type="text"
                    placeholder="e.g. 50,000L Reserve Tank • 10 Taps Available"
                    value={newPoint.details}
                    onChange={(e) => setNewPoint({ ...newPoint, details: e.target.value, capacity_info: e.target.value })}
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-300 font-bold mb-1">Contact Phone</label>
                    <input
                      type="text"
                      placeholder="+91 98230..."
                      value={newPoint.contact_number}
                      onChange={(e) => setNewPoint({ ...newPoint, contact_number: e.target.value })}
                      className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-300 font-bold mb-1">Landmark / Address</label>
                    <input
                      type="text"
                      placeholder="e.g. Alandi Gate 3"
                      value={newPoint.address}
                      onChange={(e) => setNewPoint({ ...newPoint, address: e.target.value })}
                      className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 outline-none"
                    />
                  </div>
                </div>

                <div className="pt-2 flex justify-end gap-2 border-t border-white/10">
                  <button
                    type="button"
                    onClick={() => setIsAddModalOpen(false)}
                    className="px-3.5 py-1.5 rounded-xl bg-white/5 text-slate-300 font-bold hover:bg-white/10"
                  >
                    Cancel
                  </button>

                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-4 py-1.5 rounded-xl bg-orange-500 text-white font-bold shadow-md hover:bg-orange-600 flex items-center gap-1.5"
                  >
                    {isSubmitting ? <RefreshCw size={13} className="animate-spin" /> : <CheckCircle2 size={13} />}
                    <span>Save & Drop Pin</span>
                  </button>
                </div>

              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
