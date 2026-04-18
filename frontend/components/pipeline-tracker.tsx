"use client";

import { useStore } from "../lib/store";
import { CheckCircle2, CircleDashed, Loader2 } from "lucide-react";

const STAGES = [
  "FETCHING_DATA",
  "COMPUTING_FEATURES",
  "RUNNING_ML",
  "ANALYZING_SIGNALS",
  "VALIDATING_RISK",
  "MAKING_DECISION",
  "CREATING_INTENT",
  "SIGNING_INTENT",
  "EXECUTING_ORDER",
  "RECORDING_RESULT"
];

export function PipelineTracker() {
  const pipeline = useStore((state) => state.pipeline);
  const currentStage = pipeline?.stage || "IDLE";

  const currentIndex = STAGES.indexOf(currentStage);

  return (
    <div className="panel">
      <h2 className="mb-4 text-sm font-semibold tracking-widest text-foam opacity-80 uppercase">
        Live Execution Pipeline
      </h2>
      <div className="space-y-3">
        {STAGES.map((stage, i) => {
          const isPast = currentIndex > i || currentStage === "CYCLE_COMPLETE";
          const isCurrent = currentIndex === i;
          
          return (
            <div key={stage} className={`flex items-center gap-3 text-xs md:text-sm transition-opacity duration-300 ${isPast || isCurrent ? 'opacity-100' : 'opacity-30'}`}>
              {isCurrent ? (
                <Loader2 size={16} className="text-foam animate-spin" />
              ) : isPast ? (
                <CheckCircle2 size={16} className="text-green-400" />
              ) : (
                <CircleDashed size={16} className="text-white/40" />
              )}
              <span className={`font-mono ${isCurrent ? 'text-foam font-bold' : isPast ? 'text-white/80' : 'text-white/40'}`}>
                {stage}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
