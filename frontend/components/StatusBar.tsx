'use client'

import { motion } from 'framer-motion'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Activity, Clock, Radio } from 'lucide-react'

interface StatusBarProps {
  status: 'Active' | 'Waiting' | 'Executing'
  lastUpdated: Date | null
  isSyncing?: boolean
}

const statusConfig = {
  Active: { icon: Activity, color: 'text-emerald-600', variant: 'success' as const },
  Waiting: { icon: Activity, color: 'text-amber-600', variant: 'warning' as const },
  Executing: { icon: Activity, color: 'text-blue-600', variant: 'info' as const },
}

export function StatusBar({
  status,
  lastUpdated,
  isSyncing = false,
}: StatusBarProps) {
  const config = statusConfig[status]
  const Icon = config.icon

  const formatTime = (date: Date | null) => {
    if (!date) return 'Never'
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)

    if (hours > 0) return `${hours}h ago`
    if (minutes > 0) return `${minutes}m ago`
    return `${seconds}s ago`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="flex items-center gap-3 px-4 py-3 bg-white border border-slate-200 rounded-lg text-xs"
    >
      <div className="flex items-center gap-2">
        <motion.div
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <Icon className={`w-4 h-4 ${config.color}`} />
        </motion.div>
        <Badge variant={config.variant}>
          <span className="animate-pulse-subtle">{status}</span>
        </Badge>
      </div>

      <Separator orientation="vertical" className="h-4" />

      <div className="flex items-center gap-2 text-slate-400">
        <Clock className="w-4 h-4" />
        <span>Updated {formatTime(lastUpdated)}</span>
      </div>

      <Separator orientation="vertical" className="h-4" />

      <div className="flex items-center gap-2">
        {isSyncing ? (
          <>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            >
              <Radio className="w-4 h-4 text-blue-400" />
            </motion.div>
            <span className="text-slate-400">Syncing...</span>
          </>
        ) : (
          <span className="text-slate-500">Ready</span>
        )}
      </div>
    </motion.div>
  )
}
