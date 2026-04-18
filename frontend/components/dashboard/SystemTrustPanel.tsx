"use client";

import styles from "./Dashboard.module.css";
import { useDecisionStore } from "@/store/decisionStore";
import { useMarketStore } from "@/store/marketStore";
import { useSystemStore } from "@/store/systemStore";

export function SystemTrustPanel() {
  const system = useSystemStore();
  const exchanges = useMarketStore((state) => state.exchanges);
  const decision = useDecisionStore();
  const fillClass = (health: string) =>
    health === "HEALTHY"
      ? styles.healthFillGreen
      : health === "DEGRADED"
        ? styles.healthFillAmber
        : styles.healthFillRed;
  const fillWidth = (health: string) => (health === "HEALTHY" ? "100%" : health === "DEGRADED" ? "58%" : "28%");

  const exchangeRows = [
    ["Kraken WS", system.exchangeHealth.kraken, exchanges.kraken.lastUpdate],
    ["Binance WS", system.exchangeHealth.binance, exchanges.binance.lastUpdate],
    ["KuCoin WS", system.exchangeHealth.kucoin, exchanges.kucoin.lastUpdate]
  ] as const;

  return (
    <section className={`${styles.card} ${styles.span6}`}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>System Trust</div>
      </div>
      {[
        ["Chain", system.chainHealth],
        ["Proof system", system.proofHealth],
        ["Judge oracle", system.judgeHealth],
        ["ML inference", system.mlHealth]
      ].map(([label, health]) => (
        <div key={label} className={styles.healthRow}>
          <span className={styles.rowLabel}>{label}</span>
          <div className={styles.healthTrack}>
            <div className={fillClass(String(health))} style={{ width: fillWidth(String(health)) }} />
          </div>
          <span className={styles.rowVal}>
            <span className={`${styles.healthDot} ${styles[String(health).toLowerCase()]}`} /> {health}
          </span>
        </div>
      ))}
      {exchangeRows.map(([label, health, lastUpdate]) => (
        <div key={label} className={styles.healthRow}>
          <span className={styles.rowLabel}>{label}</span>
          <div className={styles.healthTrack}>
            <div className={fillClass(String(health))} style={{ width: fillWidth(String(health)) }} />
          </div>
          <span className={styles.rowVal}>
            <span className={`${styles.healthDot} ${styles[String(health).toLowerCase()]}`} /> {health} /{" "}
            {lastUpdate ? `${Math.round((Date.now() - lastUpdate) / 1000)}s ago` : "--"}
          </span>
        </div>
      ))}
      <div className={styles.feedRow}>
        <span className={styles.rowLabel}>Decision freshness</span>
        <span className={styles.rowVal}>{decision.stale ? "Stale" : "Live"}</span>
      </div>
    </section>
  );
}
