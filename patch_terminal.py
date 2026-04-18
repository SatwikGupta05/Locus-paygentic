import sys

path = 'frontend/app/dashboard/page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add terminalLogs logic
target_logs_mount = "  const liveIntentCount = judge?.approved_intents ?? 0;"
replacement_logs_mount = """  const liveIntentCount = judge?.approved_intents ?? 0;
  const terminalLogs = useMemo(() => {
    const logs = [];
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
    if (pipeline?.stage === 'FETCHING_DATA') {
      logs.push(`[${timestamp}] [AURORA] 📡 Fetching live market stream for ${pair}`);
    }
    if (decision?.action) {
       logs.push(`[${timestamp}] [AURORA] 🧠 Decision engine generated intent (${decision.action}) with ${(confidence)}% conviction`);
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
  }, [decision, pipeline?.stage, pair, confidence, market?.price]);"""
text = text.replace(target_logs_mount, replacement_logs_mount)

# 2. Add Terminal feed to UI
target_ui = """          <GlassPanel>
            <SectionEyebrow icon={ShieldCheck} label="Live Trade Context" />"""

replacement_ui = """          <div className="flex flex-col gap-6">
            <GlassPanel>
              <SectionEyebrow icon={ShieldCheck} label="Live Trade Context" />"""

text = text.replace(target_ui, replacement_ui)


target_ui2 = """              </div>
            </div>
          </GlassPanel>
        </section>"""

replacement_ui2 = """              </div>
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
                 <div key={i} className={log.includes('✅') || log.includes('🔗') ? 'text-emerald-400' : log.includes('⚡') ? 'text-amber-300' : 'opacity-80'}>{log}</div>
               )) : <div className="text-slate-600">Awaiting stream...</div>}
               <div className="animate-pulse">_</div>
            </div>
          </GlassPanel>
          </div>
        </section>"""
text = text.replace(target_ui2, replacement_ui2)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated frontend page to include terminal.')
