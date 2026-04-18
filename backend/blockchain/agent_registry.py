"""Agent registration and vault claiming for the shared Sepolia contracts."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from backend.blockchain.contracts import ContractManager
from backend.utils.config import ROOT_DIR

logger = logging.getLogger(__name__)

AGENT_ID_FILE = ROOT_DIR / "agent-id.json"


class AgentRegistrar:
    """Handles one-time agent registration on AgentRegistry + vault claim."""

    def __init__(self, cm: ContractManager) -> None:
        self.cm = cm

    def is_registered(self) -> bool:
        """Check if our agentId is already registered on-chain."""
        registry = self.cm.agent_registry
        if not registry or self.cm.settings.agent_id == 0:
            return False
        try:
            return registry.functions.isRegistered(self.cm.settings.agent_id).call()
        except Exception:
            return False

    def register(self) -> dict[str, Any]:
        """Register agent on AgentRegistry. Returns agentId."""
        registry = self.cm.agent_registry
        if not registry:
            logger.warning("No Web3 connection — returning mock registration")
            return {"agent_id": 0, "status": "dry_run", "tx_hash": None}

        # Check if already registered
        if self.cm.settings.agent_id > 0 and self.is_registered():
            logger.info(f"Agent {self.cm.settings.agent_id} already registered")
            return {"agent_id": self.cm.settings.agent_id, "status": "already_registered", "tx_hash": None}

        s = self.cm.settings
        tx = registry.functions.register(
            self.cm.agent_address,
            s.agent_name,
            "Autonomous AI trading agent with ML predictions, risk management, and EIP-712 signed checkpoints",
            ["autonomous_trading", "risk_management", "ml_predictions", "eip712_signing"],
            s.agent_uri,
        ).build_transaction({
            "from": self.cm.operator_address,
            "chainId": s.chain_id,
        })

        tx_hash = self.cm.send_tx(tx, s.wallet_private_key)

        # Parse agentId from event logs
        agent_id = 0
        if tx_hash:
            receipt = self.cm.w3.eth.get_transaction_receipt(tx_hash)
            events = registry.events.AgentRegistered().process_receipt(receipt)
            if events:
                agent_id = events[0]["args"]["agentId"]

        result = {"agent_id": agent_id, "status": "registered", "tx_hash": tx_hash}

        # Persist to file
        AGENT_ID_FILE.write_text(json.dumps(result, indent=2))
        logger.info(f"Agent registered: agentId={agent_id}, tx={tx_hash}")
        return result

    def claim_allocation(self) -> dict[str, Any]:
        """Claim 0.05 ETH sandbox capital from HackathonVault."""
        vault = self.cm.hackathon_vault
        if not vault:
            return {"status": "dry_run", "claimed": False}

        agent_id = self.cm.settings.agent_id
        try:
            already_claimed = vault.functions.hasClaimed(agent_id).call()
            if already_claimed:
                balance = vault.functions.getBalance(agent_id).call()
                logger.info(f"Already claimed. Balance: {self.cm.w3.from_wei(balance, 'ether')} ETH")
                return {"status": "already_claimed", "claimed": True, "balance_wei": balance}
        except Exception as e:
            logger.warning(f"Could not check claim status: {e}")

        tx = vault.functions.claimAllocation(agent_id).build_transaction({
            "from": self.cm.operator_address,
            "chainId": self.cm.settings.chain_id,
        })
        tx_hash = self.cm.send_tx(tx, self.cm.settings.wallet_private_key)
        logger.info(f"Claimed allocation: tx={tx_hash}")
        return {"status": "claimed", "claimed": True, "tx_hash": tx_hash}

    def get_agent_info(self) -> dict[str, Any] | None:
        """Fetch on-chain agent info."""
        registry = self.cm.agent_registry
        if not registry or self.cm.settings.agent_id == 0:
            return None
        try:
            info = registry.functions.getAgent(self.cm.settings.agent_id).call()
            return {
                "operator_wallet": info[0],
                "agent_wallet": info[1],
                "name": info[2],
                "description": info[3],
                "capabilities": info[4],
                "registered_at": info[5],
                "active": info[6],
            }
        except Exception as e:
            logger.error(f"Failed to fetch agent info: {e}")
            return None
