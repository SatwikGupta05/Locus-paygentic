'use client'

import { motion } from 'framer-motion'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Zap } from 'lucide-react'

interface DecisionCardProps {
  decision: 'BUY' | 'SELL' | 'HOLD' | 'NO TRADE'
  confidence: number
  reasoning: string
  symbol: string
}

const decisionConfig = {
  BUY: {
    color: 'text-emerald-600',
    bgColor: 'bg-emerald-100',
    borderColor: 'border-emerald-300',
    badgeVariant: 'success',
    icon: '↑',
  },
  SELL: {
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    borderColor: 'border-red-300',
    badgeVariant: 'destructive',
    icon: '↓',
  },
  HOLD: {
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    borderColor: 'border-blue-300',
    badgeVariant: 'info',
    icon: '→',
  },
  'NO TRADE': {
    color: 'text-slate-600',
    bgColor: 'bg-slate-100',
    borderColor: 'border-slate-300',
    badgeVariant: 'secondary' as const,
    icon: '⊗',
  },
}

export function DecisionCard({
  decision,
  confidence,
  reasoning,
  symbol,
}: DecisionCardProps) {
  const config = decisionConfig[decision]

  return (
    <motion.div
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="w-full"
    >
      <Card
        className={`border-2 ${config.borderColor} ${config.bgColor} relative overflow-hidden`}
      >
        {/* Animated background gradient */}
        <div
          className={`absolute inset-0 ${config.bgColor} opacity-50`}
          style={{
            animation: decision !== 'HOLD' ? 'pulse-subtle 2s ease-in-out infinite' : 'none',
          }}
        />

        <CardContent className="relative z-10 p-8">
          <div className="flex items-start justify-between gap-4 mb-6">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <div className={`text-sm font-semibold ${config.color}`}>
                  {symbol} • Decision
                </div>
              </div>

              <motion.div
                layoutId="decision-text"
                className={`text-5xl font-black ${config.color} mb-4 tracking-tight`}
              >
                {decision}
              </motion.div>

              <p className="text-slate-300 text-sm leading-relaxed max-w-xs">
                {reasoning}
              </p>
            </div>

            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
              className="flex flex-col items-end gap-3"
            >
              <div className="bg-emerald-100 text-emerald-600 px-2 py-1 rounded-full text-xs">
                <span className="font-bold">{confidence}%</span>
              </div>

              <div className="flex items-center gap-1 text-xs text-slate-400">
                <Zap className="w-3 h-3" />
                <span>Active</span>
              </div>
            </motion.div>
          </div>

          {/* Confidence bar */}
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${confidence}%` }}
              transition={{ duration: 0.8, delay: 0.2, ease: 'easeOut' }}
              className={`h-full ${config.bgColor} rounded-full`}
            />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
