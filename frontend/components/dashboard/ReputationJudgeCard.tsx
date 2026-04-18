"use client";

import styles from "./Dashboard.module.css";
import { useReputationStore } from "@/store/reputationStore";
import { formatNumber } from "@/utils/formatters";

export function ReputationJudgeCard() {
  const reputation = useReputationStore();

  return (
    <section className={`${styles.card} ${styles.span4}`}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>Reputation Judge</div>
        <span className={`${styles.badge} ${reputation.rerateIsPending ? styles.badgeWarn : styles.badgeOk}`}>
          {reputation.rerateIsPending ? "Pending" : "Stable"}
        </span>
      </div>
      <div className={styles.mainPrice}>{formatNumber(reputation.reputationScore)}</div>
      <div className={styles.stack}>
        <div className={styles.feedRow}>
          <span className={styles.rowLabel}>Latest Judge Score</span>
          <span className={styles.rowVal}>{formatNumber(reputation.latestJudgeScore)}</span>
        </div>
        <div className={styles.subtle}>{reputation.latestJudgeFeedback || "No judge feedback yet."}</div>
      </div>
    </section>
  );
}
