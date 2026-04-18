'use client'

import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Lightbulb } from 'lucide-react'

interface ReasoningPanelProps {
  bullets: string[]
  score?: number
}

export function ReasoningPanel({ bullets = [], score }: ReasoningPanelProps) {
  // Show only 3 bullets max
  const displayBullets = bullets.slice(0, 3)

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, x: -8 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.3 },
    },
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
    >
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <motion.div
              initial={{ scale: 0, rotate: -90 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ type: 'spring', stiffness: 200, delay: 0.3 }}
            >
              <Lightbulb className="w-5 h-5 text-amber-400" />
            </motion.div>
            <div>
              <CardTitle className="text-lg">AI Reasoning</CardTitle>
              <CardDescription>Decision factors</CardDescription>
            </div>
            {score !== undefined && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 }}
                className="ml-auto text-right"
              >
                <div className="text-2xl font-bold text-blue-600">{score}%</div>
                <div className="text-xs text-slate-600">score</div>
              </motion.div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {displayBullets.length === 0 ? (
            <p className="text-slate-600 text-sm">No reasoning available</p>
          ) : (
            <motion.ul
              className="space-y-3"
              variants={containerVariants}
              initial="hidden"
              animate="visible"
            >
              {displayBullets.map((bullet, idx) => (
                <motion.li key={idx} variants={itemVariants} className="flex gap-3 items-start">
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.2 + idx * 0.1, type: 'spring' }}
                    className="text-blue-600 font-bold text-sm mt-0.5"
                  >
                    •
                  </motion.span>
                  <span className="text-sm text-slate-700">{bullet}</span>
                </motion.li>
              ))}
            </motion.ul>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
