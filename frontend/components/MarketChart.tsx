'use client'

import { useEffect, useRef } from 'react'
import { createChart, type IChartApi, type ISeriesApi, type UTCTimestamp } from 'lightweight-charts'
import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp } from 'lucide-react'

interface Candle {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
}

interface MarketChartProps {
  symbol: string
  candles: Candle[]
  isLoading?: boolean
}

export function MarketChart({ symbol, candles, isLoading = false }: MarketChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)

  useEffect(() => {
    if (!containerRef.current || !candles.length) return

    // Clean up old chart
    if (chartRef.current) {
      chartRef.current.remove()
    }

    // Create chart
    const chart = createChart(containerRef.current, {
      layout: {
        background: { color: '#f8fafc' },
        textColor: '#475569',
        fontSize: 12,
        fontFamily: 'Inter, sans-serif',
      },
      width: containerRef.current.clientWidth,
      height: 350,
      timeScale: {
        borderColor: '#e2e8f0',
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: '#e2e8f0',
        textColor: '#475569',
      },
      grid: {
        horzLines: { color: '#f1f5f9', visible: true },
        vertLines: { color: '#f1f5f9', visible: true },
      },
    })

    const series = chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    })

    chartRef.current = chart
    seriesRef.current = series

    // Update chart data
    const data = candles
      .map((c) => ({
        time: Math.floor(
          new Date(c.timestamp).getTime() / 1000
        ) as UTCTimestamp,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      }))
      .sort((a, b) => a.time - b.time)

    series.setData(data as never)
    chart.timeScale().fitContent()

    // Handle resize
    const handleResize = () => {
      if (containerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: containerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      if (chartRef.current) {
        chartRef.current.remove()
        chartRef.current = null
        seriesRef.current = null
      }
    }
  }, [candles])

  const lastCandle = candles[candles.length - 1]
  const price = lastCandle?.close || 0
  const prevPrice = candles.length > 1 ? candles[candles.length - 2].close : price
  const priceChange = price - prevPrice
  const priceChangePercent = ((priceChange / prevPrice) * 100).toFixed(2)

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
    >
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-400" />
              <div>
                <CardTitle className="text-lg">{symbol} • 1m</CardTitle>
                <CardDescription>Live price feed</CardDescription>
              </div>
            </div>
            <div className="text-right">
              <motion.div
                initial={{ scale: 0.95 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                className="text-2xl font-bold text-slate-50"
              >
                ${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </motion.div>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className={`text-sm font-semibold ${
                  priceChange >= 0 ? 'text-emerald-400' : 'text-red-400'
                }`}
              >
                {priceChange >= 0 ? '↑' : '↓'} {Math.abs(Number(priceChangePercent))}%
              </motion.div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <motion.div
            ref={containerRef}
            className="w-full h-[300px]"
            initial={{ opacity: 0 }}
            animate={{ opacity: isLoading ? 0.6 : 1 }}
            transition={{ duration: 0.3 }}
          />
        </CardContent>
      </Card>
    </motion.div>
  )
}
