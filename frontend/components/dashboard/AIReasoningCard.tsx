"use client";

import styles from "./Dashboard.module.css";
import { useDecisionStore } from "@/store/decisionStore";
import { formatNumber } from "@/utils/formatters";

export function AIReasoningCard() {
  const { explanation, reasoningBullets, technicalScore, sentimentScore, mlPrediction } = useDecisionStore();

  return (
    <section className={`${styles.card} ${styles.span5}`}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>AI Reasoning</div>
      </div>
      <div className={styles.subtle}>{explanation || "Waiting for agent backend..."}</div>
      <div className={styles.metricsGrid}>
        <div className={styles.metric}>
          <div className={styles.metricLabel}>Technical</div>
          <div className={styles.metricValue}>{formatNumber(technicalScore)}</div>
        </div>
        <div className={styles.metric}>
          <div className={styles.metricLabel}>Sentiment</div>
          <div className={styles.metricValue}>{formatNumber(sentimentScore)}</div>
        </div>
        <div className={styles.metric}>
          <div className={styles.metricLabel}>ML Prediction</div>
          <div className={styles.metricValue}>{formatNumber(mlPrediction, 4)}</div>
        </div>
      </div>
      <div className={styles.stack}>
        {reasoningBullets.map((bullet, index) => (
          <div key={`${bullet}-${index}`} className={styles.bulletRow}>
            <span className={styles.rowLabel}>R{index + 1}</span>
            <span className={styles.rowVal}>{bullet}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
