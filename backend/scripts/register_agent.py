from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from backend.blockchain.agent_registry import AgentRegistrar
from backend.blockchain.contracts import ContractManager
from backend.utils.config import ROOT_DIR, get_settings


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROOF_DIR = ROOT_DIR / "proof"
AGENT_PROOF_PATH = PROOF_DIR / "agent-id.json"
REGISTRATION_TX_PATH = PROOF_DIR / "registration-tx.json"


def append_env(values: dict[str, str]) -> None:
    env_path = ROOT_DIR / ".env"
    existing = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    lines = existing.splitlines()
    keys = set(values.keys())
    filtered = [line for line in lines if not any(line.startswith(f"{key}=") for key in keys)]
    for key, value in values.items():
        filtered.append(f"{key}={value}")
    env_path.write_text("\n".join(filtered).strip() + "\n", encoding="utf-8")


def etherscan_url(tx_hash: str | None) -> str | None:
    return f"https://sepolia.etherscan.io/tx/{tx_hash}" if tx_hash else None


def main() -> None:
    settings = get_settings()
    PROOF_DIR.mkdir(parents=True, exist_ok=True)

    if AGENT_PROOF_PATH.exists():
        payload = json.loads(AGENT_PROOF_PATH.read_text(encoding="utf-8"))
        print("Agent already registered:")
        print(json.dumps(payload, indent=2))
        return

    if not settings.wallet_private_key:
        print("ERROR: WALLET_PRIVATE_KEY not set in .env")
        sys.exit(1)

    if not settings.rpc_url:
        print("ERROR: SEPOLIA_RPC_URL not set in .env")
        sys.exit(1)

    cm = ContractManager(settings)
    if not cm.connected:
        print("ERROR: Could not connect to Sepolia RPC")
        sys.exit(1)

    registrar = AgentRegistrar(cm)
    registration = registrar.register()
    claim = registrar.claim_allocation()

    proof_payload = {
        "agent_id": registration.get("agent_id"),
        "agent_wallet": cm.agent_address,
        "operator_wallet": cm.operator_address,
        "registration_tx": registration.get("tx_hash"),
        "registration_url": etherscan_url(registration.get("tx_hash")),
        "claim_tx": claim.get("tx_hash"),
        "claim_url": etherscan_url(claim.get("tx_hash")),
    }
    AGENT_PROOF_PATH.write_text(json.dumps(proof_payload, indent=2), encoding="utf-8")
    REGISTRATION_TX_PATH.write_text(
        json.dumps(
            {
                "registration": registration,
                "claim": claim,
                "registration_url": etherscan_url(registration.get("tx_hash")),
                "claim_url": etherscan_url(claim.get("tx_hash")),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    append_env(
        {
            "AGENT_ID": str(registration.get("agent_id") or ""),
            "AGENT_WALLET_ADDRESS": cm.agent_address,
        }
    )

    print("Registration summary")
    print(f"Agent ID:        {registration.get('agent_id')}")
    print(f"Agent wallet:    {cm.agent_address}")
    print(f"Registration TX: {registration.get('tx_hash')}")
    print(f"Claim TX:        {claim.get('tx_hash')}")
    print(f"Etherscan reg:   {etherscan_url(registration.get('tx_hash'))}")
    print(f"Etherscan claim: {etherscan_url(claim.get('tx_hash'))}")


if __name__ == "__main__":
    main()
