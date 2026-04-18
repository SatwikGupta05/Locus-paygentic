'use client'

import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface PnLWidgetProps {
  totalPnL: number
  dailyPnL: number
  percentChange: number
  sparklineData?: number[]
}

export function PnLWidget({
  totalPnL,
  dailyPnL,
  percentChange,
  sparklineData = [],
}: PnLWidgetProps) {
  const isProfit = totalPnL >= 0
  const isDailyProfit = dailyPnL >= 0

  // Simple sparkline
  const normalizedData = sparklineData.length
    ? sparklineData.map((v) => {
        const min = Math.min(...sparklineData)
        const max = Math.max(...sparklineData)
        const range = max - min || 1
        return ((v - min) / range) * 100
      })
    : []

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.15 }}
    >
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                {isProfit ? (
                  <TrendingUp className="w-5 h-5 text-emerald-600" />
                ) : (
                  <TrendingDown className="w-5 h-5 text-red-600" />
                )}
                P&L
              </CardTitle>
              <CardDescription>Total realized gains</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3, delay: 0.1 }}
            className="space-y-2"
          >
            <motion.div
              className={`text-3xl font-bold ${
                isProfit ? 'text-emerald-600' : 'text-red-600'
              }`}
              animate={{ scale: [1, 1.02, 1] }}
              transition={{ duration: 2, repeat: Infinity, repeatDelay: 5 }}
            >
              {isProfit ? '+' : '-'}${Math.abs(totalPnL).toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </motion.div>
            <div className="text-sm text-slate-600">
              <span
                className={`font-semibold ${
                  percentChange >= 0 ? 'text-emerald-600' : 'text-red-600'
                }`}
              >
                {percentChange >= 0 ? '+' : ''}{percentChange.toFixed(2)}%
              </span>{' '}
              today
            </div>
          </motion.div>

          {/* Daily PnL */}
          <div className="pt-4 border-t border-slate-800">
            <div className="text-xs text-slate-600 mb-2 uppercase font-semibold tracking-wide">
              Daily P&L
            </div>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className={`text-xl font-bold ${
                isDailyProfit ? 'text-emerald-600' : 'text-red-600'
              }`}
            >
              {isDailyProfit ? '+' : '-'}${Math.abs(dailyPnL).toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </motion.div>
          </div>

          {/* Sparkline */}
          {normalizedData.length > 0 && (
            <div className="pt-4 border-t border-slate-800">
              <div className="text-xs text-slate-600 mb-3 uppercase font-semibold tracking-wide">
                7-Day Trend
              </div>
              <motion.svg
                viewBox="0 0 100 30"
                className="w-full h-12"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <polyline
                  fill="none"
                  stroke={isProfit ? '#22c55e' : '#ef4444'}
                  strokeWidth="1.5"
                  points={normalizedData
                    .map((v, i) => `${(i / (normalizedData.length - 1)) * 100},${100 - v}`)
                    .join(' ')}
                />
              </motion.svg>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
