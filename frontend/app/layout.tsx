/**
 * Root layout component
 * Phase 1.8: Add prefers-reduced-motion support here
 */
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'WariMitra - Pilgrim Safety',
  description: 'Real-time emergency response and medical coordination system',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-gray-900 text-gray-100">
        {/* Phase 1.8: Check prefers-reduced-motion */}
        {children}
      </body>
    </html>
  )
}
