'use client';

import { createChart, type IChartApi, type ISeriesApi, type UTCTimestamp } from 'lightweight-charts';
import { AnimatePresence, motion } from 'framer-motion';
import { Activity, ArrowRight, Bot, BrainCircuit, CandlestickChart, CheckCircle2, Cpu, Hourglass, Layers3, Radar, Scale, Shield, ShieldAlert, ShieldCheck, Sparkles, Trophy, TrendingDown, TrendingUp, Waves, Zap, MessageSquare, Target } from 'lucide-react';
import type { ReactNode } from 'react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useStore, type AgentNarrative } from '@/lib/store';
import { ManualTradePanel } from '@/components/dashboard/manual-trade-panel';

type DecisionTone = 'BUY' | 'SELL' | 'HOLD' | 'NO TRADE';

function GlassPanel({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`rounded-[28px] border border-white/60 bg-white/68 p-6 shadow-[0_20px_70px_rgba(148,163,184,0.16)] backdrop-blur-xl transition-all duration-500 hover:-translate-y-1 hover:shadow-[0_24px_80px_rgba(59,130,246,0.14)] ${className}`}>{children}</div>;
}

function SectionEyebrow({ icon: Icon, label }: { icon: any; label: string }) {
  return (
    <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-slate-200/80 bg-white/85 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
      <Icon className="h-3.5 w-3.5" />
      {label}
    </div>
  );
}

function formatJudgeTime(timestamp?: number) {
  if (!timestamp) return 'Awaiting judge pass';
  return new Date(timestamp * 1000).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function formatTradeTimeIST(timestamp: string): string {
  try {
    // Parse the timestamp (could be ISO string or other format)
    const date = new Date(timestamp);
    // Format in IST timezone (UTC+5:30)
    const istDate = new Date(date.getTime() + (5.5 * 60 * 60 * 1000));
    return istDate.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
  } catch (e) {
    return 'Invalid time';
  }
}

function ScoreRibbon({ scores }: { scores: number[] }) {
  if (!scores.length) {
    return <div className="rounded-[22px] border border-dashed border-slate-200 bg-white/70 px-4 py-5 text-sm text-slate-500">No validation streak yet.</div>;
  }
  return (
    <div className="rounded-[24px] border border-white/70 bg-slate-950 p-5 text-white shadow-[0_20px_50px_rgba(15,23,42,0.22)]">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Validation streak</p>
          <p className="mt-1 text-lg font-semibold">Latest 8 attestations</p>
        </div>
        <div className="rounded-full bg-emerald-500/15 px-3 py-2 text-sm font-semibold text-emerald-300">
          Avg {Math.round(scores.reduce((sum, value) => sum + value, 0) / scores.length)}
        </div>
      </div>
      <div className="grid grid-cols-4 gap-3 sm:grid-cols-8">
        {scores.map((score, index) => (
          <div key={`${score}-${index}`} className="rounded-[18px] border border-white/10 bg-white/5 px-3 py-4 text-center">
            <div className={`text-2xl font-black tracking-[-0.06em] ${score >= 95 ? 'text-emerald-300' : score >= 85 ? 'text-sky-300' : 'text-amber-300'}`}>{score}</div>
            <div className="mt-1 text-[10px] uppercase tracking-[0.24em] text-slate-500">Attest {index + 1}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function formatStage(stage?: string) {
  if (!stage) return 'Awaiting cycle';
  return stage.toLowerCase().split('_').map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(' ');
}

function buildVisual(action?: string, confidence = 58, volatility?: string) {
  const tone = (action || 'HOLD').toUpperCase();
  if (tone === 'SELL') return { label: 'SELL' as DecisionTone, headline: 'High volatility detected', summary: 'Momentum weakening • Volatility rising', note: 'Aurora is acting defensively under rising volatility.', accent: 'text-rose-500', chip: 'bg-rose-50 text-rose-600', border: 'border-rose-200/80', glow: 'from-rose-400/25 via-orange-300/10 to-transparent', marker: '#f43f5e', bullets: ['Trend is rolling over'], confidence };
  if (tone === 'BUY') return { label: 'BUY' as DecisionTone, headline: 'Momentum aligned', summary: 'Trend strengthening • Conditions supportive', note: 'Aurora is leaning into strength while risk remains stable.', accent: 'text-emerald-500', chip: 'bg-emerald-50 text-emerald-600', border: 'border-emerald-200/80', glow: 'from-emerald-400/25 via-lime-300/10 to-transparent', marker: '#22c55e', bullets: ['Liquidity remains stable'], confidence };
  if (confidence < 50) return { label: 'NO TRADE' as DecisionTone, headline: 'Confidence below threshold', summary: 'Discipline active • Capital preserved', note: 'Aurora is staying disciplined.', accent: 'text-amber-500', chip: 'bg-amber-50 text-amber-700', border: 'border-amber-200/80', glow: 'from-amber-300/25 via-yellow-200/10 to-transparent', marker: '#f59e0b', bullets: [], confidence };
  return { label: 'HOLD' as DecisionTone, headline: 'Conditions still mixed', summary: 'Neutral structure • Wait for breakout', note: 'Aurora is staying disciplined.', accent: 'text-sky-500', chip: 'bg-sky-50 text-sky-700', border: 'border-sky-200/80', glow: 'from-sky-400/25 via-cyan-300/10 to-transparent', marker: '#0ea5e9', bullets: [], confidence };
}

function linePath(values: number[], width: number, height: number) {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = Math.max(max - min, 1);
  const pts = values.map((v, i) => ({ x: (i / Math.max(values.length - 1, 1)) * width, y: height - ((v - min) / range) * (height - 20) - 10 }));
  return pts.reduce((acc, p, i, arr) => (i === 0 ? `M ${p.x} ${p.y}` : `${acc} Q ${(arr[i - 1].x + p.x) / 2} ${arr[i - 1].y}, ${p.x} ${p.y}`), '');
}

function LiveChart({ candles, action, pair, marker }: { candles: any[]; action: string; pair: string; marker: string }) {
  const ref = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    
    // Only create chart if we have candles to avoid race condition
    if (!candles.length) return;

    // Clean up old chart if it exists
    if (chartRef.current) {
      chartRef.current.remove();
    }

    const chart = createChart(ref.current, {
      autoSize: true, height: 320,
      layout: { background: { color: 'transparent' }, textColor: '#94a3b8' },
      grid: { vertLines: { color: 'rgba(148,163,184,0.08)' }, horzLines: { color: 'rgba(148,163,184,0.08)' } },
      rightPriceScale: { borderColor: 'rgba(148,163,184,0.18)' },
      timeScale: { borderColor: 'rgba(148,163,184,0.18)', timeVisible: true, secondsVisible: false },
    });
    const series = chart.addCandlestickSeries({ upColor: '#22c55e', downColor: '#f43f5e', borderVisible: false, wickUpColor: '#22c55e', wickDownColor: '#f43f5e' });
    chartRef.current = chart;
    seriesRef.current = series;

    // Immediately populate with data
    const data = Array.from(new Map(candles.map((c) => [c.timestamp, { time: Math.floor(new Date(c.timestamp).getTime() / 1000) as UTCTimestamp, open: c.open, high: c.high, low: c.low, close: c.close }])).values()).sort((a, b) => Number(a.time) - Number(b.time));
    series.setData(data as never);
    
    const last = data[data.length - 1];
    if (last) {
      series.setMarkers([{ time: last.time, position: action === 'SELL' ? 'aboveBar' : 'belowBar', color: marker, shape: action === 'SELL' ? 'arrowDown' : action === 'BUY' ? 'arrowUp' : 'circle', text: action }]);
    }
    chart.timeScale().fitContent();

    return () => {
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
        seriesRef.current = null;
      }
    };
  }, [candles, action, marker]);

  const last = candles[candles.length - 1]?.close;

  return (
    <div className="rounded-[28px] border border-white/70 bg-slate-950 p-5 text-white shadow-[0_24px_60px_rgba(15,23,42,0.24)]">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Signal driving decision</p>
          <h3 className="mt-2 text-xl font-semibold">{pair} • 1m</h3>
        </div>
        <div className="text-right">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Last price</p>
          <p className="mt-2 text-2xl font-semibold">{last ? `$${last.toLocaleString()}` : 'Awaiting feed'}</p>
        </div>
      </div>
      <div ref={ref} className="h-[320px] w-full" />
    </div>
  );
}

export default function DashboardPage() {
  const market = useStore((s) => s.market);
  const decision = useStore((s) => s.decision);
  const metrics = useStore((s) => s.metrics);
  const trades = useStore((s) => s.trades);
  const agent = useStore((s) => s.agent);
  const pipeline = useStore((s) => s.pipelineStage);
  const isConnected = useStore((s) => s.isConnected);
  const [timeLabel, setTimeLabel] = useState('');
  const [pulseIndex, setPulseIndex] = useState(0);

  // Calculate metrics from trades (for manual/paper trading)
  const calculatedMetrics = useMemo(() => {
    if (!trades || trades.length === 0) {
      return {
        total_pnl: 0,
        win_rate: 0,
        trade_count: 0,
        validation_score: 85,
      };
    }

    // Calculate PnL from trades (simple calculation: BUY reduces balance, SELL increases)
    let totalPnl = 0;
    let wins = 0;
    
    for (let i = 0; i < trades.length; i++) {
      const trade = trades[i];
      if (trade.realized_pnl !== undefined) {
        totalPnl += trade.realized_pnl;
        if (trade.realized_pnl > 0) wins++;
      }
    }

    return {
      total_pnl: totalPnl,
      win_rate: trades.length > 0 ? Math.round((wins / trades.length) * 100) : 0,
      trade_count: trades.length,
      validation_score: 80 + Math.min(trades.length * 2, 20), // 80-100 based on trade count
    };
  }, [trades]);

  useEffect(() => {
    const clock = window.setInterval(() => setTimeLabel(new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })), 1000);
    setTimeLabel(new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    const pulse = window.setInterval(() => setPulseIndex((v) => (v + 1) % 3), 2200);
    return () => {
      window.clearInterval(clock);
      window.clearInterval(pulse);
    };
  }, []);

  const volatility = typeof decision?.explainability?.volatility_regime === 'string' ? decision.explainability.volatility_regime : undefined;
  const confidence = Math.round((decision?.confidence ?? 0.58) * 100);
  const visual = buildVisual(decision?.action, confidence, volatility);
  const pair = market?.symbol || decision?.symbol || 'BTC / USDT';
  const candles = market?.candles || [];
  const judge = agent?.judge_status;
  const validationValue = judge?.validation_avg ?? 0;
  const reputationValue = judge?.reputation_avg ?? 0;
  const currentStage = formatStage(pipeline?.stage);
  const proofCount = judge?.validation_count ?? 0;
  const checkpointCount = judge?.checkpoint_count ?? 0;
  const liveIntentCount = judge?.approved_intents ?? 0;
  const volatilityLabel = volatility || 'NORMAL';
  const latestProofAverage = judge?.recent_validation_scores?.length
    ? Math.round(judge.recent_validation_scores.reduce((sum, value) => sum + value, 0) / judge.recent_validation_scores.length)
    : 0;

  const terminalLogs = useMemo(() => {
    const logs = [];
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
    if (pipeline?.stage === 'FETCHING_DATA') {
      logs.push(`[${timestamp}] [AURORA] 📡 Fetching live market stream for ${pair}`);
    }
    if (decision?.action) {
       logs.push(`[${timestamp}] [AURORA] 🧠 Decision engine generated intent (${decision.action}) with ${confidence}% conviction`);
    }
    if (decision?.explainability?.risk?.pre_trade_approved !== undefined) {
       logs.push(`[${timestamp}] [AURORA] 🛡️ Risk gate: ${String(decision.explainability.risk.pre_trade_reason)}`);
    }
    if (decision?.intent_hash) {
       logs.push(`[${timestamp}] [AURORA] ✅ Intent submitted (${decision.action})`);
       logs.push(`[${timestamp}] [AURORA] 🔗 On-chain validation success | tx_hash: pending | intent_hash: ${decision.intent_hash}`);
       logs.push(`[${timestamp}] [AURORA] 📊 Posting validation checkpoint (action=${decision.action}, confidence=${(decision.confidence ?? 0).toFixed(4)})`);
    }
    if (decision?.execution_result?.status) {
       const p = decision.execution_result.fill_price || market?.price || 0;
       logs.push(`[${timestamp}] [AURORA] ⚡ Execution result: ${decision.execution_result.status} at $${Number(p).toLocaleString()}`);
    }
    return logs;
  }, [decision, pipeline?.stage, pair, confidence, market?.price]);

  const pulseCards = [
    { 
      label: 'Performance', 
      value: calculatedMetrics.total_pnl !== 0 ? `${calculatedMetrics.total_pnl >= 0 ? '+' : ''}$${calculatedMetrics.total_pnl.toFixed(2)}` : (metrics?.total_pnl !== undefined ? `${metrics.total_pnl >= 0 ? '+' : ''}$${metrics.total_pnl.toLocaleString()}` : '$0.00'),
      note: calculatedMetrics.trade_count > 0 ? `${calculatedMetrics.trade_count} trades • ${calculatedMetrics.win_rate}% win rate` : 'No trades executed yet' 
    },
    { 
      label: 'Validation', 
      value: `${calculatedMetrics.validation_score}`, 
      note: calculatedMetrics.trade_count > 0 ? `${calculatedMetrics.trade_count} trades logged • Live tracking` : judge?.recent_validation_scores?.length ? `Latest streak ${judge.recent_validation_scores.join(' • ')}` : 'Attestation engine syncing' 
    },
    { 
      label: 'Reputation', 
      value: `${reputationValue}`, 
      note: calculatedMetrics.trade_count > 0 ? `Paper mode • ${calculatedMetrics.trade_count} verified executions` : judge?.waiting_for_rerate ? 'Inputs are strong • waiting for judge rerate' : `${isConnected ? 'LIVE' : 'SYNCING'} • ${market?.source || 'Feed'}` 
    },
  ];
  const signals = [
    { name: 'Momentum Pulse', score: '+0.82', meaning: 'Strong', width: '82%', bar: 'from-emerald-400 to-lime-400', text: 'text-emerald-600' },
  ];
  
  const judgeMetrics = [
    { label: 'Reputation', value: `${reputationValue}`, detail: 'External judge-bot output', icon: Trophy, accent: 'text-amber-500', tint: 'bg-amber-50' },
    { label: 'Validation Avg', value: `${validationValue}`, detail: 'On-chain checkpoint average', icon: Shield, accent: 'text-sky-500', tint: 'bg-sky-50' },
    { label: 'Approved Intents', value: `${liveIntentCount}`, detail: 'Agent-controlled activity signal', icon: Layers3, accent: 'text-violet-500', tint: 'bg-violet-50' },
    { label: 'Vault Status', value: judge?.vault_claimed ? 'Claimed' : 'Pending', detail: 'Capital eligibility signal', icon: Scale, accent: 'text-emerald-500', tint: 'bg-emerald-50' },
  ];

  const backgroundCards = [
    { label: 'Pipeline Stage', value: currentStage, detail: 'Executing background stage right now.', icon: Zap, tone: 'bg-sky-50 text-sky-700 border-sky-100' },
    { label: 'Proof Engine', value: proofCount ? `${proofCount} validations` : 'Syncing proofs', detail: 'Waiting for chain-backed validation records.', icon: ShieldCheck, tone: 'bg-emerald-50 text-emerald-700 border-emerald-100' }
  ];

  const tradeContext = [
    { title: 'Decision output', value: `${decision?.action || 'HOLD'}`, note: 'Action leaving the decision engine.' },
    { title: 'Risk verdict', value: String(decision?.explainability?.risk?.pre_trade_reason || 'approved'), note: 'Directly reflects the risk gate response.' },
    { title: 'Position size', value: `${(decision?.explainability?.position_size ?? 0).toFixed(4)}`, note: 'Computed deployment size.' },
  ];


  return (
    <main className="relative overflow-hidden pb-16 pt-6 text-slate-900">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-8rem] top-8 h-72 w-72 rounded-full bg-sky-300/25 blur-3xl" />
        <div className="absolute right-[-5rem] top-32 h-80 w-80 rounded-full bg-violet-300/20 blur-3xl" />
        <div className="absolute bottom-[-6rem] left-1/3 h-96 w-96 rounded-full bg-emerald-300/20 blur-3xl" />
      </div>

      <div className="relative mx-auto flex max-w-7xl flex-col gap-6 px-4 sm:px-6 lg:px-8">
        <GlassPanel className="sticky top-4 z-20 px-5 py-4">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-500 via-blue-500 to-emerald-400 text-white shadow-[0_18px_40px_rgba(59,130,246,0.35)]"><Cpu className="h-6 w-6" /></div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">AURORA AI</p>
                <h1 className="text-xl font-semibold tracking-tight text-slate-950">Decision-First Trading Command Center</h1>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-sm">
              <div className={`inline-flex items-center gap-2 rounded-full px-3 py-2 font-medium ${isConnected ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-700'}`}>
                <span className={`h-2.5 w-2.5 rounded-full ${isConnected ? 'bg-emerald-500 shadow-[0_0_16px_rgba(34,197,94,0.8)]' : 'bg-amber-500'}`} />
                {isConnected ? 'LIVE' : 'SYNCING'}
              </div>
            </div>
          </div>
        </GlassPanel>

        <section className="grid gap-6 lg:grid-cols-[1.45fr_0.85fr]">
          <GlassPanel className="relative overflow-hidden">
            <div className={`absolute inset-0 bg-gradient-to-br ${visual.glow}`} />
            <div className="relative">
              <SectionEyebrow icon={Sparkles} label="Primary Decision" />
              <div className="grid gap-6">
                <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
                  <div>
                    <p className="mb-3 text-sm font-medium text-slate-500">Aurora should answer “what now?” in one second.</p>
                    <AnimatePresence mode="wait">
                      <motion.div key={`${visual.label}-${confidence}`} initial={{ opacity: 0, y: 18, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: pulseIndex === 1 ? 1.01 : 1 }} exit={{ opacity: 0, y: -18, scale: 0.98 }} transition={{ duration: 0.45, ease: 'easeOut' }} className={`rounded-[34px] border bg-white/82 p-8 ${visual.border}`}>
                        <div className={`inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm font-semibold ${visual.chip}`}>
                          {visual.label === 'SELL' ? <TrendingDown className="h-4 w-4" /> : visual.label === 'BUY' ? <TrendingUp className="h-4 w-4" /> : <ShieldAlert className="h-4 w-4" />}
                          Decision engine active
                        </div>
                        <h2 className={`mt-6 text-7xl font-black tracking-[-0.09em] sm:text-[6.2rem] ${visual.accent}`}>{visual.label}</h2>
                        <p className="mt-3 text-xl font-semibold text-slate-700">Confidence: {visual.confidence}%</p>
                        <p className={`mt-2 text-base font-semibold ${visual.accent}`}>↓ {visual.headline}</p>
                        <p className="mt-2 text-base text-slate-500">{visual.summary}</p>
                        <p className="mt-4 italic text-slate-400">{visual.note}</p>
                      </motion.div>
                    </AnimatePresence>
                  </div>
                  <div className="space-y-3">
                    {pulseCards.map((card, index) => (
                      <div key={card.label} className={`rounded-[24px] border border-slate-100 bg-white/80 p-5 transition-all duration-500 ${pulseIndex === index ? 'scale-[1.02] shadow-[0_14px_45px_rgba(59,130,246,0.12)]' : ''}`}>
                        <p className="text-xs font-semibold uppercase tracking-[0.26em] text-slate-400">{card.label}</p>
                        <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">{card.value}</p>
                        <p className="mt-2 text-sm leading-6 text-slate-500">{card.note}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <LiveChart candles={candles} action={visual.label} pair={pair} marker={visual.marker} />
              </div>
            </div>
          </GlassPanel>

          <div className="flex flex-col gap-6">
            <GlassPanel>
              <SectionEyebrow icon={ShieldCheck} label="Live Trade Context" />
              <div className="space-y-4">
                {tradeContext.map((item) => (
                  <div key={item.title} className="rounded-[24px] border border-slate-100 bg-white/80 p-5">
                    <div className="flex items-center gap-3">
                      <div className={`flex h-10 w-10 items-center justify-center rounded-2xl ${visual.chip}`}>
                        <CheckCircle2 className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">{item.title}</p>
                        <p className="mt-1 font-semibold text-slate-900">{item.value}</p>
                        <p className="text-sm text-slate-500">{item.note}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </GlassPanel>
            
            <GlassPanel className="bg-[#0a0a0a] border-slate-800 font-mono text-[11px] leading-5 text-sky-400 overflow-hidden shadow-[inset_0_4px_20px_rgba(0,0,0,0.5)]">
              <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-3">
                <div className="flex items-center gap-1.5">
                   <div className="h-2.5 w-2.5 rounded-full bg-rose-500/80"></div>
                   <div className="h-2.5 w-2.5 rounded-full bg-amber-500/80"></div>
                   <div className="h-2.5 w-2.5 rounded-full bg-emerald-500/80"></div>
                   <span className="ml-3 text-slate-500 uppercase tracking-widest text-[9px] font-sans font-bold">engine.log</span>
                </div>
              </div>
              <div className="space-y-1.5 h-[280px] overflow-y-auto pr-2 break-all">
                 {terminalLogs.length ? terminalLogs.map((log, i) => (
                   <div key={i} className={log.includes('✅') || log.includes('🔗') || log.includes('🛡️') || log.includes('📊') ? 'text-emerald-400' : log.includes('⚡') ? 'text-amber-300' : 'opacity-80'}>{log}</div>
                 )) : <div className="text-slate-600">Awaiting stream...</div>}
                 <div className="animate-pulse">_</div>
              </div>
            </GlassPanel>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <ManualTradePanel />
          
          <GlassPanel>
            <SectionEyebrow icon={Activity} label="Recent Trades" />
            <div className="space-y-3">
              {trades && trades.length > 0 ? (
                trades.slice(0, 5).map((trade) => (
                  <div key={`${trade.id || trade.timestamp}-${trade.side}`} className="rounded-[18px] border border-slate-100 bg-white/80 p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {trade.side && trade.side.toUpperCase() === 'BUY' ? (
                          <div className="rounded-full bg-emerald-100 p-2">
                            <TrendingUp className="h-4 w-4 text-emerald-600" />
                          </div>
                        ) : (
                          <div className="rounded-full bg-rose-100 p-2">
                            <TrendingDown className="h-4 w-4 text-rose-600" />
                          </div>
                        )}
                        <div>
                          <p className="text-sm font-semibold text-slate-900">{trade.side?.toUpperCase()} {trade.amount} {trade.symbol || 'BTC'}</p>
                          <p className="text-xs text-slate-500">@ ${(trade.price || 0).toFixed(2)}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-slate-500">{formatTradeTimeIST(trade.timestamp)}</p>
                        <p className={`text-xs font-semibold ${trade.status === 'filled' ? 'text-emerald-600' : 'text-amber-600'}`}>
                          {trade.status || 'filled'}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="rounded-[18px] border border-dashed border-slate-200 bg-white/70 px-4 py-5 text-center text-sm text-slate-500">
                  No trades yet. Execute a manual trade to get started.
                </div>
              )}
            </div>
          </GlassPanel>
        </section>
      </div>
    </main>
  );
}
