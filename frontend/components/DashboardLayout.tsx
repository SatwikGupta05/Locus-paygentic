'use client'

import { ReactNode } from 'react'

interface DashboardLayoutProps {
  children: ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="w-full h-full bg-white">
      <div className="container max-w-7xl mx-auto px-4 py-4 space-y-2">
        {children}
      </div>
    </div>
  )
}

interface DashboardGridProps {
  children: ReactNode
}

/**
 * Responsive grid for dashboard:
 * Desktop: 12-column grid with gaps
 * Mobile: Stacked vertically
 * 
 * Usage:
 * - Decision: col-span-4 → md:col-span-12
 * - Chart: col-span-8 → md:col-span-12
 * - PnL: col-span-4 → md:col-span-6 → sm:col-span-12
 * - Risk: col-span-4 → md:col-span-6 → sm:col-span-12
 * - Feed: col-span-4 → md:col-span-6 → sm:col-span-12
 */
export function DashboardGrid({ children }: DashboardGridProps) {
  return (
    <div className="grid grid-cols-12 gap-2 auto-rows-max">
      {children}
    </div>
  )
}

// Helper components for grid positioning
export function DecisionCardWrapper({ children }: { children: ReactNode }) {
  return <div className="col-span-12 lg:col-span-4">{children}</div>
}

export function MarketChartWrapper({ children }: { children: ReactNode }) {
  return <div className="col-span-12 lg:col-span-8">{children}</div>
}

export function BottomRowWrapper({ children }: { children: ReactNode }) {
  return <div className="col-span-12 grid grid-cols-12 gap-2 auto-rows-max">{children}</div>
}

export function PnLWidgetWrapper({ children }: { children: ReactNode }) {
  return <div className="col-span-12 md:col-span-6 lg:col-span-4">{children}</div>
}

export function RiskBadgeWrapper({ children }: { children: ReactNode }) {
  return <div className="col-span-12 md:col-span-6 lg:col-span-4">{children}</div>
}

export function LiveFeedWrapper({ children }: { children: ReactNode }) {
  return <div className="col-span-12 md:col-span-6 lg:col-span-4">{children}</div>
}

export function ReasoningPanelWrapper({ children }: { children: ReactNode }) {
  return <div className="col-span-12 lg:col-span-8">{children}</div>
}

export function SecondaryPanelWrapper({ children }: { children: ReactNode }) {
  return <div className="col-span-12 lg:col-span-4">{children}</div>
}
