'use client'

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Settings, Award, CheckSquare } from 'lucide-react'

interface SecondaryPanelProps {
  validation?: {
    approved: boolean
    reason?: string
  }
  reputation?: {
    winRate: number
    profitFactor: number
    sharpeRatio: number
    maxDrawdown: number
  }
  approvedIntents?: Array<{
    id: string
    symbol: string
    action: string
    timestamp: Date
  }>
  proofStats?: {
    totalTrades: number
    validatedTrades: number
    successRate: number
  }
}

export function SecondaryPanel({
  validation,
  reputation,
  approvedIntents = [],
  proofStats,
}: SecondaryPanelProps) {
  return (
    <Accordion type="single" collapsible className="w-full">
      {/* Validation Section */}
      {validation && (
        <AccordionItem value="validation" className="border-slate-800">
          <AccordionTrigger className="hover:bg-slate-900/50">
            <div className="flex items-center gap-2">
              <CheckSquare className="w-4 h-4 text-blue-600" />
              <span>Validation</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Status</span>
                <Badge variant={validation.approved ? 'success' : 'destructive'}>
                  {validation.approved ? 'Approved' : 'Blocked'}
                </Badge>
              </div>
              {validation.reason && (
                <p className="text-sm text-slate-700 bg-slate-100 rounded p-2">
                  {validation.reason}
                </p>
              )}
            </div>
          </AccordionContent>
        </AccordionItem>
      )}

      {/* Reputation Section */}
      {reputation && (
        <AccordionItem value="reputation" className="border-slate-800">
          <AccordionTrigger className="hover:bg-slate-900/50">
            <div className="flex items-center gap-2">
              <Award className="w-4 h-4 text-amber-400" />
              <span>Reputation</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-900/50 rounded p-3">
                  <div className="text-xs text-slate-600 mb-1">Win Rate</div>
                  <div className="text-xl font-bold text-emerald-600">
                    {(reputation.winRate * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="bg-slate-900/50 rounded p-3">
                  <div className="text-xs text-slate-600 mb-1">Profit Factor</div>
                  <div className="text-xl font-bold text-blue-400">
                    {reputation.profitFactor.toFixed(2)}x
                  </div>
                </div>
                <div className="bg-slate-900/50 rounded p-3">
                  <div className="text-xs text-slate-600 mb-1">Sharpe Ratio</div>
                  <div className="text-xl font-bold text-blue-400">
                    {reputation.sharpeRatio.toFixed(2)}
                  </div>
                </div>
                <div className="bg-slate-900/50 rounded p-3">
                  <div className="text-xs text-slate-600 mb-1">Max Drawdown</div>
                  <div className="text-xl font-bold text-red-600">
                    {(reputation.maxDrawdown * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      )}

      {/* Approved Intents Section */}
      {approvedIntents.length > 0 && (
        <AccordionItem value="intents" className="border-slate-800">
          <AccordionTrigger className="hover:bg-slate-900/50">
            <div className="flex items-center gap-2">
              <CheckSquare className="w-4 h-4 text-emerald-400" />
              <span>Approved Intents ({approvedIntents.length})</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-2">
              {approvedIntents.map((intent) => (
                <div
                  key={intent.id}
                  className="flex items-center justify-between p-2 bg-slate-900/50 rounded text-sm"
                >
                  <div>
                    <span className="font-medium text-slate-50">{intent.symbol}</span>
                    <span className="text-slate-400 mx-2">•</span>
                    <Badge variant="success" className="py-0 text-xs">
                      {intent.action}
                    </Badge>
                  </div>
                  <span className="text-xs text-slate-500">
                    {intent.timestamp.toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>
      )}

      {/* Proof Stats Section */}
      {proofStats && (
        <AccordionItem value="proof" className="border-slate-800">
          <AccordionTrigger className="hover:bg-slate-900/50">
            <div className="flex items-center gap-2">
              <Settings className="w-4 h-4 text-slate-400" />
              <span>Proof Stats</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-2">
                <div className="bg-slate-900/50 rounded p-2">
                  <div className="text-xs text-slate-400">Total</div>
                  <div className="text-lg font-bold text-slate-50">
                    {proofStats.totalTrades}
                  </div>
                </div>
                <div className="bg-slate-900/50 rounded p-2">
                  <div className="text-xs text-slate-400">Validated</div>
                  <div className="text-lg font-bold text-emerald-400">
                    {proofStats.validatedTrades}
                  </div>
                </div>
                <div className="bg-slate-900/50 rounded p-2">
                  <div className="text-xs text-slate-400">Success</div>
                  <div className="text-lg font-bold text-blue-400">
                    {(proofStats.successRate * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      )}
    </Accordion>
  )
}
