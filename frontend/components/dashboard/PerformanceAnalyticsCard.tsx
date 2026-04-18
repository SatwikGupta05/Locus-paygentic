"use client";

import styles from "./Dashboard.module.css";
import { EquityCurveChart } from "@/components/charts/EquityCurveChart";
import { useAnalyticsStore } from "@/store/analyticsStore";
import { formatNumber, formatPercent } from "@/utils/formatters";

export function PerformanceAnalyticsCard() {
  const analytics = useAnalyticsStore();

  return (
    <section className={`${styles.card} ${styles.span8}`}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>Performance Analytics</div>
      </div>
      <div className={styles.metricsGrid}>
        <div className={styles.metric}>
          <div className={styles.metricLabel}>Win Rate</div>
          <div className={styles.metricValue}>{formatPercent(analytics.winRate)}</div>
        </div>
        <div className={styles.metric}>
          <div className={styles.metricLabel}>Profit Factor</div>
          <div className={styles.metricValue}>{formatNumber(analytics.profitFactor)}</div>
        </div>
        <div className={styles.metric}>
          <div className={styles.metricLabel}>Sharpe</div>
          <div className={styles.metricValue}>{formatNumber(analytics.sharpeRatio)}</div>
        </div>
      </div>
      <div className={styles.feedRow}>
        <span className={styles.rowLabel}>Max Drawdown</span>
        <span className={styles.rowVal}>{formatPercent(analytics.maxDrawdown)}</span>
      </div>
      <div className={styles.feedRow}>
        <span className={styles.rowLabel}>Consistency</span>
        <span className={styles.rowVal}>{formatPercent(analytics.consistency)}</span>
      </div>
      <div className={styles.chartWrap}>
        <EquityCurveChart points={analytics.equityCurve} />
      </div>
    </section>
  );
}
