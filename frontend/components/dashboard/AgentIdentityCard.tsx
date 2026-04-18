"use client";

import styles from "./Dashboard.module.css";
import { useReputationStore } from "@/store/reputationStore";
import { useValidationStore } from "@/store/validationStore";
import { formatAddress, formatNumber } from "@/utils/formatters";

export function AgentIdentityCard() {
  const checkpointCount = useValidationStore((state) => state.checkpointCount);
  const reputationScore = useReputationStore((state) => state.reputationScore);

  return (
    <section className={`${styles.card} ${styles.span4}`}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>Agent Identity</div>
        <span className={`${styles.badge} ${styles.badgeLive}`}>ERC-8004</span>
      </div>
      <div className={styles.mainPrice}>AURORA PRIME</div>
      <div className={styles.subtle}>Execution identity, on-chain reputation, and checkpoint lineage.</div>
      <div className={styles.stack}>
        <div className={styles.feedRow}>
          <span className={styles.rowLabel}>Pair</span>
          <span className={styles.rowVal}>{process.env.NEXT_PUBLIC_TRADING_PAIR ?? "BTC/USDT"}</span>
        </div>
        <div className={styles.feedRow}>
          <span className={styles.rowLabel}>Agent Wallet</span>
          <span className={styles.rowVal}>{formatAddress(process.env.NEXT_PUBLIC_AGENT_WALLET ?? "")}</span>
        </div>
        <div className={styles.feedRow}>
          <span className={styles.rowLabel}>Operator</span>
          <span className={styles.rowVal}>{formatAddress(process.env.NEXT_PUBLIC_OPERATOR_WALLET ?? "")}</span>
        </div>
        <div className={styles.feedRow}>
          <span className={styles.rowLabel}>Reputation</span>
          <span className={styles.rowVal}>{formatNumber(reputationScore)}</span>
        </div>
        <div className={styles.feedRow}>
          <span className={styles.rowLabel}>Checkpoints</span>
          <span className={styles.rowVal}>{checkpointCount}</span>
        </div>
      </div>
    </section>
  );
}
