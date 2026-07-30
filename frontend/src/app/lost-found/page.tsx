"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, QrCode, Plus, ChevronRight, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import dynamic from 'next/dynamic';
const GoogleMapContainer = dynamic(() => import('@/components/maps/GoogleMapContainer'), { ssr: false });
import { lostFoundService } from '@/lib/api';

export default function LostFoundPage() {
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [items, setItems] = useState<any[]>([
    { id: '1', title: 'Black Leather Wallet with Aadhaar Card', category: 'Wallet / ID', location: 'Alandi Camp Beta', status: 'FOUND', qr_claim_code: 'WM-LF-99201' },
    { id: '2', title: 'Samsung Galaxy Smartphone (Blue)', category: 'Electronics', location: 'Pune Sector 3', status: 'REPORTED', qr_claim_code: 'WM-LF-99202' },
  ]);
  const [statusMsg, setStatusMsg] = useState('');

  useEffect(() => {
    lostFoundService.getItems()
      .then(res => {
        const data = Array.isArray(res.data) ? res.data : res.data.results || [];
        if (data.length > 0) setItems(data);
      })
      .catch(() => {});
  }, []);

  return (
    <div className="relative w-full h-[calc(100vh-4rem)] overflow-hidden bg-[#05080F]">
      {/* INTERACTIVE MAP BACKDROP */}
      <GoogleMapContainer activeRole="Digital Lost & Found Command Center" />

      {/* TOP HEADER OVERLAY */}
      <div className="absolute top-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-4 pointer-events-none">
        <div className="pointer-events-auto bg-[#0F1420]/90 backdrop-blur-2xl border border-cyan-500/40 px-4 py-2.5 rounded-2xl shadow-2xl flex items-center gap-3.5 max-w-full">
          <div className="p-2 bg-cyan-500/20 text-cyan-400 rounded-xl">
            <Search size={20} />
          </div>
          <div>
            <p className="text-white font-extrabold text-xs tracking-tight flex items-center gap-2">
              <span>हरवलेल्या वस्तू व व्यक्ती केंद्र (DIGITAL LOST & FOUND)</span>
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            </p>
            <p className="text-slate-400 text-[10px]">QR Claim Verification • Police & Volunteer Escalation</p>
          </div>
        </div>

        <div className="pointer-events-auto flex items-center gap-2">
          <button className="px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-cyan-500/30 transition-all flex items-center gap-2 active:scale-95">
            <Plus size={16} />
            <span>Report Lost / Found Item</span>
          </button>
        </div>
      </div>

      {/* RIGHT SIDE DRAWER: Items Feed & Verification */}
      <AnimatePresence>
        <motion.div
          initial={{ x: 340, opacity: 0 }}
          animate={{ x: drawerOpen ? 0 : 320, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 280, damping: 28 }}
          className="absolute top-20 right-4 bottom-6 z-20 w-80 sm:w-96 bg-[#0B0F19]/95 backdrop-blur-2xl border border-cyan-500/30 p-4 rounded-3xl shadow-2xl flex flex-col space-y-4"
        >
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <QrCode size={16} className="text-cyan-400" />
              <div>
                <p className="text-white font-extrabold text-xs">Reported Items & QR Verification</p>
                <p className="text-slate-400 text-[10px]">क्यूआर कोडद्वारे पडताळणी</p>
              </div>
            </div>
            <button 
              onClick={() => setDrawerOpen(!drawerOpen)}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors"
            >
              <ChevronRight size={16} className={`transition-transform duration-300 ${drawerOpen ? '' : 'rotate-180'}`} />
            </button>
          </div>

          {/* Items Feed */}
          <div className="space-y-2.5 flex-1 overflow-y-auto pr-1">
            {items.map(item => (
              <div key={item.id} className="p-3.5 rounded-2xl bg-[#131B2E] border border-white/10 space-y-2 text-xs">
                <div className="flex justify-between items-center">
                  <span className="font-extrabold text-white text-xs">{item.title}</span>
                  <span className={`px-2 py-0.5 rounded text-[9px] font-extrabold ${
                    item.status === 'FOUND' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
                  }`}>
                    {item.status}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400">Category: {item.category} • Location: {item.location}</p>
                <div className="pt-2 border-t border-white/10 flex justify-between items-center">
                  <span className="text-[10px] text-cyan-400 font-mono font-bold">QR: {item.qr_claim_code}</span>
                  <button className="text-[10px] bg-cyan-600 hover:bg-cyan-500 text-white px-2.5 py-1 rounded-lg font-bold transition-colors">
                    Verify Claim
                  </button>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
