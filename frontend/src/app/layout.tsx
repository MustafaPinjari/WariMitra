import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import AppShell from '@/components/layout/AppShell';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'WariMitra | Government Dashboard',
  description: 'Centralized control center for Wari pilgrimage management — साथ चालू, सुरक्षित पोहोचू',
  icons: {
    icon: '/logo.png',
    shortcut: '/logo.png',
    apple: '/logo.png',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#0B0F19] min-h-screen text-slate-200`}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
