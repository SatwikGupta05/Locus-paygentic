import { create } from "zustand";

interface ValidationStore {
  validationAverage: number;
  validationsPosted: number;
  checkpointCount: number;
  approvedIntents: number;
  totalIntents: number;
  recentValidationScores: number[];
  latestProofTxHash: string;
  setValidationState: (payload: Partial<Omit<ValidationStore, "setValidationState">>) => void;
}

export const useValidationStore = create<ValidationStore>((set) => ({
  validationAverage: 0,
  validationsPosted: 0,
  checkpointCount: 0,
  approvedIntents: 0,
  totalIntents: 0,
  recentValidationScores: [],
  latestProofTxHash: "",
  setValidationState: (payload) => set(payload)
}));
