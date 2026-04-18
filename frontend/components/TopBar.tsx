"use client";

import { useEffect, useState } from "react";
import styles from "@/components/dashboard/Dashboard.module.css";
import { useMarketStore } from "@/store/marketStore";
import { formatAddress } from "@/utils/formatters";

export function TopBar() {
  const pair = useMarketStore((state) => state.pair);
  const [clock, setClock] = useState("");

  useEffect(() => {
    const tick = () => {
      setClock(
        new Intl.DateTimeFormat([], {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          month: "short",
          day: "2-digit"
        }).format(new Date())
      );
    };

    tick();
    const interval = window.setInterval(tick, 1000);
    return () => window.clearInterval(interval);
  }, []);

  return (
    <header className={styles.topBar}>
      <div className={styles.logoBlock}>
        <div className={styles.logo}>AURORA</div>
        <div className={styles.topBarText}>
          <div className={styles.eyebrow}>Autonomous Protocol Agent</div>
          <h1 className={styles.title}>{pair} Intelligence Console</h1>
        </div>
      </div>
      <div className={styles.topBarMeta}>
        <span className={styles.statusBadge}>Node: Synchronized</span>
        <span className={styles.topMetaPill}>Auth: {formatAddress(process.env.NEXT_PUBLIC_OPERATOR_WALLET ?? "0x...")}</span>
        <span className={styles.clock}>{clock}</span>
      </div>
    </header>

  );
}
