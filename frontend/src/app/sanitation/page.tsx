"use client";

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Trash2, 
  Plus, 
  Droplets, 
  CheckCircle2, 
  MapPin, 
  AlertTriangle, 
  RefreshCw, 
  Phone, 
  Camera, 
  X, 
  Bath, 
  Upload, 
  ShieldCheck, 
  Clock, 
  Sparkles, 
  Check, 
  Filter,
  Maximize2
} from 'lucide-react';
import { setOptions, importLibrary } from '@googlemaps/js-api-loader';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';

const API_BASE = 'http://127.0.0.1:8000/api/v1';

interface PublicToilet {
  id: string | number;
  name: string;
  location: string;
  gender_type: string;
  cleanliness_score: number;
  is_water_available: boolean;
  latitude: number;
  longitude: number;
}

interface WasteReport {
  id: string | number;
  location_name: string;
  waste_type: string;
  description: string;
  image?: string;
  image_url?: string;
  status: 'PENDING' | 'CLEANING_DISPATCHED' | 'CLEANED';
  latitude: number;
  longitude: number;
  created_at?: string;
}

const LIGHT_MAP_STYLES = [
  { elementType: "geometry", stylers: [{ color: "#f8fafc" }] },
  { elementType: "labels.icon", stylers: [{ visibility: "off" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#475569" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#ffffff" }] },
  { featureType: "administrative.land_parcel", elementType: "labels.text.fill", stylers: [{ color: "#cbd5e1" }] },
  { featureType: "poi", elementType: "geometry", stylers: [{ color: "#f1f5f9" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#ffffff" }] },
  { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#fed7aa" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#bae6fd" }] }
];

export default function SanitationPage() {
  const { t } = useAccessibility();
  const mapRef = useRef<HTMLDivElement>(null);
  const googleMapObj = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const clickMarkerRef = useRef<any>(null);

  const [toilets, setToilets] = useState<PublicToilet[]>([]);
  const [wasteReports, setWasteReports] = useState<WasteReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'TOILETS' | 'WASTE'>('TOILETS');

  // Modals
  const [addToiletModalOpen, setAddToiletModalOpen] = useState(false);
  const [reportWasteModalOpen, setReportWasteModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Add Toilet Form State
  const [toiletName, setToiletName] = useState('');
  const [toiletLocation, setToiletLocation] = useState('');
  const [genderType, setGenderType] = useState('Unisex');
  const [cleanlinessScore, setCleanlinessScore] = useState(90);
  const [hasWater, setHasWater] = useState(true);
  const [toiletLat, setToiletLat] = useState(18.5204);
  const [toiletLng, setToiletLng] = useState(73.8567);

  // Waste Report Form State
  const [wasteLocation, setWasteLocation] = useState('');
  const [wasteType, setWasteType] = useState('Overflowing Bin');
  const [wasteDescription, setWasteDescription] = useState('');
  const [wasteLat, setWasteLat] = useState(18.5204);
  const [wasteLng, setWasteLng] = useState(73.8567);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const fetchSanitationData = async () => {
    setLoading(true);
    try {
      const [toiletsRes, wasteRes] = await Promise.all([
        fetch(`${API_BASE}/sanitation/toilets/`).then(res => res.json()).catch(() => []),
        fetch(`${API_BASE}/sanitation/waste-reports/`).then(res => res.json()).catch(() => []),
      ]);

      const toiletsList = Array.isArray(toiletsRes) ? toiletsRes : (toiletsRes.results || []);
      const wasteList = Array.isArray(wasteRes) ? wasteRes : (wasteRes.results || []);

      setToilets(toiletsList);
      setWasteReports(wasteList);
    } catch (e) {
      console.error('Failed to load sanitation data:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSanitationData();
  }, []);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
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

  // Init Google Light Map
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
          center: { lat: 18.5204, lng: 73.8567 },
          zoom: 11,
          styles: LIGHT_MAP_STYLES, // Light Theme Map
          disableDefaultUI: true,
          zoomControl: true,
        });

        googleMapObj.current = map;

        // Click map to pick location & drop a red selection pin!
        map.addListener('click', async (e: any) => {
          const clickedLat = Number(e.latLng.lat().toFixed(5));
          const clickedLng = Number(e.latLng.lng().toFixed(5));

          setToiletLat(clickedLat);
          setToiletLng(clickedLng);
          setWasteLat(clickedLat);
          setWasteLng(clickedLng);

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
                      <div style="margin-top:6px; font-size:10px; font-weight:bold; color:#0D9488;">Click "+ Add Toilet" or "Report Waste" to save this location!</div>
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
        console.warn('[Sanitation Light Map Init]', err);
      }
    };

    initMap();
  }, []);

  // Update reduced pin markers on map & fit bounds
  useEffect(() => {
    const updateMarkers = async () => {
      if (!googleMapObj.current) return;

      markersRef.current.forEach(m => m.setMap(null));
      markersRef.current = [];

      try {
        const { Marker, InfoWindow, LatLngBounds, Size, Point } = await getGoogleMapsClasses();
        const bounds = LatLngBounds ? new LatLngBounds() : null;
        let hasPoints = false;

        const sizeObj = Size ? new Size(22, 28) : undefined;
        const anchorObj = Point ? new Point(11, 28) : undefined;

        if (!Marker) return;

        if (activeTab === 'TOILETS') {
          toilets.forEach((t) => {
            hasPoints = true;
            if (bounds) bounds.extend({ lat: t.latitude, lng: t.longitude });

            const pinSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="30" viewBox="0 0 24 30">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 9 12 18 12 18s12-9 12-18C24 5.37 18.63 0 12 0z" fill="#8B5CF6"/>
              <circle cx="12" cy="12" r="6" fill="#FFFFFF"/>
            </svg>`;

            const marker = new Marker({
              position: { lat: t.latitude, lng: t.longitude },
              map: googleMapObj.current,
              title: t.name,
              icon: sizeObj && anchorObj ? {
                url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(pinSvg),
                scaledSize: sizeObj,
                anchor: anchorObj,
              } : undefined
            });

            if (InfoWindow) {
              const infoWindow = new InfoWindow({
                content: `
                  <div style="padding:8px; color:#0F172A; font-family:sans-serif; max-width:200px;">
                    <h4 style="margin:0 0 4px 0; font-weight:bold; font-size:12px; color:#6B21A8;">🚽 ${t.name}</h4>
                    <p style="margin:0 0 4px 0; font-size:11px; color:#475569;">${t.location}</p>
                    <div style="font-size:10px; font-weight:bold; color:#059669;">${t.cleanliness_score}% Clean • ${t.gender_type}</div>
                  </div>
                `
              });

              marker.addListener('click', () => {
                infoWindow.open(googleMapObj.current, marker);
                googleMapObj.current.panTo({ lat: t.latitude, lng: t.longitude });
              });
            }

            markersRef.current.push(marker);
          });
        } else {
          wasteReports.forEach((w) => {
            hasPoints = true;
            if (bounds) bounds.extend({ lat: w.latitude, lng: w.longitude });

            const pinColor = w.status === 'CLEANED' ? '#10B981' : w.status === 'CLEANING_DISPATCHED' ? '#3B82F6' : '#EF4444';
            const pinSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="30" viewBox="0 0 24 30">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 9 12 18 12 18s12-9 12-18C24 5.37 18.63 0 12 0z" fill="${pinColor}"/>
              <circle cx="12" cy="12" r="6" fill="#FFFFFF"/>
            </svg>`;

            const marker = new Marker({
              position: { lat: w.latitude, lng: w.longitude },
              map: googleMapObj.current,
              title: w.location_name,
              icon: sizeObj && anchorObj ? {
                url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(pinSvg),
                scaledSize: sizeObj,
                anchor: anchorObj,
              } : undefined
            });

            if (InfoWindow) {
              const infoWindow = new InfoWindow({
                content: `
                  <div style="padding:8px; color:#0F172A; font-family:sans-serif; max-width:200px;">
                    <h4 style="margin:0 0 4px 0; font-weight:bold; font-size:12px; color:#B91C1C;">🚨 ${w.waste_type}</h4>
                    <p style="margin:0 0 4px 0; font-size:11px; color:#475569;">${w.location_name}</p>
                    <div style="font-size:10px; font-weight:bold; color:${pinColor};">${w.status}</div>
                  </div>
                `
              });

              marker.addListener('click', () => {
                infoWindow.open(googleMapObj.current, marker);
                googleMapObj.current.panTo({ lat: w.latitude, lng: w.longitude });
              });
            }

            markersRef.current.push(marker);
          });
        }

        if (hasPoints && bounds && googleMapObj.current) {
          googleMapObj.current.fitBounds(bounds);
        }

      } catch (err) {
        console.warn('Error placing reduced light markers:', err);
      }
    };

    updateMarkers();
  }, [toilets, wasteReports, activeTab]);

  const fitAllMapPins = async () => {
    if (!googleMapObj.current) return;
    try {
      const { LatLngBounds } = await getGoogleMapsClasses();
      if (!LatLngBounds) return;
      const bounds = new LatLngBounds();
      let count = 0;
      toilets.forEach(t => { bounds.extend({ lat: t.latitude, lng: t.longitude }); count++; });
      wasteReports.forEach(w => { bounds.extend({ lat: w.latitude, lng: w.longitude }); count++; });
      if (count > 0) {
        googleMapObj.current.fitBounds(bounds);
        showToast('🎯 Map Centered to All Sanitation Pins');
      }
    } catch (e) {
      console.warn(e);
    }
  };

  // File Picker for Waste Report
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => setImagePreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  // Submit New Public Toilet
  const handleAddToiletSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    const payload = {
      name: toiletName,
      location: toiletLocation,
      gender_type: genderType,
      cleanliness_score: cleanlinessScore,
      is_water_available: hasWater,
      latitude: toiletLat,
      longitude: toiletLng,
    };

    try {
      const res = await fetch(`${API_BASE}/sanitation/toilets/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        showToast('🎉 Public Toilet registered successfully!');
        setAddToiletModalOpen(false);
        resetToiletForm();
        fetchSanitationData();
      }
    } catch (e) {
      showToast('⚠️ Registration failed');
    } finally {
      setSubmitting(false);
    }
  };

  // Submit Waste Report (with Image upload support via FormData to S3/backend)
  const handleReportWasteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const formData = new FormData();
      formData.append('location_name', wasteLocation);
      formData.append('waste_type', wasteType);
      formData.append('description', wasteDescription);
      formData.append('status', 'PENDING');
      formData.append('latitude', wasteLat.toString());
      formData.append('longitude', wasteLng.toString());

      if (selectedFile) {
        formData.append('image', selectedFile);
      }

      const res = await fetch(`${API_BASE}/sanitation/waste-reports/`, {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        showToast('🎉 Waste report submitted! Municipal crew notified.');
        setReportWasteModalOpen(false);
        resetWasteForm();
        fetchSanitationData();
      }
    } catch (e) {
      showToast('⚠️ Report submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  // Staff Action: Manage Waste Report Status
  const handleUpdateWasteStatus = async (reportId: string | number, newStatus: string) => {
    try {
      const res = await fetch(`${API_BASE}/sanitation/waste-reports/${reportId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) {
        showToast(`✓ Report status updated to ${newStatus}`);
        fetchSanitationData();
      }
    } catch (e) {
      console.error('Failed to update waste status', e);
    }
  };

  const resetToiletForm = () => {
    setToiletName('');
    setToiletLocation('');
    setGenderType('Unisex');
    setCleanlinessScore(90);
    setHasWater(true);
  };

  const resetWasteForm = () => {
    setWasteLocation('');
    setWasteType('Overflowing Bin');
    setWasteDescription('');
    setSelectedFile(null);
    setImagePreview(null);
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 rounded-3xl bg-[#131B2E] border border-teal-500/40 shadow-2xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-teal-500/20 border border-teal-500/40 flex items-center justify-center text-teal-400">
            <Trash2 size={28} />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-white">
              {t('स्वच्छतागृह व कचरा व्यवस्थापन (Sanitation Hub)', 'Sanitation & Mobile Toilets Hub')}
            </h1>
            <p className="text-xs text-slate-300 font-medium">
              {t('मोबाईल स्वच्छतागृहे, पाणी स्थिती, कचरा तक्रार व नगरपालिका व्यवस्थापन', 'Real-time light map of toilets, cleanup reports & municipal management')}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setAddToiletModalOpen(true)}
            className="px-4 py-2.5 bg-purple-600 hover:bg-purple-500 text-white font-extrabold text-xs rounded-xl shadow-lg flex items-center gap-2 transition-all"
          >
            <Plus size={16} />
            <span>{t('+ स्वच्छतागृह जोडा', '+ Add Toilet')}</span>
          </button>

          <button
            onClick={() => setReportWasteModalOpen(true)}
            className="px-4 py-2.5 bg-teal-600 hover:bg-teal-500 text-white font-extrabold text-xs rounded-xl shadow-lg flex items-center gap-2 transition-all"
          >
            <AlertTriangle size={16} />
            <span>{t('कचरा तक्रार करा', 'Report Waste Issue')}</span>
          </button>
        </div>
      </div>

      {/* Light Theme Map Container */}
      <div className="bg-[#131B2E] border border-white/10 rounded-3xl p-4 flex flex-col shadow-xl min-h-[380px] relative overflow-hidden">
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-teal-400 animate-pulse" />
              <h3 className="text-xs font-black text-white uppercase tracking-wider">
                {t('लाइट थीम नकाशा (Click Map to Drop Pin)', 'Light GIS Map — Click Anywhere to Drop Pin')}
              </h3>
            </div>
            
            {/* Map Tab Filter */}
            <div className="flex items-center gap-1 bg-[#0B0F19] p-1 rounded-xl border border-white/10 text-xs">
              <button
                onClick={() => setActiveTab('TOILETS')}
                className={`px-3 py-1 font-bold rounded-lg transition-all ${
                  activeTab === 'TOILETS' ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-white'
                }`}
              >
                🚽 Toilets ({toilets.length})
              </button>
              <button
                onClick={() => setActiveTab('WASTE')}
                className={`px-3 py-1 font-bold rounded-lg transition-all ${
                  activeTab === 'WASTE' ? 'bg-teal-600 text-white shadow' : 'text-slate-400 hover:text-white'
                }`}
              >
                🚨 Waste Reports ({wasteReports.length})
              </button>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={fitAllMapPins}
              className="px-2.5 py-1.5 rounded-lg bg-teal-500/20 hover:bg-teal-500/30 text-teal-300 font-bold text-xs flex items-center gap-1 transition-all border border-teal-500/30"
              title="Fit All Map Pins"
            >
              <Maximize2 size={13} />
              <span>Fit Pins</span>
            </button>

            <button
              onClick={fetchSanitationData}
              className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 transition-all border border-white/10"
              title="Refresh Sanitation Data"
            >
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            </button>
          </div>
        </div>

        {/* Light Map Canvas */}
        <div className="w-full h-[320px] rounded-2xl overflow-hidden relative border border-white/10 bg-[#f8fafc]">
          <div ref={mapRef} className="w-full h-full z-0" />

          {/* Toast Notification */}
          <AnimatePresence>
            {toastMessage && (
              <motion.div
                initial={{ opacity: 0, y: -15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -15 }}
                className="absolute top-4 left-1/2 -translate-x-1/2 z-30 px-4 py-2 rounded-xl bg-[#0F1420]/95 border border-teal-500/40 text-xs font-bold text-white shadow-2xl backdrop-blur-xl"
              >
                {toastMessage}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Main Content Grid: Toilets vs Waste Reports Management */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Public Toilets List */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-purple-500/30 space-y-4 shadow-xl">
          <div className="flex justify-between items-center pb-3 border-b border-white/10">
            <h3 className="font-extrabold text-white text-base flex items-center gap-2">
              <Bath className="text-purple-400" size={20} />
              <span>{t('सार्वजनिक मोबाईल स्वच्छतागृहे', 'Public Toilet Facilities')}</span>
            </h3>
            <span className="px-2.5 py-0.5 rounded bg-purple-500/20 text-purple-300 font-extrabold text-[10px]">
              {toilets.length} स्थाने
            </span>
          </div>

          <div className="space-y-3.5 max-h-[500px] overflow-y-auto pr-1 custom-scrollbar">
            {toilets.length === 0 ? (
              <div className="p-8 rounded-2xl bg-[#0B0F19] text-center text-slate-400 text-xs">
                कोणतेही स्वच्छतागृह नोंदवलेले नाही. No public toilets listed yet.
              </div>
            ) : (
              toilets.map(toilet => (
                <div key={toilet.id} className="p-4 rounded-2xl bg-[#0B0F19] border border-white/10 space-y-3 text-xs">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="font-black text-white text-sm block">{toilet.name}</span>
                      <span className="text-slate-400 text-[11px] flex items-center gap-1 mt-0.5">
                        <MapPin size={12} className="text-purple-400" /> {toilet.location}
                      </span>
                    </div>
                    <span className="px-2.5 py-1 rounded-lg font-extrabold text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      {toilet.cleanliness_score}% Clean
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-[11px] text-slate-300">
                    <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-bold">
                      {toilet.gender_type}
                    </span>
                    {toilet.is_water_available && (
                      <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-bold">
                        Continuous Water ✓
                      </span>
                    )}
                    <button
                      onClick={() => {
                        if (googleMapObj.current) {
                          googleMapObj.current.panTo({ lat: toilet.latitude, lng: toilet.longitude });
                          googleMapObj.current.setZoom(15);
                        }
                      }}
                      className="px-2.5 py-1 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 font-bold text-[11px] flex items-center gap-1 transition-all border border-purple-500/30 ml-auto"
                    >
                      <MapPin size={12} />
                      <span>View on Map</span>
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Waste Reports & Municipal Dispatch Board */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-teal-500/30 space-y-4 shadow-xl">
          <div className="flex justify-between items-center pb-3 border-b border-white/10">
            <h3 className="font-extrabold text-white text-base flex items-center gap-2">
              <AlertTriangle className="text-teal-400" size={20} />
              <span>{t('कचरा तक्रारी व नगरपालिका व्यवस्थापन', 'Waste Reports & Municipal Control')}</span>
            </h3>
            <span className="px-2.5 py-0.5 rounded bg-teal-500/20 text-teal-300 font-extrabold text-[10px]">
              {wasteReports.length} तक्रारी
            </span>
          </div>

          <div className="space-y-3.5 max-h-[500px] overflow-y-auto pr-1 custom-scrollbar">
            {wasteReports.length === 0 ? (
              <div className="p-8 rounded-2xl bg-[#0B0F19] text-center text-slate-400 text-xs">
                कोणतीही तक्रार नाही. No waste reports.
              </div>
            ) : (
              wasteReports.map(report => (
                <div key={report.id} className="p-4 rounded-2xl bg-[#0B0F19] border border-white/10 space-y-3 text-xs">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="font-black text-white text-sm block">{report.location_name}</span>
                      <span className="text-teal-400 text-[11px] font-bold">{report.waste_type}</span>
                    </div>
                    <span className={`px-2.5 py-1 rounded-lg font-extrabold text-[10px] ${
                      report.status === 'CLEANED' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                      report.status === 'CLEANING_DISPATCHED' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                      'bg-orange-500/20 text-orange-300 border border-orange-500/30'
                    }`}>
                      {report.status}
                    </span>
                  </div>

                  {report.description && (
                    <p className="text-slate-300 bg-white/5 p-2 rounded-lg text-[11px]">
                      "{report.description}"
                    </p>
                  )}

                  {(report.image_url || report.image) && (
                    <div className="p-2 rounded-xl bg-white/5 border border-white/10 flex items-center gap-3">
                      <img 
                        src={report.image_url || report.image} 
                        alt="Waste Attachment" 
                        className="w-12 h-12 object-cover rounded-lg border border-white/10" 
                      />
                      <div>
                        <span className="text-cyan-300 text-[11px] font-bold block">📷 Attached Photo (S3/Media)</span>
                        <a 
                          href={report.image_url || report.image} 
                          target="_blank" 
                          rel="noreferrer"
                          className="text-[10px] text-slate-400 hover:text-white underline"
                        >
                          View Full Image
                        </a>
                      </div>
                    </div>
                  )}

                  {/* Municipal Manager Status Control Actions */}
                  <div className="pt-2 border-t border-white/10 flex items-center justify-between text-[11px]">
                    <button
                      onClick={() => {
                        if (googleMapObj.current) {
                          googleMapObj.current.panTo({ lat: report.latitude, lng: report.longitude });
                          googleMapObj.current.setZoom(15);
                        }
                      }}
                      className="px-2.5 py-1 rounded-lg bg-teal-500/20 hover:bg-teal-500/30 text-teal-300 font-bold text-[11px] flex items-center gap-1 transition-all border border-teal-500/30"
                    >
                      <MapPin size={12} />
                      <span>View on Map</span>
                    </button>

                    <div className="flex items-center gap-1.5">
                      <span className="text-[11px] text-slate-400 font-bold">Status:</span>
                      <select
                        value={report.status}
                        onChange={(e) => handleUpdateWasteStatus(report.id, e.target.value)}
                        className="px-2.5 py-1 rounded-xl bg-[#1E293B] border border-white/20 text-white text-xs font-bold outline-none focus:border-teal-400 cursor-pointer"
                      >
                        <option value="PENDING">🟠 PENDING (Pending Dispatch)</option>
                        <option value="CLEANING_DISPATCHED">🔵 CLEANING DISPATCHED (Crew Dispatched)</option>
                        <option value="CLEANED">🟢 CLEANED (Resolved & Cleaned)</option>
                      </select>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

      {/* Modal 1: Add Public Toilet */}
      {addToiletModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-3xl bg-[#0F172A] border-2 border-purple-500/40 text-white space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-3 border-b border-white/10">
              <h3 className="font-extrabold text-base flex items-center gap-2">
                <Plus size={18} className="text-purple-400" />
                <span>{t('नवीन सार्वजनिक स्वच्छतागृह नोंदवा', 'Register New Public Toilet')}</span>
              </h3>
              <button onClick={() => setAddToiletModalOpen(false)} className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-slate-400 hover:text-white">✕</button>
            </div>

            <form onSubmit={handleAddToiletSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block font-bold text-slate-300 mb-1">Name *</label>
                <input
                  required
                  type="text"
                  value={toiletName}
                  onChange={e => setToiletName(e.target.value)}
                  placeholder="e.g. Alandi Gate 1 Mobile Toilet"
                  className="w-full p-2.5 rounded-xl bg-white/5 border border-white/15 text-white outline-none focus:border-purple-400"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-300 mb-1">Location Landmark *</label>
                <input
                  required
                  type="text"
                  value={toiletLocation}
                  onChange={e => setToiletLocation(e.target.value)}
                  placeholder="e.g. Near Alandi Bus Stand"
                  className="w-full p-2.5 rounded-xl bg-white/5 border border-white/15 text-white outline-none focus:border-purple-400"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-300 mb-1">Gender Access</label>
                  <select
                    value={genderType}
                    onChange={e => setGenderType(e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-[#1E293B] border border-white/15 text-white outline-none"
                  >
                    <option value="Unisex">Unisex</option>
                    <option value="Male">Male Only</option>
                    <option value="Female">Female Only</option>
                    <option value="Accessible">Accessible (Disabled)</option>
                  </select>
                </div>

                <div>
                  <label className="block font-bold text-slate-300 mb-1">Cleanliness Score (%)</label>
                  <input
                    type="number"
                    value={cleanlinessScore}
                    onChange={e => setCleanlinessScore(parseInt(e.target.value) || 85)}
                    className="w-full p-2.5 rounded-xl bg-white/5 border border-white/15 text-white outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-300 mb-1">Latitude</label>
                  <input
                    type="number"
                    step="any"
                    value={toiletLat}
                    onChange={e => setToiletLat(parseFloat(e.target.value) || 0)}
                    className="w-full p-2.5 rounded-xl bg-white/5 border border-white/15 text-white outline-none"
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-300 mb-1">Longitude</label>
                  <input
                    type="number"
                    step="any"
                    value={toiletLng}
                    onChange={e => setToiletLng(parseFloat(e.target.value) || 0)}
                    className="w-full p-2.5 rounded-xl bg-white/5 border border-white/15 text-white outline-none"
                  />
                </div>
              </div>

              <div className="pt-2 flex justify-end gap-2 border-t border-white/10">
                <button
                  type="button"
                  onClick={() => setAddToiletModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-white/5 text-slate-300 font-bold hover:bg-white/10"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-extrabold shadow-lg flex items-center gap-2"
                >
                  {submitting ? <RefreshCw size={14} className="animate-spin" /> : <CheckCircle2 size={14} />}
                  <span>Save Toilet</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal 2: Report Waste Issue with Image Upload */}
      {reportWasteModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-3xl bg-[#0F172A] border-2 border-teal-500/40 text-white space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-3 border-b border-white/10">
              <h3 className="font-extrabold text-base flex items-center gap-2">
                <AlertTriangle size={18} className="text-teal-400" />
                <span>{t('कचरा समस्या तक्रार करा', 'Report Waste / Sanitation Issue')}</span>
              </h3>
              <button onClick={() => setReportWasteModalOpen(false)} className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-slate-400 hover:text-white">✕</button>
            </div>

            <form onSubmit={handleReportWasteSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block font-bold text-slate-300 mb-1">Issue Type *</label>
                <select
                  value={wasteType}
                  onChange={e => setWasteType(e.target.value)}
                  className="w-full p-2.5 rounded-xl bg-[#1E293B] border border-white/15 text-white outline-none"
                >
                  <option value="Overflowing Bin">Overflowing Bin</option>
                  <option value="Plastic Waste Accumulation">Plastic Waste Accumulation</option>
                  <option value="Unhygienic Public Toilet">Unhygienic Public Toilet</option>
                  <option value="Organic Waste / Food Remnants">Organic Waste / Food Remnants</option>
                  <option value="Sewage / Water Leakage">Sewage / Water Leakage</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-300 mb-1">Location Name *</label>
                <input
                  required
                  type="text"
                  value={wasteLocation}
                  onChange={e => setWasteLocation(e.target.value)}
                  placeholder="e.g. Alandi Gate 2 Tea Stalls"
                  className="w-full p-2.5 rounded-xl bg-white/5 border border-white/15 text-white outline-none focus:border-teal-400"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-300 mb-1">Description</label>
                <textarea
                  rows={2}
                  value={wasteDescription}
                  onChange={e => setWasteDescription(e.target.value)}
                  placeholder="e.g. Bins overflowing, requires urgent clearing."
                  className="w-full p-2.5 rounded-xl bg-white/5 border border-white/15 text-white outline-none focus:border-teal-400"
                />
              </div>

              {/* Photo Upload to S3 / Backend */}
              <div>
                <label className="block font-bold text-slate-300 mb-1">
                  Upload Photo (Optional — Saved to AWS S3)
                </label>
                <div className="flex items-center gap-3">
                  <label className="cursor-pointer px-3 py-2 bg-white/10 hover:bg-white/15 rounded-xl border border-white/15 flex items-center gap-2 text-slate-200 text-xs font-bold transition-all">
                    <Camera size={15} className="text-teal-400" />
                    <span>Choose Image File</span>
                    <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
                  </label>
                  {selectedFile && (
                    <span className="text-[11px] text-teal-300 font-bold truncate max-w-[150px]">
                      ✓ {selectedFile.name}
                    </span>
                  )}
                </div>
                {imagePreview && (
                  <div className="mt-2 p-2 rounded-xl bg-white/5 border border-teal-500/30 flex items-center gap-2">
                    <img src={imagePreview} alt="Preview" className="w-10 h-10 object-cover rounded-lg" />
                    <span className="text-[10px] text-slate-300 font-bold">Image ready for upload</span>
                  </div>
                )}
              </div>

              <div className="pt-2 flex justify-end gap-2 border-t border-white/10">
                <button
                  type="button"
                  onClick={() => setReportWasteModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-white/5 text-slate-300 font-bold hover:bg-white/10"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-extrabold shadow-lg flex items-center gap-2"
                >
                  {submitting ? <RefreshCw size={14} className="animate-spin" /> : <CheckCircle2 size={14} />}
                  <span>Submit Report</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
