import sys

path = 'frontend/app/dashboard/page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Imports
target_imports = """  TrendingUp,
  Waves,
  Zap,
} from 'lucide-react';
import type { ReactNode } from 'react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useStore } from '@/lib/store';"""
replacement_imports = """  TrendingUp,
  Waves,
  Zap,
  MessageSquare,
  Target,
} from 'lucide-react';
import type { ReactNode } from 'react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useStore, type AgentNarrative } from '@/lib/store';"""
text = text.replace(target_imports, replacement_imports)

# 2. State
target_state = """  ];

  return (
    <main className="relative overflow-hidden pb-16 pt-6 text-slate-900">"""
replacement_state = """  ];

  const narrativeState = (decision?.audit?.narrative) as AgentNarrative | undefined;

  return (
    <main className="relative overflow-hidden pb-16 pt-6 text-slate-900">"""
text = text.replace(target_state, replacement_state)

# 3. Component
target_ui = """          </GlassPanel>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">"""
replacement_ui = """          </GlassPanel>
        </section>

        <GlassPanel className="overflow-hidden bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-[#020617] px-8 py-8 text-white shadow-[0_20px_60px_rgba(15,23,42,0.25)]">
          <SectionEyebrow icon={MessageSquare} label="Aurora Explaining AI" />
          
          {narrativeState ? (
            <div className="mt-4 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-[24px] border border-white/10 bg-white/5 p-5 transition-all hover:bg-white/10">
                <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">
                  <Bot className="h-4 w-4" /> Decision
                </p>
                <div className="mt-4 flex items-baseline gap-2">
                  <span className={`text-4xl font-black ${narrativeState.decision === 'BUY' ? 'text-emerald-400' : narrativeState.decision === 'SELL' ? 'text-rose-400' : 'text-slate-200'}`}>
                    {narrativeState.decision}
                  </span>
                  <span className="text-sm font-semibold tracking-wider text-slate-400 uppercase ml-2">{narrativeState.confidence_level}</span>
                </div>
              </div>

              <div className="rounded-[24px] border border-white/10 bg-white/5 p-5 transition-all hover:bg-white/10">
                <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.24em] text-emerald-300">
                  <Activity className="h-4 w-4" /> Opportunity
                </p>
                <p className="mt-4 text-sm leading-6 text-slate-300">{narrativeState.opportunity_description}</p>
              </div>

              <div className="rounded-[24px] border border-white/10 bg-white/5 p-5 transition-all hover:bg-white/10">
                <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.24em] text-amber-300">
                  <Target className="h-4 w-4" /> Expected Edge
                </p>
                <p className="mt-4 text-sm leading-6 text-slate-300">{narrativeState.expected_edge}</p>
              </div>

              <div className="rounded-[24px] border border-white/10 bg-white/5 p-5 transition-all hover:bg-white/10">
                <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.24em] text-violet-300">
                  <ArrowRight className="h-4 w-4" /> Exit Strategy
                </p>
                <p className="mt-4 text-sm leading-6 text-slate-300">{narrativeState.exit_condition}</p>
                <div className="mt-3 inline-flex items-center gap-2 rounded-full bg-slate-900/80 px-3 py-1.5 text-xs text-slate-400">
                  Allocation: {narrativeState.capital_allocation}
                </div>
              </div>
            </div>
          ) : (
            <div className="mt-4 rounded-[24px] border border-white/5 bg-white/5 p-8 text-center text-sm text-slate-500">
              Awaiting narrative generation from ML backend...
            </div>
          )}
          {narrativeState?.risk_warning && (
            <div className="mt-4 flex items-center gap-3 rounded-2xl bg-amber-500/10 px-5 py-4 border border-amber-500/20 text-sm text-amber-200">
              <ShieldAlert className="h-5 w-5 shrink-0 text-amber-400" />
              {narrativeState.risk_warning}
            </div>
          )}
        </GlassPanel>

        <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">"""
text = text.replace(target_ui, replacement_ui)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated frontend page.')
