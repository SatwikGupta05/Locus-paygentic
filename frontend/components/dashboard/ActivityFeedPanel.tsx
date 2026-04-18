"use client";

import styles from "./Dashboard.module.css";
import { useDecisionStore } from "@/store/decisionStore";

export function ActivityFeedPanel() {
  const entries = useDecisionStore((state) => state.activityFeed);

  return (
    <section className={`${styles.card} ${styles.span6}`}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>Activity Feed</div>
      </div>
      {entries.length === 0 ? <div className={styles.emptyState}>No activity yet.</div> : null}
      {entries.map((entry, index) => (
        <div
          key={`${entry.time}-${entry.text}-${index}`}
          className={styles.feedItem}
          data-type={entry.type}
        >
          <span className={styles.feedTime}>{entry.time}</span>
          <span className={styles.feedText}>{entry.text}</span>
        </div>
      ))}
    </section>
  );
}
