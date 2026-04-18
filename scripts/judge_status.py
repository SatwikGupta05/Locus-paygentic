from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.utils.config import ROOT_DIR, get_settings
from backend.blockchain.contracts import ContractManager


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def main() -> None:
    settings = get_settings()
    cm = ContractManager(settings)

    checkpoints = [r for r in load_jsonl(ROOT_DIR / "checkpoints.jsonl") if r.get("agent_id") == settings.agent_id]
    approved_intents = sum(1 for r in checkpoints if r.get("intent_tx_hash"))
    validations = sum(1 for r in checkpoints if r.get("validation_tx_hash"))
    recent_scores = [r.get("score", 0) for r in checkpoints[-8:]]

    reputation_avg = cm.reputation_registry.functions.getAverageScore(settings.agent_id).call() if cm.reputation_registry else 0
    validation_avg = cm.validation_registry.functions.getAverageValidationScore(settings.agent_id).call() if cm.validation_registry else 0
    vault_claimed = bool(cm.hackathon_vault.functions.hasClaimed(settings.agent_id).call()) if cm.hackathon_vault else False

    feedback_history = []
    if cm.reputation_registry:
        abi = [{
            "type": "function",
            "name": "getFeedbackHistory",
            "stateMutability": "view",
            "inputs": [{"name": "agentId", "type": "uint256"}],
            "outputs": [{
                "components": [
                    {"name": "rater", "type": "address"},
                    {"name": "score", "type": "uint8"},
                    {"name": "outcomeRef", "type": "bytes32"},
                    {"name": "comment", "type": "string"},
                    {"name": "timestamp", "type": "uint256"},
                    {"name": "feedbackType", "type": "uint8"},
                ],
                "type": "tuple[]",
            }],
        }]
        registry = cm.w3.eth.contract(address=cm.w3.to_checksum_address(settings.reputation_registry_address), abi=abi)
        try:
            feedback_history = registry.functions.getFeedbackHistory(settings.agent_id).call()
        except Exception:
            feedback_history = []

    print(f"agent_id={settings.agent_id}")
    print(f"reputation_avg={reputation_avg}")
    print(f"validation_avg={validation_avg}")
    print(f"vault_claimed={vault_claimed}")
    print(f"local_approved_intents={approved_intents}")
    print(f"local_validations={validations}")
    print(f"recent_validation_scores={recent_scores}")
    print(f"feedback_entries={len(feedback_history)}")
    for item in feedback_history[-3:]:
        print("feedback=", item)


if __name__ == "__main__":
    main()
