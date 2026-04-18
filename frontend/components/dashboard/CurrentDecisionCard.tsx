"use client";

import styles from "./Dashboard.module.css";
import { useDecisionStore } from "@/store/decisionStore";
import { formatCurrency, formatPercent } from "@/utils/formatters";

export function CurrentDecisionCard() {
  const decision = useDecisionStore();
  const confidenceWidth = Math.max(0, Math.min(100, decision.confidence * 100));
  const badgeClass =
    decision.decision === "BUY"
      ? styles.badgeBuy
      : decision.decision === "SELL"
        ? styles.badgeSell
        : styles.badgeHold;
  const decisionClass =
    decision.decision === "BUY"
      ? styles.decisionBuy
      : decision.decision === "SELL"
        ? styles.decisionSell
        : styles.decisionHold;

  return (
    <section className={`${styles.card} ${styles.span4}`}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>Current Decision</div>
        <span className={`${styles.badge} ${badgeClass}`}>{decision.tradeType}</span>
      </div>
      <div className={`${styles.decisionAction} ${decisionClass}`}>{decision.decision}</div>
      <div className={styles.subtle}>{decision.explanation || "Waiting for decision context."}</div>
      <div className={styles.stack}>
        <div>
          <div className={styles.metricLabel}>Confidence {formatPercent(confidenceWidth)}</div>
          <div className={styles.confidenceBar}>
            <div
              className={styles.confidenceFill}
              style={{ width: `${confidenceWidth}%` }}
            />
          </div>
        </div>
        <div className={styles.feedRow}>
          <span className={styles.rowLabel}>Target Exchange</span>
          <span className={styles.rowVal}>{decision.targetExchange}</span>
        </div>
        <div className={styles.feedRow}>
          <span className={styles.rowLabel}>Intent Price</span>
          <span className={styles.rowVal}>{formatCurrency(decision.intentPrice)}</span>
        </div>
        <div className={styles.feedRow}>
          <span className={styles.rowLabel}>Position Size</span>
          <span className={styles.rowVal}>{decision.positionSize}</span>
        </div>
      </div>
    </section>
  );
}
