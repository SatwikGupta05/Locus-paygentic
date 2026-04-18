"use client";

import { PlayCircle } from "lucide-react";
import { useState } from "react";
import { getJson, API_BASE } from "../lib/api";
import { useStore } from "../lib/store";

export function ReplayMode() {
  const [loading, setLoading] = useState(false);
  const connect = useStore(s => s.connect);

  const handleReplay = async () => {
    setLoading(true);
    try {
      // Direct REST call to trigger backend replay event or local frontend fetch
      // We will grab the audit trail and mock the pipeline stages into Zustand
      const audit = await getJson<{items: any[]}>("/audit-trail");
      if (!audit.items.length) return;
      
      const latest = audit.items[0]; // grab most recent historical trade
      
      // We push a mock WebSocket event to simulate live UI replay
      // For a quick and robust hackathon demo, we update the store directly by emitting to local state:
      
      const mockEvent = (stage: string, ms: number) => new Promise(res => {
        setTimeout(() => {
          useStore.setState({ pipeline: { stage, data: latest } });
          res(null);
        }, ms);
      });

      await mockEvent("FETCHING_DATA", 500);
      await mockEvent("COMPUTING_FEATURES", 800);
      await mockEvent("RUNNING_ML", 1000);
      await mockEvent("VALIDATING_RISK", 800);
      await mockEvent("CREATING_INTENT", 500);
      await mockEvent("INTENT_SIGNED", 600);
      await mockEvent("EXECUTING_ORDER", 800);
      await mockEvent("RECORDING_RESULT", 500);
      await mockEvent("CYCLE_COMPLETE", 500);

    } catch (e) {
      console.error("Replay failed", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button 
      onClick={handleReplay}
      disabled={loading}
      className="flex items-center gap-2 bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border border-purple-500/20 rounded px-3 py-1.5 text-xs font-semibold tracking-widest uppercase transition-colors"
    >
      <PlayCircle size={14} className={loading ? "animate-spin" : ""} />
      {loading ? "Replaying..." : "Replay Last Trade"}
    </button>
  );
}
