import { create } from "zustand";

interface ReputationStore {
  reputationScore: number;
  latestJudgeFeedback: string;
  latestJudgeScore: number;
  rerateIsPending: boolean;
  setReputationState: (payload: Partial<Omit<ReputationStore, "setReputationState">>) => void;
}

export const useReputationStore = create<ReputationStore>((set) => ({
  reputationScore: 0,
  latestJudgeFeedback: "",
  latestJudgeScore: 0,
  rerateIsPending: false,
  setReputationState: (payload) => set(payload)
}));
