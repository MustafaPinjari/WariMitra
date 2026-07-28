"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  HeartHandshake, 
  Package, 
  Plus, 
  ChevronRight,
  Droplets,
  UtensilsCrossed,
  AlertTriangle
} from 'lucide-react';
import GoogleMapContainer from '@/components/maps/GoogleMapContainer';
import { ngoService } from '@/lib/api';

export default function NGOSupplyChainPage() {
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [tankerCount, setTankerCount] = useState(12);

  useEffect(() => {
    ngoService.getWaterTankers()
      .then(res => {
        if (res.data) setTankerCount(res.data.length || 12);
      })
      .catch(() => {});
  }, []);

  return (
    <div className="relative w-full h-[calc(100vh-4rem)] overflow-hidden bg-[#05080F]">
      {/* INTERACTIVE MAP BACKDROP */}
      <GoogleMapContainer activeRole="NGO Relief Supply Chain & Tanker Tracking" />

      {/* TOP HEADER OVERLAY */}
      <div className="absolute top-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-4 pointer-events-none">
        <div className="pointer-events-auto bg-[#0F1420]/90 backdrop-blur-2xl border border-pink-500/40 px-4 py-2.5 rounded-2xl shadow-2xl flex items-center gap-3.5 max-w-full">
          <div className="p-2 bg-pink-500/20 text-pink-400 rounded-xl">
            <HeartHandshake size={20} />
          </div>
          <div>
            <p className="text-white font-extrabold text-xs tracking-tight flex items-center gap-2">
              <span>अन्न व निवारा सेवा (NGO RELIEF SUPPLY)</span>
              <span className="w-2 h-2 rounded-full bg-pink-400 animate-pulse" />
            </p>
            <p className="text-slate-400 text-[10px]">
              {tankerCount} Water Tankers Active • 8 Food Kitchens • 1 Refill Alert
            </p>
          </div>
        </div>

        <div className="pointer-events-auto">
          <button className="px-4 py-2.5 bg-pink-600 hover:bg-pink-500 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-pink-500/30 transition-all flex items-center gap-2 active:scale-95">
            <Plus size={16} />
            <span>Dispatch Water Tanker / Relief Truck</span>
          </button>
        </div>
      </div>

      {/* RIGHT SIDE DRAWER: Supply Stock & Inventory */}
      <AnimatePresence>
        <motion.div
          initial={{ x: 340, opacity: 0 }}
          animate={{ x: drawerOpen ? 0 : 320, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 280, damping: 28 }}
          className="absolute top-20 right-4 bottom-6 z-20 w-80 sm:w-96 bg-[#0B0F19]/95 backdrop-blur-2xl border border-pink-500/30 p-4 rounded-3xl shadow-2xl flex flex-col space-y-4"
        >
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Package size={16} className="text-pink-400" />
              <div>
                <p className="text-white font-extrabold text-xs">Live Inventory & Supply Fleet</p>
                <p className="text-slate-400 text-[10px]">अन्न व निवारा पुरवठा ट्रॅकिंग</p>
              </div>
            </div>
            <button 
              onClick={() => setDrawerOpen(!drawerOpen)}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors"
            >
              <ChevronRight size={16} className={`transition-transform duration-300 ${drawerOpen ? '' : 'rotate-180'}`} />
            </button>
          </div>

          {/* Active Refill Alert Banner */}
          <div className="p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-slate-200 space-y-2">
            <div className="flex justify-between items-center">
              <span className="font-extrabold text-xs text-amber-300 flex items-center gap-1.5">
                <AlertTriangle size={14} className="text-amber-400" />
                Station 2 — Saswad Corridor
              </span>
              <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-extrabold text-[9px]">REFILL ALERT</span>
            </div>
            <p className="text-xs text-slate-300">ORS Water Packets down to 12% stock. Tanker #WT-04 dispatched.</p>
          </div>

          {/* Inventory Distribution Stream */}
          <div className="space-y-2 flex-1 overflow-y-auto pr-1">
            <p className="text-slate-400 text-[10px] font-bold uppercase tracking-wider">Field Distribution Hubs</p>

            <div className="p-3 rounded-2xl bg-[#131B2E] border border-white/10 flex justify-between items-center text-xs">
              <div className="flex items-center gap-2.5">
                <Droplets size={16} className="text-blue-400" />
                <div>
                  <p className="font-bold text-white">500ml Water Packets</p>
                  <p className="text-[10px] text-blue-400 font-bold">50,000 Packets Stock</p>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">Abundant</span>
            </div>

            <div className="p-3 rounded-2xl bg-[#131B2E] border border-white/10 flex justify-between items-center text-xs">
              <div className="flex items-center gap-2.5">
                <UtensilsCrossed size={16} className="text-orange-400" />
                <div>
                  <p className="font-bold text-white">Annadhana Meal Thalis</p>
                  <p className="text-[10px] text-orange-400 font-bold">10,000 Meals Active</p>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">Serving</span>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
