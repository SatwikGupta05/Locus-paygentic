import sys

path = 'frontend/app/dashboard/page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# target block to remove
target = """        <section className="col-span-full">
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
                </div>
              </div>
            ) : (
              <div className="mt-4 rounded-[24px] border border-white/5 bg-white/5 p-8 text-center text-sm text-slate-500">
                Awaiting narrative generation from ML backend...
              </div>
            )}
          </GlassPanel>
        </section>"""

if target in text:
    text = text.replace(target, "")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Explaining AI section removed.")
else:
    print("Could not find the target text block to remove.")
