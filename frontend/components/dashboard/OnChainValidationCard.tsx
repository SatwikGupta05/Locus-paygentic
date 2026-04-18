"use client";

import styles from "./Dashboard.module.css";
import { ValidationBarChart } from "@/components/charts/ValidationBarChart";
import { useValidationStore } from "@/store/validationStore";
import { formatNumber } from "@/utils/formatters";

export function OnChainValidationCard() {
  const validation = useValidationStore();

  return (
    <section className={`${styles.card} ${styles.span4}`}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>On-Chain Validation</div>
      </div>
      <div className={styles.metricsGrid}>
        <div className={styles.metric}>
          <div className={styles.metricLabel}>Average</div>
          <div className={styles.metricValue}>{formatNumber(validation.validationAverage)}</div>
        </div>
        <div className={styles.metric}>
          <div className={styles.metricLabel}>Posted</div>
          <div className={styles.metricValue}>{validation.validationsPosted}</div>
        </div>
        <div className={styles.metric}>
          <div className={styles.metricLabel}>Approved</div>
          <div className={styles.metricValue}>{validation.approvedIntents}</div>
        </div>
      </div>
      <div className={styles.chartWrap}>
        <ValidationBarChart values={validation.recentValidationScores} />
      </div>
    </section>
  );
}
