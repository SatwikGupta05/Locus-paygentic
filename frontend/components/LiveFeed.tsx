'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Activity, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react'

interface FeedEvent {
  id: string
  type: 'trade' | 'decision' | 'risk' | 'update'
  title: string
  description: string
  timestamp: Date
  severity?: 'info' | 'warning' | 'error'
}

interface LiveFeedProps {
  events: FeedEvent[]
  isLoading?: boolean
}

const eventIcons = {
  trade: TrendingUp,
  decision: Activity,
  risk: AlertCircle,
  update: Activity,
}

const severityConfig = {
  info: { color: 'text-blue-600', variant: 'info' as const },
  warning: { color: 'text-amber-400', variant: 'warning' as const },
  error: { color: 'text-red-600', variant: 'destructive' as const },
}

export function LiveFeed({ events = [], isLoading = false }: LiveFeedProps) {
  // Show only last 3 events, filter out undefined/null
  const filteredEvents = events
    .filter((e) => e && e.id && e.type && e.title)
    .slice(-3)
    .reverse()

  const formatTime = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)

    if (minutes > 0) return `${minutes}m ago`
    return `${seconds}s ago`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.25 }}
    >
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" />
            <div>
              <CardTitle className="text-lg">Live Events</CardTitle>
              <CardDescription>Latest trading activity</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredEvents.length === 0 ? (
            <div className="text-center py-8">
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="text-slate-600 text-sm"
              >
                {isLoading ? 'Loading events...' : 'No events yet'}
              </motion.p>
            </div>
          ) : (
            <div className="space-y-3">
              <AnimatePresence mode="popLayout">
                {filteredEvents.map((event, idx) => {
                  const Icon = eventIcons[event.type]
                  const severityConfig_ = event.severity
                    ? severityConfig[event.severity]
                    : { color: 'text-slate-600', variant: 'secondary' as const }

                  return (
                    <motion.div
                      key={event.id}
                      initial={{ opacity: 0, y: -8, x: -16 }}
                      animate={{ opacity: 1, y: 0, x: 0 }}
                      exit={{ opacity: 0, y: 8, x: 16 }}
                      transition={{
                        duration: 0.3,
                        delay: idx * 0.05,
                      }}
                      className="flex items-start gap-3 p-3 rounded-lg bg-slate-100 border border-slate-300 hover:border-slate-400 transition-colors hover:bg-slate-200"
                    >
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{
                          type: 'spring',
                          stiffness: 200,
                          delay: idx * 0.05 + 0.1,
                        }}
                      >
                        <Icon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${severityConfig_.color}`} />
                      </motion.div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <p className="text-sm font-medium text-slate-900">
                              {event.title}
                            </p>
                            <p className="text-xs text-slate-600 mt-1 line-clamp-1">
                              {event.description}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant={severityConfig_.variant} className="text-[10px] py-0.5">
                            {event.type}
                          </Badge>

                          <span className="text-xs text-slate-700">
                            {formatTime(event.timestamp)}
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  )
                })}
              </AnimatePresence>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
