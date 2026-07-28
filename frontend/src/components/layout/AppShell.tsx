"use client";

import { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import Sidebar from '@/components/layout/Sidebar';
import Topbar from '@/components/layout/Topbar';

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const isLoginPage = pathname === '/login';

  useEffect(() => {
    if (isLoginPage) return;

    const saved = localStorage.getItem('warimitra_user');
    if (saved) {
      try {
        const u = JSON.parse(saved);
        // Automatic Role Route Redirection if accessing overview `/` as non-admin
        if (pathname === '/') {
          if (u.role === 'Medical Officer') router.push('/medical');
          else if (u.role === 'Police Officer') router.push('/police');
          else if (u.role === 'NGO Coordinator') router.push('/ngo');
        }
      } catch (e) {}
    }
  }, [pathname, isLoginPage, router]);

  if (isLoginPage) {
    return <main className="w-full min-h-screen">{children}</main>;
  }

  return (
    <div className="flex min-h-screen w-full bg-[#0B0F19] text-slate-200">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-x-hidden">
        <Topbar />
        <main className="flex-1 overflow-hidden p-0">{children}</main>
      </div>
    </div>
  );
}
