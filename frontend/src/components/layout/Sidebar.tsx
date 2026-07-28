"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { LayoutDashboard, AlertTriangle, Users, Tent, Shield, Activity, HeartHandshake, ChevronRight, BookOpen, Search, Trash2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Sidebar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(true);
  const [userRole, setUserRole] = useState({ name: 'Govt Admin', role: 'Govt Admin', email: 'admin@warimitra.gov.in' });

  useEffect(() => {
    const saved = localStorage.getItem('warimitra_user');
    if (saved) {
      try {
        const u = JSON.parse(saved);
        setUserRole({
          name: u.username || 'User',
          role: u.role || 'Govt Admin',
          email: `${u.username || 'admin'}@warimitra.gov.in`,
        });
      } catch (e) {}
    }
  }, []);

  const allNavItems = [
    { href: '/', icon: LayoutDashboard, label: 'Overview', marathi: 'मुख्य नियंत्रण', color: '#E85D04', roles: ['Govt Admin', 'Super Admin', 'Medical Officer', 'Police Officer', 'NGO Coordinator', 'Dindi Leader', 'Volunteer'] },
    { href: '/sos', icon: AlertTriangle, label: 'SOS Emergencies', marathi: 'आणीबाणी', color: '#EF4444', roles: ['Govt Admin', 'Super Admin', 'Medical Officer', 'Police Officer', 'NGO Coordinator', 'Dindi Leader', 'Volunteer'] },
    { href: '/crowd', icon: Users, label: 'Crowd Intel', marathi: 'गर्दी व्यवस्थापन', color: '#3B82F6', roles: ['Govt Admin', 'Super Admin', 'Police Officer', 'Dindi Leader', 'Volunteer', 'NGO Coordinator'] },
    { href: '/medical', icon: Activity, label: 'Medical Ops', marathi: 'वैद्यकीय केंद्र', color: '#10B981', roles: ['Govt Admin', 'Super Admin', 'Medical Officer'] },
    { href: '/police', icon: Shield, label: 'Police Security', marathi: 'पोलीस बंदोबस्त', color: '#6366F1', roles: ['Govt Admin', 'Super Admin', 'Police Officer'] },
    { href: '/ngo', icon: HeartHandshake, label: 'NGO Relief', marathi: 'अन्न व निवारा', color: '#EC4899', roles: ['Govt Admin', 'Super Admin', 'NGO Coordinator'] },
    { href: '/temple', icon: Tent, label: 'Temple Queues', marathi: 'दर्शन रांग', color: '#8B5CF6', roles: ['Govt Admin', 'Super Admin'] },
    { href: '/heritage', icon: BookOpen, label: 'Vari Heritage', marathi: 'वारी वारसा', color: '#D97706', roles: ['Govt Admin', 'Super Admin', 'Medical Officer', 'Police Officer', 'NGO Coordinator', 'Dindi Leader', 'Volunteer'] },
    { href: '/lost-found', icon: Search, label: 'Lost & Found', marathi: 'वस्तू व व्यक्ती', color: '#06B6D4', roles: ['Govt Admin', 'Super Admin', 'Medical Officer', 'Police Officer', 'NGO Coordinator', 'Dindi Leader', 'Volunteer'] },
    { href: '/sanitation', icon: Trash2, label: 'Sanitation', marathi: 'स्वच्छता मोहीम', color: '#14B8A6', roles: ['Govt Admin', 'Super Admin', 'Medical Officer', 'Police Officer', 'NGO Coordinator', 'Dindi Leader', 'Volunteer'] },
  ];

  const visibleNavItems = allNavItems.filter(item => 
    item.roles.includes(userRole.role)
  );

  return (
    <>
      {/* Mobile Backdrop */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
            onClick={() => setIsOpen(false)}
          />
        )}
      </AnimatePresence>

      <motion.aside
        initial={false}
        animate={{ width: isOpen ? 250 : 76 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className="bg-[#0B0F19] border-r border-orange-500/20 h-screen fixed left-0 top-0 z-50 flex flex-col py-5 overflow-hidden shadow-2xl"
      >
        {/* Header / Brand */}
        <div className="flex items-center px-4 mb-5 gap-3">
          <div
            className="w-10 h-10 rounded-xl bg-gradient-to-tr from-orange-600 to-amber-500 flex-shrink-0 flex items-center justify-center cursor-pointer shadow-lg shadow-orange-500/30"
            onClick={() => setIsOpen(!isOpen)}
          >
            <span className="text-white font-black text-lg">W</span>
          </div>

          <AnimatePresence>
            {isOpen && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.18 }}
                className="overflow-hidden whitespace-nowrap"
              >
                <p className="text-white font-extrabold text-base tracking-tight leading-none">वारीमित्र</p>
                <p className="text-orange-400 text-[10px] font-bold uppercase tracking-wider mt-1">{userRole.role}</p>
              </motion.div>
            )}
          </AnimatePresence>

          <button
            onClick={() => setIsOpen(!isOpen)}
            className="ml-auto flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-lg bg-white/5 border border-white/10 text-slate-400 hover:text-white hover:bg-orange-500/20 transition-colors"
          >
            <ChevronRight size={14} className={`transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`} />
          </button>
        </div>

        {/* Navigation items */}
        <nav className="flex-1 w-full flex flex-col gap-1 px-3 overflow-y-auto pr-1">
          {visibleNavItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className="relative flex items-center gap-3.5 h-11 rounded-xl transition-all duration-200 group px-3 select-none flex-shrink-0"
                style={{
                  background: isActive ? `${item.color}20` : 'transparent',
                  border: isActive ? `1px solid ${item.color}40` : '1px solid transparent',
                }}
              >
                {/* Active Indicator Bar */}
                {isActive && (
                  <motion.div
                    layoutId="activeBar"
                    className="absolute left-0 top-2 bottom-2 w-1 rounded-r-full"
                    style={{ background: item.color }}
                    transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
                  />
                )}

                {/* Icon */}
                <div className="flex-shrink-0 w-6 flex items-center justify-center">
                  <Icon
                    size={19}
                    style={{ color: isActive ? item.color : undefined }}
                    className={!isActive ? 'text-slate-400 group-hover:text-white transition-colors' : ''}
                  />
                </div>

                {/* Labels */}
                <AnimatePresence>
                  {isOpen && (
                    <motion.div
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -8 }}
                      transition={{ duration: 0.18 }}
                      className="flex flex-col whitespace-nowrap overflow-hidden"
                    >
                      <span 
                        className={`text-xs font-bold leading-tight transition-colors ${
                          isActive ? 'text-white' : 'text-slate-300 group-hover:text-white'
                        }`}
                      >
                        {item.label}
                      </span>
                      <span className="text-[9px] text-slate-400 font-medium">
                        {item.marathi}
                      </span>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Tooltip when sidebar is collapsed */}
                {!isOpen && (
                  <div className="absolute left-[68px] px-3 py-1.5 bg-[#0F1420] border border-orange-500/30 text-white text-xs font-bold rounded-xl opacity-0 -translate-x-2 pointer-events-none group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200 whitespace-nowrap shadow-2xl z-50">
                    <p>{item.label}</p>
                    <p className="text-[10px] text-orange-400 font-normal">{item.marathi}</p>
                  </div>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Bottom User Profile info */}
        <div className="mt-auto px-3 pt-3 border-t border-white/10 flex-shrink-0">
          <div className="flex items-center gap-3 px-1">
            <div className="w-8 h-8 flex-shrink-0 rounded-lg bg-orange-500/20 border border-orange-500/40 flex items-center justify-center text-orange-400 font-bold text-xs">
              {userRole.role.charAt(0)}
            </div>
            <AnimatePresence>
              {isOpen && (
                <motion.div
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -8 }}
                  transition={{ duration: 0.18 }}
                  className="overflow-hidden"
                >
                  <p className="text-white text-xs font-bold whitespace-nowrap">{userRole.role}</p>
                  <p className="text-slate-400 text-[10px] whitespace-nowrap truncate max-w-[140px]">{userRole.email}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.aside>

      {/* Dynamic spacer */}
      <motion.div
        animate={{ width: isOpen ? 250 : 76 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className="flex-shrink-0 h-screen"
        aria-hidden
      />
    </>
  );
}
