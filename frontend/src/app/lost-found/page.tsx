"use client";

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, QrCode, Plus, AlertTriangle, MapPin, Camera, CheckCircle2, RefreshCw, UserCheck, ShieldCheck, Tag, Phone } from 'lucide-react';
import { useAccessibility } from '@/components/providers/AccessibilityProvider';

const API_BASE = 'http://127.0.0.1:8000/api/v1';

export default function LostFoundPage() {
  const { t } = useAccessibility();
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [reportType, setReportType] = useState<'ITEM' | 'PERSON'>('ITEM');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  // Live Data lists
  const [lostItems, setLostItems] = useState<any[]>([]);
  const [missingPersons, setMissingPersons] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Form State
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Bag');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [personAge, setPersonAge] = useState('');
  
  // Dummy Image Upload State
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageFileName, setImageFileName] = useState<string>('');

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [itemsRes, personsRes] = await Promise.all([
        fetch(`${API_BASE}/lost-found/items/`).then(res => res.json()).catch(() => []),
        fetch(`${API_BASE}/missing-person/reports/`).then(res => res.json()).catch(() => []),
      ]);

      const itemsList = Array.isArray(itemsRes) ? itemsRes : (itemsRes.results || []);
      const personsList = Array.isArray(personsRes) ? personsRes : (personsRes.results || []);

      setLostItems(itemsList);
      setMissingPersons(personsList);
    } catch (e) {
      console.error("Failed to load Lost & Found data", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  const handleImagePick = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFileName(file.name);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      if (reportType === 'ITEM') {
        const payload = {
          title,
          category,
          description,
          location,
          contact_phone: contactPhone,
          image_url: imagePreview || '',
        };

        const res = await fetch(`${API_BASE}/lost-found/items/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        if (res.ok) {
          setSubmitted(true);
          resetForm();
          fetchAllData();
        }
      } else {
        const payload = {
          name: title,
          age: parseInt(personAge) || 0,
          category: category === 'Bag' ? 'Child' : category,
          description,
          last_seen_location: location,
          contact_mobile: contactPhone,
          photo_url: imagePreview || '',
        };

        const res = await fetch(`${API_BASE}/missing-person/reports/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        if (res.ok) {
          setSubmitted(true);
          resetForm();
          fetchAllData();
        }
      }
    } catch (err) {
      console.error("Failed to submit report", err);
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setTitle('');
    setDescription('');
    setLocation('');
    setContactPhone('');
    setPersonAge('');
    setImagePreview(null);
    setImageFileName('');
    setTimeout(() => {
      setSubmitted(false);
      setReportModalOpen(false);
    }, 2000);
  };

  // Staff Action: Update Lost Item Status
  const handleUpdateItemStatus = async (itemId: string, newStatus: string) => {
    try {
      const res = await fetch(`${API_BASE}/lost-found/items/${itemId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) {
        fetchAllData();
      }
    } catch (e) {
      console.error("Failed to update status", e);
    }
  };

  // Staff Action: Update Missing Person Status
  const handleUpdatePersonStatus = async (personId: string, newStatus: string) => {
    try {
      const res = await fetch(`${API_BASE}/missing-person/reports/${personId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) {
        fetchAllData();
      }
    } catch (e) {
      console.error("Failed to update status", e);
    }
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 rounded-3xl bg-[#131B2E] border border-cyan-500/40 shadow-2xl">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
            <Search size={28} />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-white flex items-center gap-2">
              <span>{t('हरवलेले व्यक्ती व वस्तू केंद्र', 'Lost & Found Hub')}</span>
              <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 text-xs font-bold border border-cyan-500/30">Live Sync</span>
            </h1>
            <p className="text-xs text-slate-300 font-medium">
              {t('हरवलेल्या व्यक्तींचा व वस्तूंचा तात्काळ शोध, व्यवस्थापन व मोबाईल अ‍ॅप अपडेट्स', 'Real-time search, staff resolution & app sync for missing persons & belongings')}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchAllData}
            className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition-all border border-slate-700"
            title="Refresh List"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
          <button
            onClick={() => setReportModalOpen(true)}
            className="px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-cyan-500/30 transition-all flex items-center gap-2"
          >
            <Plus size={16} />
            <span>{t('हरवलेले / सापडलेले नोंदवा', 'Report Lost / Found')}</span>
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Missing Persons Management Board */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-amber-500/30 space-y-4 shadow-xl">
          <div className="flex justify-between items-center pb-3 border-b border-white/10">
            <h3 className="font-extrabold text-white text-base flex items-center gap-2">
              <AlertTriangle className="text-amber-400" size={20} />
              <span>{t('हरवलेले व्यक्ती शोध व्यवस्थापन', 'Missing Persons Feed & Resolution')}</span>
            </h3>
            <span className="px-2.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-extrabold text-[10px]">
              {missingPersons.length} नोंदी
            </span>
          </div>

          <div className="space-y-3.5 max-h-[550px] overflow-y-auto pr-1 custom-scrollbar">
            {loading ? (
              <div className="text-center py-8 text-slate-400 text-xs font-bold animate-pulse">
                लोड होत आहे... Loading missing reports...
              </div>
            ) : missingPersons.length === 0 ? (
              <div className="p-8 rounded-2xl bg-[#0B0F19] text-center text-slate-400 text-xs">
                कोणतीही हरवलेल्या व्यक्तीची नोंद नाही. No active missing person reports.
              </div>
            ) : (
              missingPersons.map(person => (
                <div key={person.id} className="p-4 rounded-2xl bg-[#0B0F19] border border-white/10 space-y-3 text-xs">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="font-black text-white text-sm block">{person.name}</span>
                      <span className="text-slate-400 text-[11px]">
                        वयोगट: {person.age ? `${person.age} वर्षे` : 'N/A'} • श्रेणी: {person.category}
                      </span>
                    </div>
                    <span className={`px-2.5 py-1 rounded-lg font-extrabold text-[10px] ${
                      person.status === 'Found' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                      person.status === 'Closed' ? 'bg-slate-700 text-slate-300' :
                      'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    }`}>
                      {person.status === 'Found' ? '✓ सापडला (FOUND)' : person.status === 'Closed' ? 'बंद (CLOSED)' : '🔍 शोध सुरू (SEARCHING)'}
                    </span>
                  </div>

                  {person.photo_url && (
                    <div className="flex items-center gap-2 p-2 rounded-xl bg-white/5 border border-white/10">
                      <Camera size={14} className="text-cyan-400" />
                      <span className="text-[11px] text-cyan-300 font-bold truncate">📸 Photo attached</span>
                    </div>
                  )}

                  {person.last_seen_location && (
                    <p className="text-slate-300 flex items-center gap-1.5">
                      <MapPin size={13} className="text-amber-400 shrink-0" />
                      <span>शेवटचे स्थान: {person.last_seen_location}</span>
                    </p>
                  )}

                  {person.description && (
                    <p className="text-slate-400 italic bg-white/5 p-2 rounded-lg text-[11px]">
                      "{person.description}"
                    </p>
                  )}

                  {/* Staff Management Action Bar (Website Manager) */}
                  <div className="pt-2.5 border-t border-white/10 flex flex-wrap items-center justify-between gap-2">
                    <span className="text-[10px] text-slate-400">
                      संपर्क: {person.contact_mobile || 'N/A'}
                    </span>

                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] text-slate-400 font-bold mr-1">अधिकारी कृती:</span>
                      <button
                        onClick={() => handleUpdatePersonStatus(person.id, 'Found')}
                        disabled={person.status === 'Found'}
                        className="px-2.5 py-1 bg-emerald-600/80 hover:bg-emerald-500 disabled:opacity-40 text-white font-extrabold text-[10px] rounded-lg transition-all"
                      >
                        ✓ सापडला (Mark Found)
                      </button>
                      <button
                        onClick={() => handleUpdatePersonStatus(person.id, 'Closed')}
                        disabled={person.status === 'Closed'}
                        className="px-2.5 py-1 bg-slate-700 hover:bg-slate-600 disabled:opacity-40 text-slate-200 font-bold text-[10px] rounded-lg transition-all"
                      >
                        बंद (Close)
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Lost & Found Items Management Board */}
        <div className="p-6 rounded-3xl bg-[#131B2E] border border-cyan-500/30 space-y-4 shadow-xl">
          <div className="flex justify-between items-center pb-3 border-b border-white/10">
            <h3 className="font-extrabold text-white text-base flex items-center gap-2">
              <Tag className="text-cyan-400" size={20} />
              <span>{t('हरवलेल्या वस्तू रजिस्टर व क्यूआर पडताळणी', 'Lost Items & QR Claims')}</span>
            </h3>
            <span className="px-2.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-extrabold text-[10px]">
              {lostItems.length} वस्तू
            </span>
          </div>

          <div className="space-y-3.5 max-h-[550px] overflow-y-auto pr-1 custom-scrollbar">
            {loading ? (
              <div className="text-center py-8 text-slate-400 text-xs font-bold animate-pulse">
                लोड होत आहे... Loading items...
              </div>
            ) : lostItems.length === 0 ? (
              <div className="p-8 rounded-2xl bg-[#0B0F19] text-center text-slate-400 text-xs">
                कोणतीही हरवलेल्या वस्तूची नोंद नाही. No reported items yet.
              </div>
            ) : (
              lostItems.map(item => (
                <div key={item.id} className="p-4 rounded-2xl bg-[#0B0F19] border border-white/10 space-y-3 text-xs">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="font-black text-white text-sm block">{item.title}</span>
                      <span className="text-slate-400 text-[11px]">
                        प्रवर्ग: {item.category} • स्थान: {item.location}
                      </span>
                    </div>
                    <span className={`px-2.5 py-1 rounded-lg font-extrabold text-[10px] ${
                      item.status === 'FOUND' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                      item.status === 'RETURNED' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                      'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                    }`}>
                      {item.status === 'FOUND' ? '✓ साठवणूकीत सापडले (FOUND)' :
                       item.status === 'RETURNED' ? '✓ मालकाला दिले (RETURNED)' :
                       'हरवले (REPORTED)'}
                    </span>
                  </div>

                  {item.image_url && (
                    <div className="flex items-center gap-2 p-2 rounded-xl bg-white/5 border border-white/10">
                      <Camera size={14} className="text-cyan-400" />
                      <span className="text-[11px] text-cyan-300 font-bold truncate">📸 Photo attached</span>
                    </div>
                  )}

                  {item.description && (
                    <p className="text-slate-400 italic bg-white/5 p-2 rounded-lg text-[11px]">
                      "{item.description}"
                    </p>
                  )}

                  <div className="pt-2 border-t border-white/10 flex justify-between items-center text-slate-400 text-[11px]">
                    <span className="font-mono text-cyan-400 font-bold flex items-center gap-1">
                      <QrCode size={13} /> {item.qr_claim_code || 'WM-LF-99202'}
                    </span>
                    <span className="flex items-center gap-1">
                      <Phone size={12} /> {item.contact_phone || 'N/A'}
                    </span>
                  </div>

                  {/* Staff Management Action Bar */}
                  <div className="pt-2 border-t border-white/10 flex items-center justify-end gap-1.5">
                    <span className="text-[10px] text-slate-400 font-bold mr-1">व्यवस्थापन:</span>
                    <button
                      onClick={() => handleUpdateItemStatus(item.id, 'FOUND')}
                      disabled={item.status === 'FOUND'}
                      className="px-2 py-1 bg-emerald-600/80 hover:bg-emerald-500 disabled:opacity-40 text-white font-extrabold text-[10px] rounded-lg transition-all"
                    >
                      ✓ सापडले (Found)
                    </button>
                    <button
                      onClick={() => handleUpdateItemStatus(item.id, 'RETURNED')}
                      disabled={item.status === 'RETURNED'}
                      className="px-2 py-1 bg-blue-600/80 hover:bg-blue-500 disabled:opacity-40 text-white font-extrabold text-[10px] rounded-lg transition-all"
                    >
                      परत दिले (Return)
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

      {/* Report Modal */}
      {reportModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-3xl bg-[#0F172A] border-2 border-cyan-500/40 text-white space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-3 border-b border-white/10">
              <h3 className="font-extrabold text-base flex items-center gap-2">
                <Plus size={18} className="text-cyan-400" />
                <span>{t('हरवलेल्या व्यक्ती / वस्तूची नोंदणी', 'Report Missing Person or Item')}</span>
              </h3>
              <button onClick={() => setReportModalOpen(false)} className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-slate-400 hover:text-white">✕</button>
            </div>

            {submitted ? (
              <div className="p-4 rounded-2xl bg-emerald-500/20 text-emerald-300 text-xs font-bold text-center border border-emerald-500/30 space-y-1">
                <p className="text-sm">✓ नोंदणी यशस्वी झाली आहे!</p>
                <p className="text-[11px] text-slate-300">माहिती थेट पोलीस, स्वयंसेवक व मोबाईल अ‍ॅपमध्ये पाठवली गेली आहे.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-3 text-xs">
                
                {/* Type Switcher */}
                <div className="flex rounded-xl bg-white/5 p-1 border border-white/10">
                  <button
                    type="button"
                    onClick={() => setReportType('ITEM')}
                    className={`flex-1 py-1.5 font-bold text-xs rounded-lg transition-all ${
                      reportType === 'ITEM' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    📦 हरवलेली वस्तू (Item)
                  </button>
                  <button
                    type="button"
                    onClick={() => setReportType('PERSON')}
                    className={`flex-1 py-1.5 font-bold text-xs rounded-lg transition-all ${
                      reportType === 'PERSON' ? 'bg-amber-600 text-white shadow' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    👤 हरवलेली व्यक्ती (Person)
                  </button>
                </div>

                <div>
                  <label className="block font-bold text-slate-300 mb-1">
                    {reportType === 'ITEM' ? 'वस्तूचे नाव • Title *' : 'व्यक्तीचे नाव • Full Name *'}
                  </label>
                  <input
                    required
                    type="text"
                    value={title}
                    onChange={e => setTitle(e.target.value)}
                    placeholder={reportType === 'ITEM' ? 'उदा. काळे पाकीट / सॅक' : 'उदा. अनिश जाधव'}
                    className="w-full p-2.5 rounded-xl bg-white/5 border border-white/15 text-white outline-none focus:border-cyan-400"
                  />
                </div>

                {reportType === 'PERSON' && (
                  <div>
                    <label className="block font-bold text-slate-300 mb-1">वय • Age</label>
                    <input
                      type="number"
                      value={personAge}
                      onChange={e => setPersonAge(e.target.value)}
                      placeholder="उदा. 8"
                      className="w-full p-2.5 rounded-xl bg-white/5 border border-white/15 text-white outline-none focus:border-cyan-400"
                    />
                  </div>
                )}

                <div>
                  <label className="block font-bold text-slate-300 mb-1">श्रेणी • Category</label>
                  <select
                    value={category}
                    onChange={e => setCategory(e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-[#1E293B] border border-white/15 text-white outline-none focus:border-cyan-400"
                  >
                    {reportType === 'ITEM' ? (
                      <>
                        <option value="Bag">सॅक / बॅग (Bag)</option>
                        <option value="Phone">मोबाईल (Phone)</option>
                        <option value="ID Card">ओळखपत्र / कार्ड (ID Card)</option>
                        <option value="Jewellery">दागिने (Jewellery)</option>
                        <option value="Clothing">कपडे (Clothing)</option>
                        <option value="Other">इतर (Other)</option>
                      </>
                    ) : (
                      <>
                        <option value="Child">लहान मुलगा/मुलगी (Child)</option>
                        <option value="Elderly">ज्येष्ठ नागरिक (Elderly)</option>
                        <option value="Adult">वयस्क व्यक्ती (Adult)</option>
                        <option value="Disabled">विशेष व्यक्ती (Disabled)</option>
                      </>
                    )}
                  </select>
                </div>

                <div>
                  <label className="block font-bold text-slate-300 mb-1">स्थान • Last Seen Location *</label>
                  <input
                    required
                    type="text"
                    value={location}
                    onChange={e => setLocation(e.target.value)}
                    placeholder="उदा. सासवड पालखी विसावा तंबू"
                    className="w-full p-2.5 rounded-xl bg-white/5 border border-white/15 text-white outline-none focus:border-cyan-400"
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-300 mb-1">वर्णन • Description</label>
                  <textarea
                    rows={2}
                    value={description}
                    onChange={e => setDescription(e.target.value)}
                    placeholder="उदा. भगवा कुर्ता घातलेला मुलगा..."
                    className="w-full p-2.5 rounded-xl bg-white/5 border border-white/15 text-white outline-none focus:border-cyan-400"
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-300 mb-1">संपर्क नंबर • Contact Mobile</label>
                  <input
                    type="tel"
                    value={contactPhone}
                    onChange={e => setContactPhone(e.target.value)}
                    placeholder="+91 98765 43210"
                    className="w-full p-2.5 rounded-xl bg-white/5 border border-white/15 text-white outline-none focus:border-cyan-400"
                  />
                </div>

                {/* Dummy Image Upload Field */}
                <div>
                  <label className="block font-bold text-slate-300 mb-1">
                    फोटो जोडा (ऐच्छिक) • Upload Photo (Optional Dummy Input)
                  </label>
                  <div className="flex items-center gap-3">
                    <label className="cursor-pointer px-3 py-2 bg-white/10 hover:bg-white/15 rounded-xl border border-white/15 flex items-center gap-2 text-slate-200 text-xs font-bold transition-all">
                      <Camera size={15} className="text-cyan-400" />
                      <span>फोटो निवडा (Select Photo)</span>
                      <input type="file" accept="image/*" onChange={handleImagePick} className="hidden" />
                    </label>
                    {imageFileName && (
                      <span className="text-[11px] text-cyan-300 font-bold truncate max-w-[150px]">
                        ✓ {imageFileName}
                      </span>
                    )}
                  </div>
                  {imagePreview && (
                    <div className="mt-2 p-2 rounded-xl bg-white/5 border border-cyan-500/30 flex items-center gap-2">
                      <img src={imagePreview} alt="Preview" className="w-10 h-10 object-cover rounded-lg" />
                      <span className="text-[10px] text-slate-300 font-bold">Photo preview attached</span>
                    </div>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-extrabold rounded-xl transition-all shadow mt-2 flex items-center justify-center gap-2"
                >
                  {submitting ? (
                    <span>नोंदणी होत आहे... Registering...</span>
                  ) : (
                    <>
                      <CheckCircle2 size={16} />
                      <span>नोंदवा व शोध सुरू करा (Submit Report)</span>
                    </>
                  )}
                </button>
              </form>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
