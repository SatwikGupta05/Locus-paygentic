'use client'

import { motion } from 'framer-motion'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Shield, ShieldAlert, AlertTriangle } from 'lucide-react'

type RiskLevel = 'SAFE' | 'CAUTION' | 'BLOCKED'

interface RiskBadgeProps {
  level: RiskLevel
  reason?: string
  exposure?: number
}

const riskConfig = {
  SAFE: {
    icon: Shield,
    color: 'text-emerald-600',
    bgColor: 'bg-emerald-100',
    borderColor: 'border-emerald-300',
    badgeVariant: 'success',
    message: 'Risk parameters approved',
  },
  CAUTION: {
    icon: AlertTriangle,
    color: 'text-amber-600',
    bgColor: 'bg-amber-100',
    borderColor: 'border-amber-300',
    badgeVariant: 'warning',
    message: 'Elevated risk detected',
  },
  BLOCKED: {
    icon: ShieldAlert,
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    borderColor: 'border-red-300',
    badgeVariant: 'destructive',
    message: 'Trade blocked by risk controls',
  },
}

export function RiskBadge({ level, reason, exposure }: RiskBadgeProps) {
  const config = riskConfig[level]
  const Icon = config.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <motion.div
        animate={level === 'CAUTION' ? { x: [-4, 4, -4, 0] } : {}}
        transition={level === 'CAUTION' ? { duration: 0.5, delay: 0.5 } : {}}
      >
        <Card className={`border-2 ${config.borderColor} ${config.bgColor}`}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', stiffness: 200, delay: 0.3 }}
                >
                  <Icon className={`w-5 h-5 ${config.color}`} />
                </motion.div>
                <div>
                  <CardTitle className="text-lg">Risk Status</CardTitle>
                  <CardDescription>Portfolio protection</CardDescription>
                </div>
              </div>
              <Badge variant={config.badgeVariant as 'success' | 'warning' | 'destructive'}>
                {level}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3, delay: 0.2 }}
              className={`text-sm font-medium ${config.color}`}
            >
              {config.message}
            </motion.p>

            {reason && (
              <div className="pt-4 border-t border-slate-800">
                <div className="text-xs text-slate-400 mb-2 uppercase font-semibold tracking-wide">
                  Details
                </div>
                <p className="text-sm text-slate-600">{reason}</p>
              </div>
            )}

            {exposure !== undefined && (
              <div className="pt-4 border-t border-slate-800">
                <div className="text-xs text-slate-400 mb-2 uppercase font-semibold tracking-wide">
                  Gross Exposure
                </div>
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 }}
                  className="text-lg font-semibold text-slate-900"
                >
                  {(exposure * 100).toFixed(1)}%
                </motion.div>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
