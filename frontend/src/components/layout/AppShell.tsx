"use client";

import React from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import { AccessibilityProvider } from '@/components/providers/AccessibilityProvider';

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <AccessibilityProvider>
      <div className="flex h-screen overflow-hidden bg-[#0B0F19]">
        <Sidebar />
        <div className="flex flex-col flex-1 h-screen overflow-hidden">
          <Topbar />
          <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
            {children}
          </main>
        </div>
      </div>
    </AccessibilityProvider>
  );
}
