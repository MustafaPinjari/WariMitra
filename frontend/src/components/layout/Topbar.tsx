"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Bell, Search, UserCircle, LogOut, ChevronDown, ShieldCheck, Flag } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Topbar() {
  const router = useRouter();
  const [user, setUser] = useState<{ username: string; role: string; title: string } | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('warimitra_user');
    if (saved) {
      try {
        setUser(JSON.parse(saved));
      } catch (e) {
        setUser(null);
      }
    } else {
      setUser({
        username: 'govt_admin',
        role: 'Govt Admin',
        title: 'Collectorate Office',
      });
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('warimitra_user');
    localStorage.removeItem('warimitra_token');
    document.cookie = 'warimitra_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'warimitra_role=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    setUser(null);
    setDropdownOpen(false);
    router.push('/login');
  };

  return (
    <header className="h-16 bg-[#0B0F19]/90 backdrop-blur-2xl saturate-150 border-b border-orange-500/20 flex items-center justify-between px-4 sm:px-6 lg:px-8 sticky top-0 z-40 w-full shadow-lg">
      {/* Left: Dynamic Responsive Search */}
      <div className="flex items-center gap-4 flex-1 max-w-md">
        <div className="relative w-full">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-orange-400" size={16} />
          <input 
            type="text" 
            placeholder="Search incidents, pilgrims, dindis, resources..." 
            className="w-full pl-10 pr-4 py-2 bg-[#131B2E] border border-white/15 text-white placeholder-slate-400 text-xs rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all"
          />
        </div>
      </div>

      {/* Center: Maharashtra Govt Wari Badge */}
      <div className="hidden xl:flex items-center gap-2 px-3 py-1 bg-orange-500/10 border border-orange-500/30 rounded-full">
        <Flag size={13} className="text-orange-400" />
        <span className="text-[11px] font-bold text-orange-300 tracking-wide">महाराष्ट्र शासन • पंढरपूर वारी मिशन कंट्रोल</span>
      </div>
      
      {/* Right: Notifications & Profile */}
      <div className="flex items-center gap-3 sm:gap-5">
        <button className="relative p-2 text-slate-300 hover:bg-white/10 hover:text-white rounded-xl transition-colors">
          <Bell size={18} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full shadow-[0_0_8px_rgba(239,68,68,0.9)] animate-pulse" />
        </button>

        {/* User Profile & Popover */}
        <div className="relative">
          <div 
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2.5 pl-4 border-l border-white/10 cursor-pointer group select-none"
          >
            <div className="text-right hidden sm:block">
              <p className="text-xs font-bold text-white tracking-tight group-hover:text-orange-400 transition-colors">
                {user ? user.role : 'Govt Admin'}
              </p>
              <p className="text-[10px] text-slate-400">{user ? user.title : 'Collectorate Office'}</p>
            </div>
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-orange-600 to-amber-500 border border-orange-400/50 flex items-center justify-center text-white shadow-md group-hover:scale-105 transition-transform">
              <UserCircle size={20} />
            </div>
            <ChevronDown size={14} className={`text-slate-400 transition-transform duration-200 ${dropdownOpen ? 'rotate-180' : ''}`} />
          </div>

          {/* Dropdown Menu */}
          <AnimatePresence>
            {dropdownOpen && (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 mt-3 w-60 bg-[#0F1420] border border-orange-500/30 p-2.5 rounded-2xl shadow-2xl z-50 space-y-1.5"
              >
                <div className="p-3 bg-orange-500/10 rounded-xl border border-orange-500/20">
                  <p className="text-xs font-extrabold text-white flex items-center gap-1.5">
                    <ShieldCheck size={14} className="text-emerald-400" />
                    {user?.username || 'govt_admin'}
                  </p>
                  <p className="text-[10px] text-slate-300 mt-0.5">{user?.role || 'Govt Admin'}</p>
                </div>

                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-bold text-red-400 hover:bg-red-500/10 rounded-xl transition-colors text-left"
                >
                  <LogOut size={15} />
                  <span>Log Out of Portal</span>
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
}
