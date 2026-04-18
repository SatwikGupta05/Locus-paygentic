"use client";

import { useEffect, useRef } from "react";
import { useStore } from "../lib/store";

export function StoreInitializer() {
  const connectWebSockets = useStore(state => state.connectWebSockets);
  const refreshSnapshot = useStore(state => state.refreshSnapshot);
  const initialized = useRef(false);
  
  useEffect(() => {
    if (!initialized.current) {
      connectWebSockets();
      refreshSnapshot().catch(console.error);
      initialized.current = true;
    }

    const interval = window.setInterval(() => {
      refreshSnapshot().catch(console.error);
    }, 15000);

    return () => {
      window.clearInterval(interval);
    };
  }, [connectWebSockets, refreshSnapshot]);

  return null;
}
