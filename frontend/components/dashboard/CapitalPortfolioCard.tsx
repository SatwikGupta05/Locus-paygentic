"use client";

import styles from "./Dashboard.module.css";
import { usePortfolioStore } from "@/store/portfolioStore";
import { formatCurrency } from "@/utils/formatters";

export function CapitalPortfolioCard() {
  const { balances, totalBalance, allocatedCapital, totalPnL } = usePortfolioStore();

  return (
    <section className={`${styles.card} ${styles.span4}`}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>Capital Portfolio</div>
      </div>
      <div className={styles.miniGrid}>
        {Object.entries(balances).map(([exchange, value]) => (
          <div key={exchange} className={styles.metric}>
            <div className={styles.metricLabel}>{exchange}</div>
            <div className={styles.metricValue}>{formatCurrency(value)}</div>
          </div>
        ))}
      </div>
      <div className={styles.stack}>
        <div className={styles.feedRow}>
          <span className={styles.rowLabel}>Total Aggregated Balance</span>
          <span className={styles.rowVal}>{formatCurrency(totalBalance)}</span>
        </div>
        <div className={styles.feedRow}>
          <span className={styles.rowLabel}>Allocated Capital</span>
          <span className={styles.rowVal}>{formatCurrency(allocatedCapital)}</span>
        </div>
        <div className={styles.feedRow}>
          <span className={styles.rowLabel}>Total PnL</span>
          <span className={styles.rowVal}>{formatCurrency(totalPnL)}</span>
        </div>
      </div>
    </section>
  );
}
