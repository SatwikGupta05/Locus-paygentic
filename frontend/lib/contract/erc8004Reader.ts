import { Contract, JsonRpcProvider, formatUnits } from "ethers";
import type { ContractStateResponse } from "@/types";

export const ERC8004_ABI = [
  "function agentName() view returns (string)",
  "function agentId() view returns (bytes32)",
  "function isRegistered() view returns (bool)",
  "function capitalClaimed() view returns (bool)",
  "function allocatedCapital() view returns (uint256)",
  "function reputationScore() view returns (uint256)",
  "function validationAverage() view returns (uint256)",
  "function validationsPosted() view returns (uint256)",
  "function checkpointCount() view returns (uint256)",
  "function approvedIntents() view returns (uint256)",
  "function totalIntents() view returns (uint256)",
  "function rerateIsPending() view returns (bool)",
  "function latestJudgeFeedback() view returns (string)",
  "function latestJudgeScore() view returns (uint256)",
  "function recentValidationScores() view returns (uint256[])",
  "function latestProofTxHash() view returns (bytes32)"
] as const;

export async function readContractState(): Promise<ContractStateResponse> {
  const rpcUrl = process.env.RPC_URL;
  const contractAddress = process.env.AGENT_CONTRACT_ADDRESS;

  if (!rpcUrl || !contractAddress) {
    throw new Error("Missing RPC_URL or AGENT_CONTRACT_ADDRESS");
  }

  const provider = new JsonRpcProvider(rpcUrl);
  const contract = new Contract(contractAddress, ERC8004_ABI, provider);

  const [
    agentName,
    agentId,
    isRegistered,
    capitalClaimed,
    allocatedCapital,
    reputationScore,
    validationAverage,
    validationsPosted,
    checkpointCount,
    approvedIntents,
    totalIntents,
    rerateIsPending,
    latestJudgeFeedback,
    latestJudgeScore,
    recentValidationScores,
    latestProofTxHash
  ] = await Promise.all([
    contract.agentName(),
    contract.agentId(),
    contract.isRegistered(),
    contract.capitalClaimed(),
    contract.allocatedCapital(),
    contract.reputationScore(),
    contract.validationAverage(),
    contract.validationsPosted(),
    contract.checkpointCount(),
    contract.approvedIntents(),
    contract.totalIntents(),
    contract.rerateIsPending(),
    contract.latestJudgeFeedback(),
    contract.latestJudgeScore(),
    contract.recentValidationScores(),
    contract.latestProofTxHash()
  ]);

  return {
    agentName,
    agentId,
    isRegistered,
    capitalClaimed,
    allocatedCapital: Number(formatUnits(allocatedCapital, 6)),
    reputationScore: Number(reputationScore) / 100,
    validationAverage: Number(validationAverage) / 100,
    validationsPosted: Number(validationsPosted),
    checkpointCount: Number(checkpointCount),
    approvedIntents: Number(approvedIntents),
    totalIntents: Number(totalIntents),
    rerateIsPending,
    latestJudgeFeedback,
    latestJudgeScore: Number(latestJudgeScore) / 100,
    recentValidationScores: (recentValidationScores as bigint[]).map((value) => Number(value) / 100),
    latestProofTxHash
  };
}
