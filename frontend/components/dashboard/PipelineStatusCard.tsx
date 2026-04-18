"use client";

import styles from "./Dashboard.module.css";
import { useDecisionStore } from "@/store/decisionStore";

const steps = [
  "FETCHING_DATA",
  "COMPUTING_FEATURES",
  "RUNNING_ML",
  "ANALYZING_SIGNALS",
  "MAKING_DECISION",
  "VALIDATING_RISK",
  "CREATING_INTENT",
  "SIGNING_INTENT",
  "EXECUTING_ORDER",
  "RECORDING_RESULT"
];

export function PipelineStatusCard() {
  const activeStage = useDecisionStore((state) => state.pipelineStage);
  const activeIndex = steps.indexOf(activeStage);

  return (
    <section className={`${styles.card} ${styles.span3}`}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>Pipeline Status</div>
      </div>
      {steps.map((step) => (
        <div
          key={step}
          className={`${styles.pipelineStep} ${
            step === activeStage
              ? styles.pipelineStepActive
              : activeIndex > -1 && steps.indexOf(step) < activeIndex
                ? styles.pipelineStepDone
                : ""
          }`}
        >
          {step}
        </div>
      ))}
    </section>
  );
}
