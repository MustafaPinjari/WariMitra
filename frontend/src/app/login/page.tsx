"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Shield, Lock, User, ArrowRight, CheckCircle2, Sparkles, Flag } from 'lucide-react';

const DEMO_ACCOUNTS = [
  { role: 'Govt Admin', username: 'govt_admin', password: 'GovtAdmin@123', desc: 'Collectorate Command Center', marathi: 'जिल्हाधिकारी नियंत्रण', target: '/' },
  { role: 'Super Admin', username: 'superadmin', password: 'WariMitra@2025!', desc: 'Full System Access', marathi: 'मुख्य प्रशासन', target: '/' },
  { role: 'Medical Officer', username: 'medical_officer', password: 'MedOfficer@123', desc: 'Health & Ambulance Ops', marathi: 'वैद्यकीय कक्ष', target: '/medical' },
  { role: 'Police Officer', username: 'police_officer', password: 'Police@1234', desc: 'Traffic & Patrol Security', marathi: 'पोलीस बंदोबस्त', target: '/police' },
  { role: 'NGO Coordinator', username: 'ngo_coord', password: 'NGO@123456', desc: 'Resource & Food Relief', marathi: 'अन्न व निवारा सेवा', target: '/ngo' },
];

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('govt_admin');
  const [password, setPassword] = useState('GovtAdmin@123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const { authService } = await import('../../lib/api');
      
      const response = await authService.login({
        username,
        password,
      });

      const { access, refresh, user } = response.data;
      
      // Determine route based on user role or fallback demo
      const selectedDemo = DEMO_ACCOUNTS.find(a => a.username === username);
      const targetRoute = selectedDemo ? selectedDemo.target : '/';

      const userObj = {
        ...user,
        title: selectedDemo ? selectedDemo.desc : 'Government Official',
        token: access,
        defaultRoute: targetRoute,
      };

      localStorage.setItem('warimitra_user', JSON.stringify(userObj));
      localStorage.setItem('warimitra_token', access);
      
      document.cookie = `warimitra_token=${access}; path=/; max-age=86400`;
      document.cookie = `warimitra_role=${encodeURIComponent(user.role || 'ADMIN')}; path=/; max-age=86400`;
      
      router.push(targetRoute);
    } catch (err: any) {
      console.error('Login failed:', err);
      setError(err.response?.data?.detail || 'Login failed. Please check credentials.');
      setLoading(false);
    }
  };

  const selectDemoAccount = (acc: typeof DEMO_ACCOUNTS[0]) => {
    setUsername(acc.username);
    setPassword(acc.password);
  };

  return (
    <div className="min-h-screen bg-[#070A12] flex items-center justify-center p-4 sm:p-6 relative overflow-hidden">
      {/* Background Bhagwa Glows */}
      <div className="absolute -top-32 -left-32 w-96 h-96 bg-orange-600/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-amber-500/15 rounded-full blur-[120px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.4, type: 'spring', bounce: 0.2 }}
        className="w-full max-w-md bg-[#0F1420]/95 backdrop-blur-2xl border border-orange-500/30 p-6 sm:p-8 rounded-3xl shadow-2xl z-10 space-y-6"
      >
        {/* Header & Emblem */}
        <div className="text-center space-y-3">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-tr from-orange-600 to-amber-500 flex items-center justify-center shadow-lg shadow-orange-500/40">
            <span className="text-white font-black text-2xl tracking-tighter">W</span>
          </div>
          <div>
            <h1 className="text-2xl font-black text-white tracking-tight">वारीमित्र पोर्टल</h1>
            <p className="text-orange-400 font-bold text-xs mt-1 flex items-center justify-center gap-1">
              <Flag size={12} />
              <span>महाराष्ट्र शासन • पंढरपूर वारी सेवा कौन्सिल</span>
            </p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="text-slate-300 text-xs font-bold block mb-1.5">Username / पदनाव</label>
            <div className="relative">
              <User className="absolute left-3.5 top-1/2 -translate-y-1/2 text-orange-400" size={16} />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 bg-[#161B2E] border border-white/15 text-white placeholder-slate-500 text-sm rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all"
              />
            </div>
          </div>

          <div>
            <label className="text-slate-300 text-xs font-bold block mb-1.5">Password / संकेतशब्द</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-orange-400" size={16} />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 bg-[#161B2E] border border-white/15 text-white placeholder-slate-500 text-sm rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all"
              />
            </div>
          </div>

          {error && <p className="text-red-400 text-xs font-semibold">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-orange-600 to-amber-500 hover:from-orange-500 hover:to-amber-400 text-white font-extrabold text-sm rounded-xl shadow-lg shadow-orange-500/30 transition-all flex items-center justify-center gap-2 active:scale-[0.98]"
          >
            {loading ? 'प्रमाणित करत आहे...' : 'Sign In to Command Center'}
            {!loading && <ArrowRight size={16} />}
          </button>
        </form>

        {/* Quick Demo Credentials Picker */}
        <div className="pt-4 border-t border-white/10 space-y-3">
          <p className="text-slate-400 text-xs font-bold flex items-center gap-1.5">
            <Sparkles size={14} className="text-orange-400" />
            Select Official Role for Instant Access:
          </p>
          <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
            {DEMO_ACCOUNTS.map((acc) => (
              <div
                key={acc.username}
                onClick={() => selectDemoAccount(acc)}
                className={`p-2.5 rounded-xl border text-xs cursor-pointer flex items-center justify-between transition-all ${
                  username === acc.username
                    ? 'bg-orange-500/20 border-orange-500/60 text-white font-bold shadow-md'
                    : 'bg-[#131B2E] border-white/10 text-slate-300 hover:bg-white/10'
                }`}
              >
                <div>
                  <span className="font-extrabold text-white">{acc.role}</span>
                  <span className="text-orange-400 text-[10px] block font-medium">{acc.marathi} • {acc.desc}</span>
                </div>
                {username === acc.username && <CheckCircle2 size={16} className="text-orange-400" />}
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
