"""EIP-712 intent signer for the shared RiskRouter contract.

Domain and type struct MUST exactly match the deployed RiskRouter on Sepolia
or all submitTradeIntent() calls will revert.
"""
from __future__ import annotations

import logging
import time
from hashlib import sha256
from typing import Any

from eth_account import Account
from eth_account.messages import encode_typed_data

from backend.blockchain.contracts import ContractManager

logger = logging.getLogger(__name__)


# ─── EIP-712 Domain (MUST match RiskRouter) ────────────────────────────────────
RISK_ROUTER_DOMAIN = {
    "name": "RiskRouter",
    "version": "1",
    "chainId": 11155111,
    "verifyingContract": "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC",
}

# ─── TradeIntent struct type (MUST match contract exactly) ──────────────────────
TRADE_INTENT_TYPES = {
    "TradeIntent": [
        {"name": "agentId", "type": "uint256"},
        {"name": "agentWallet", "type": "address"},
        {"name": "pair", "type": "string"},
        {"name": "action", "type": "string"},
        {"name": "amountUsdScaled", "type": "uint256"},
        {"name": "maxSlippageBps", "type": "uint256"},
        {"name": "nonce", "type": "uint256"},
        {"name": "deadline", "type": "uint256"},
    ]
}

# ─── Checkpoint type for ValidationRegistry ─────────────────────────────────────
AGENT_REGISTRY_DOMAIN = {
    "name": "AITradingAgent",
    "version": "1",
    "chainId": 11155111,
    "verifyingContract": "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3",
}

CHECKPOINT_TYPES = {
    "Checkpoint": [
        {"name": "agentId", "type": "uint256"},
        {"name": "timestamp", "type": "uint256"},
        {"name": "action", "type": "string"},
        {"name": "pair", "type": "string"},
        {"name": "amountUsdScaled", "type": "uint256"},
        {"name": "priceUsdScaled", "type": "uint256"},
        {"name": "reasoningHash", "type": "bytes32"},
    ]
}


class IntentSigner:
    """Signs TradeIntents with EIP-712 for the shared RiskRouter contract."""

    def __init__(self, cm: ContractManager) -> None:
        self.cm = cm
        self.agent_account = cm.agent_account
        self.private_key = cm.settings.agent_wallet_private_key

        # Update domain with actual contract address from settings
        self.domain = {
            **RISK_ROUTER_DOMAIN,
            "chainId": cm.settings.chain_id,
            "verifyingContract": cm.settings.risk_router_address,
        }

    @property
    def wallet_address(self) -> str:
        return self.agent_account.address if self.agent_account else "0x" + "0" * 40

    def build_trade_intent(
        self,
        pair: str,
        action: str,
        amount_usd: float,
        max_slippage_bps: int = 100,
        nonce: int | None = None,
    ) -> dict[str, Any]:
        """Build a TradeIntent struct matching the RiskRouter contract."""
        if nonce is None:
            nonce = self._resolve_intent_nonce()

        intent = {
            "agentId": self.cm.settings.agent_id,
            "agentWallet": self.wallet_address,
            "pair": pair,
            "action": action.upper(),
            "amountUsdScaled": int(amount_usd * 100),  # $500 → 50000
            "maxSlippageBps": max_slippage_bps,
            "nonce": nonce,
            "deadline": int(time.time()) + 300,  # 5 min expiry
        }
        return intent

    def _resolve_intent_nonce(self) -> int:
        """Resolve the next usable signing nonce without crashing the trading loop."""
        agent_id = self.cm.settings.agent_id
        nonce_errors: list[str] = []

        router = self.cm.risk_router
        if router:
            try:
                return int(router.functions.getIntentNonce(agent_id).call())
            except Exception as exc:
                nonce_errors.append(f"risk_router.getIntentNonce failed: {exc}")

        registry = self.cm.agent_registry
        if registry:
            try:
                return int(registry.functions.getSigningNonce(agent_id).call())
            except Exception as exc:
                nonce_errors.append(f"agent_registry.getSigningNonce failed: {exc}")

        fallback_nonce = int(time.time())
        if nonce_errors:
            logger.warning(
                "Falling back to timestamp nonce for agent %s. %s",
                agent_id,
                " | ".join(nonce_errors),
            )
        return fallback_nonce

    def sign_intent(self, intent: dict[str, Any]) -> dict[str, Any]:
        """Sign a TradeIntent with EIP-712 and return signature + hash."""
        intent_hash = "0x" + sha256(str(intent).encode()).hexdigest()

        if self.agent_account:
            signable = encode_typed_data(
                domain_data=self.domain,
                message_types=TRADE_INTENT_TYPES,
                message_data=intent,
            )
            signed = Account.sign_message(signable, self.private_key)
            signature = signed.signature.hex()
        else:
            signature = "demo-signature"

        logger.info(
            f"Signed TradeIntent: pair={intent['pair']} action={intent['action']} "
            f"amount=${intent['amountUsdScaled']/100:.2f} hash={intent_hash[:18]}..."
        )

        return {
            "intent": intent,
            "intent_hash": intent_hash,
            "signature": signature,
            "signer": self.wallet_address,
        }

    def build_checkpoint_hash(
        self,
        action: str,
        pair: str,
        amount_usd: float,
        price_usd: float,
        reasoning: str,
    ) -> bytes:
        """Build a deterministic checkpointHash for ValidationRegistry."""
        from web3 import Web3 as W3

        reasoning_hash = W3.keccak(text=reasoning)
        checkpoint_data = {
            "agentId": self.cm.settings.agent_id,
            "timestamp": int(time.time()),
            "action": action,
            "pair": pair,
            "amountUsdScaled": int(amount_usd * 100),
            "priceUsdScaled": int(price_usd * 100),
            "reasoningHash": reasoning_hash,
        }

        if self.agent_account:
            signable = encode_typed_data(
                domain_data={
                    **AGENT_REGISTRY_DOMAIN,
                    "chainId": self.cm.settings.chain_id,
                    "verifyingContract": self.cm.settings.agent_registry_address,
                },
                message_types=CHECKPOINT_TYPES,
                message_data=checkpoint_data,
            )
            # The hash IS the signable message hash — this is what we post
            return signable.body
        else:
            # Dry-run: use keccak of serialized data
            return W3.keccak(text=str(checkpoint_data))
