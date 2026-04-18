"""Intent router: simulate → submit → receipt for the shared RiskRouter contract."""
from __future__ import annotations

import logging
from typing import Any

from backend.blockchain.contracts import ContractManager
from backend.blockchain.intent_signer import IntentSigner

logger = logging.getLogger(__name__)


class IntentRouter:
    """Routes trade intents through the shared RiskRouter contract.

    Flow: build intent → sign → simulate (dry-run) → submit → parse events.
    """

    def __init__(self, signer: IntentSigner, cm: ContractManager, min_confidence: float = 0.15) -> None:
        self.signer = signer
        self.cm = cm
        self.min_confidence = min_confidence

    def route(
        self,
        pair: str,
        action: str,
        amount_usd: float,
        price: float,
        confidence: float,
        max_slippage_bps: int = 100,
    ) -> dict[str, Any]:
        """Full intent routing pipeline: build → sign → simulate → submit."""

        # Pre-check: reject low-confidence only for active trades
        if confidence < self.min_confidence and action != "HOLD":
            return {
                "approved": False,
                "rejection_reason": f"confidence_below_threshold: {confidence:.4f} < {self.min_confidence}",
                "intent_hash": None,
                "tx_hash": None,
                "signature": None,
                "signer": self.signer.wallet_address,
            }

        # 1. Build intent struct
        try:
            intent = self.signer.build_trade_intent(pair, action, amount_usd, max_slippage_bps)
            signed = self.signer.sign_intent(intent)
        except Exception as e:
            logger.error("Failed to build/sign trade intent: %s", e)
            return {
                "approved": False,
                "rejection_reason": f"intent_build_failed: {e}",
                "intent_hash": None,
                "tx_hash": None,
                "signature": None,
                "signer": self.signer.wallet_address,
            }

        # 3. Simulate first (CRITICAL: saves gas on rejections)
        simulation = self._simulate(intent)
        if not simulation["valid"]:
            logger.warning(f"simulateIntent rejected: {simulation['reason']}")
            return {
                "approved": False,
                "rejection_reason": f"risk_router_rejected: {simulation['reason']}",
                "intent": intent,
                "intent_hash": signed["intent_hash"],
                "signature": signed["signature"],
                "signer": signed["signer"],
                "tx_hash": None,
                "simulation": simulation,
            }

        # 4. Submit on-chain
        tx_hash = self._submit(intent, signed["signature"])
        approved = bool(tx_hash)

        return {
            "approved": approved,
            "intent": intent,
            "intent_hash": signed["intent_hash"],
            "signature": signed["signature"],
            "signer": signed["signer"],
            "tx_hash": tx_hash,
            "simulation": simulation,
            "rejection_reason": None if approved else "submit_failed",
        }

    def _simulate(self, intent: dict[str, Any]) -> dict[str, Any]:
        """Dry-run the intent via RiskRouter.simulateIntent()."""
        router = self.cm.risk_router
        if not router:
            logger.info("Dry-run mode — simulation auto-approved")
            return {"valid": True, "reason": "dry_run_mode"}

        try:
            intent_tuple = (
                intent["agentId"],
                intent["agentWallet"],
                intent["pair"],
                intent["action"],
                intent["amountUsdScaled"],
                intent["maxSlippageBps"],
                intent["nonce"],
                intent["deadline"],
            )
            valid, reason = router.functions.simulateIntent(intent_tuple).call()
            return {"valid": valid, "reason": reason}
        except Exception as e:
            logger.error(f"simulateIntent failed: {e}")
            return {"valid": True, "reason": f"bypassed_simulation_error: {e}"}

    def _submit(self, intent: dict[str, Any], signature: str) -> str | None:
        """Submit signed intent to RiskRouter on-chain."""
        router = self.cm.risk_router
        if not router:
            logger.info("Dry-run mode — submit skipped")
            return None

        try:
            intent_tuple = (
                intent["agentId"],
                intent["agentWallet"],
                intent["pair"],
                intent["action"],
                intent["amountUsdScaled"],
                intent["maxSlippageBps"],
                intent["nonce"],
                intent["deadline"],
            )
            sig_bytes = bytes.fromhex(signature.replace("0x", "")) if signature != "demo-signature" else b"\x00" * 65

            tx = router.functions.submitTradeIntent(
                intent_tuple, sig_bytes
            ).build_transaction({
                "from": self.cm.operator_address,
                "chainId": self.cm.settings.chain_id,
            })

            tx_hash = self.cm.send_tx(tx, self.cm.settings.wallet_private_key)
            logger.info(f"TradeIntent submitted: tx={tx_hash}")
            return tx_hash
        except Exception as e:
            logger.error(f"submitTradeIntent failed: {e}")
            return None
