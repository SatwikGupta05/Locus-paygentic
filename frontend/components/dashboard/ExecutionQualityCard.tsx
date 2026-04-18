"use client";

import styles from "./Dashboard.module.css";
import { useExecutionStore } from "@/store/executionStore";
import { formatCurrency, formatNumber, formatPercent } from "@/utils/formatters";

export function ExecutionQualityCard() {
  const execution = useExecutionStore();
  const slippageAbs = Math.abs(execution.slippage);
  const slippageColor =
    slippageAbs < 0.05 ? "var(--accent)" : slippageAbs < 0.2 ? "var(--accent-amber)" : "var(--accent-red)";

  return (
    <section className={`${styles.card} ${styles.span4}`}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>Execution Quality</div>
      </div>
      <div className={styles.feedRow}>
        <span className={styles.rowLabel}>Exchange</span>
        <span className={styles.rowVal}>{execution.exchange}</span>
      </div>
      <div className={styles.feedRow}>
        <span className={styles.rowLabel}>Fill Price</span>
        <span className={styles.rowVal}>{formatCurrency(execution.fillPrice)}</span>
      </div>
      <div className={styles.feedRow}>
        <span className={styles.rowLabel}>Fill Size</span>
        <span className={styles.rowVal}>{formatNumber(execution.fillSize, 6)}</span>
      </div>
      <div className={styles.feedRow}>
        <span className={styles.rowLabel}>Slippage</span>
        <span className={styles.rowVal} style={{ color: slippageColor }}>{formatPercent(execution.slippage, 3)}</span>
      </div>
      <div className={styles.feedRow}>
        <span className={styles.rowLabel}>Latency</span>
        <span className={styles.rowVal}>{execution.latencyMs} ms</span>
      </div>
    </section>
  );
}
