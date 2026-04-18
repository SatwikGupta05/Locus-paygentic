"use client";

import styles from "./Dashboard.module.css";
import { useSystemStore } from "@/store/systemStore";

export function ExchangeHealthBar() {
  const exchangeHealth = useSystemStore((state) => state.exchangeHealth);
  const trackClass = (health: string) =>
    health === "HEALTHY"
      ? styles.healthFillGreen
      : health === "DEGRADED"
        ? styles.healthFillAmber
        : styles.healthFillRed;
  const trackWidth = (health: string) => (health === "HEALTHY" ? "100%" : health === "DEGRADED" ? "60%" : "30%");

  return (
    <section className={`${styles.card} ${styles.span12}`}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>Exchange Health</div>
      </div>
      {Object.entries(exchangeHealth).map(([exchange, health]) => (
        <div key={exchange} className={styles.healthRow}>
          <span className={styles.rowLabel}>{exchange}</span>
          <div className={styles.healthTrack}>
            <div className={trackClass(health)} style={{ width: trackWidth(health) }} />
          </div>
          <span className={styles.rowVal}>
            <span className={`${styles.healthDot} ${styles[health.toLowerCase()]}`} /> {health}
          </span>
        </div>
      ))}
    </section>
  );
}
