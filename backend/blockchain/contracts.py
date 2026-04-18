"""Centralized Web3 contract factory for the 5 shared Sepolia hackathon contracts.

This module provides a singleton Web3 provider and typed contract accessors.
All ABIs come directly from SHARED_CONTRACTS.md — do NOT modify them.
"""
from __future__ import annotations

import logging
from typing import Any

from web3 import Web3
from web3.contract import Contract
from eth_account import Account

from backend.utils.config import Settings

logger = logging.getLogger(__name__)


# ─── ABIs (proper JSON format for Web3.py) ─────────────────────────────────────
# Every ABI entry MUST be a dict, not a Solidity-style string.

AGENT_REGISTRY_ABI: list[dict] = [
    {
        "type": "function",
        "name": "register",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "agentWallet", "type": "address", "internalType": "address"},
            {"name": "name", "type": "string", "internalType": "string"},
            {"name": "description", "type": "string", "internalType": "string"},
            {"name": "capabilities", "type": "string[]", "internalType": "string[]"},
            {"name": "agentURI", "type": "string", "internalType": "string"},
        ],
        "outputs": [
            {"name": "agentId", "type": "uint256", "internalType": "uint256"},
        ],
    },
    {
        "type": "function",
        "name": "isRegistered",
        "stateMutability": "view",
        "inputs": [{"name": "agentId", "type": "uint256", "internalType": "uint256"}],
        "outputs": [{"name": "", "type": "bool", "internalType": "bool"}],
    },
    {
        "type": "function",
        "name": "getAgent",
        "stateMutability": "view",
        "inputs": [{"name": "agentId", "type": "uint256", "internalType": "uint256"}],
        "outputs": [
            {
                "name": "",
                "type": "tuple",
                "internalType": "struct AgentRegistry.AgentInfo",
                "components": [
                    {"name": "operatorWallet", "type": "address", "internalType": "address"},
                    {"name": "agentWallet", "type": "address", "internalType": "address"},
                    {"name": "name", "type": "string", "internalType": "string"},
                    {"name": "description", "type": "string", "internalType": "string"},
                    {"name": "capabilities", "type": "string[]", "internalType": "string[]"},
                    {"name": "registeredAt", "type": "uint256", "internalType": "uint256"},
                    {"name": "active", "type": "bool", "internalType": "bool"},
                ],
            },
        ],
    },
    {
        "type": "function",
        "name": "getSigningNonce",
        "stateMutability": "view",
        "inputs": [{"name": "agentId", "type": "uint256", "internalType": "uint256"}],
        "outputs": [{"name": "", "type": "uint256", "internalType": "uint256"}],
    },
    {
        "type": "event",
        "name": "AgentRegistered",
        "anonymous": False,
        "inputs": [
            {"name": "agentId", "type": "uint256", "indexed": True, "internalType": "uint256"},
            {"name": "operatorWallet", "type": "address", "indexed": True, "internalType": "address"},
            {"name": "agentWallet", "type": "address", "indexed": True, "internalType": "address"},
        ],
    },
]

HACKATHON_VAULT_ABI: list[dict] = [
    {
        "type": "function",
        "name": "claimAllocation",
        "stateMutability": "nonpayable",
        "inputs": [{"name": "agentId", "type": "uint256", "internalType": "uint256"}],
        "outputs": [],
    },
    {
        "type": "function",
        "name": "getBalance",
        "stateMutability": "view",
        "inputs": [{"name": "agentId", "type": "uint256", "internalType": "uint256"}],
        "outputs": [{"name": "", "type": "uint256", "internalType": "uint256"}],
    },
    {
        "type": "function",
        "name": "hasClaimed",
        "stateMutability": "view",
        "inputs": [{"name": "agentId", "type": "uint256", "internalType": "uint256"}],
        "outputs": [{"name": "", "type": "bool", "internalType": "bool"}],
    },
    {
        "type": "function",
        "name": "allocationPerTeam",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256", "internalType": "uint256"}],
    },
]

# TradeIntent tuple components — shared by submitTradeIntent and simulateIntent
_TRADE_INTENT_COMPONENTS: list[dict] = [
    {"name": "agentId", "type": "uint256", "internalType": "uint256"},
    {"name": "agentWallet", "type": "address", "internalType": "address"},
    {"name": "pair", "type": "string", "internalType": "string"},
    {"name": "action", "type": "string", "internalType": "string"},
    {"name": "amountUsdScaled", "type": "uint256", "internalType": "uint256"},
    {"name": "maxSlippageBps", "type": "uint256", "internalType": "uint256"},
    {"name": "nonce", "type": "uint256", "internalType": "uint256"},
    {"name": "deadline", "type": "uint256", "internalType": "uint256"},
]

RISK_ROUTER_ABI: list[dict] = [
    {
        "type": "function",
        "name": "submitTradeIntent",
        "stateMutability": "nonpayable",
        "inputs": [
            {
                "name": "intent",
                "type": "tuple",
                "internalType": "struct RiskRouter.TradeIntent",
                "components": _TRADE_INTENT_COMPONENTS,
            },
            {"name": "signature", "type": "bytes", "internalType": "bytes"},
        ],
        "outputs": [],
    },
    {
        "type": "function",
        "name": "simulateIntent",
        "stateMutability": "view",
        "inputs": [
            {
                "name": "intent",
                "type": "tuple",
                "internalType": "struct RiskRouter.TradeIntent",
                "components": _TRADE_INTENT_COMPONENTS,
            },
        ],
        "outputs": [
            {"name": "valid", "type": "bool", "internalType": "bool"},
            {"name": "reason", "type": "string", "internalType": "string"},
        ],
    },
    {
        "type": "function",
        "name": "getIntentNonce",
        "stateMutability": "view",
        "inputs": [{"name": "agentId", "type": "uint256", "internalType": "uint256"}],
        "outputs": [{"name": "", "type": "uint256", "internalType": "uint256"}],
    },
    {
        "type": "event",
        "name": "TradeApproved",
        "anonymous": False,
        "inputs": [
            {"name": "agentId", "type": "uint256", "indexed": True, "internalType": "uint256"},
            {"name": "intentHash", "type": "bytes32", "indexed": False, "internalType": "bytes32"},
            {"name": "amountUsdScaled", "type": "uint256", "indexed": False, "internalType": "uint256"},
        ],
    },
    {
        "type": "event",
        "name": "TradeRejected",
        "anonymous": False,
        "inputs": [
            {"name": "agentId", "type": "uint256", "indexed": True, "internalType": "uint256"},
            {"name": "intentHash", "type": "bytes32", "indexed": False, "internalType": "bytes32"},
            {"name": "reason", "type": "string", "indexed": False, "internalType": "string"},
        ],
    },
]

VALIDATION_REGISTRY_ABI: list[dict] = [
    {
        "type": "function",
        "name": "postEIP712Attestation",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "agentId", "type": "uint256", "internalType": "uint256"},
            {"name": "checkpointHash", "type": "bytes32", "internalType": "bytes32"},
            {"name": "score", "type": "uint8", "internalType": "uint8"},
            {"name": "notes", "type": "string", "internalType": "string"},
        ],
        "outputs": [],
    },
    {
        "type": "function",
        "name": "getAverageValidationScore",
        "stateMutability": "view",
        "inputs": [{"name": "agentId", "type": "uint256", "internalType": "uint256"}],
        "outputs": [{"name": "", "type": "uint256", "internalType": "uint256"}],
    },
]

REPUTATION_REGISTRY_ABI: list[dict] = [
    {
        "type": "function",
        "name": "submitFeedback",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "agentId", "type": "uint256", "internalType": "uint256"},
            {"name": "score", "type": "uint8", "internalType": "uint8"},
            {"name": "outcomeRef", "type": "bytes32", "internalType": "bytes32"},
            {"name": "comment", "type": "string", "internalType": "string"},
            {"name": "feedbackType", "type": "uint8", "internalType": "uint8"},
        ],
        "outputs": [],
    },
    {
        "type": "function",
        "name": "getAverageScore",
        "stateMutability": "view",
        "inputs": [{"name": "agentId", "type": "uint256", "internalType": "uint256"}],
        "outputs": [{"name": "", "type": "uint256", "internalType": "uint256"}],
    },
]


class ContractManager:
    """Singleton factory for Sepolia contract instances and Web3 provider."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.w3 = Web3(Web3.HTTPProvider(settings.rpc_url)) if settings.rpc_url else None
        self.connected = bool(self.w3 and self.w3.is_connected())

        # Operator wallet (owns ERC-721, pays gas)
        self.operator_account = Account.from_key(settings.wallet_private_key) if settings.wallet_private_key else None
        # Agent wallet (signs trade intents + checkpoints)
        self.agent_account = Account.from_key(settings.agent_wallet_private_key) if settings.agent_wallet_private_key else None

        if self.connected:
            logger.info(f"Web3 connected to Sepolia (chainId={self.w3.eth.chain_id})")
        else:
            logger.warning("Web3 NOT connected — blockchain features will use dry-run mode")

    @property
    def operator_address(self) -> str:
        return self.operator_account.address if self.operator_account else "0x" + "0" * 40

    @property
    def agent_address(self) -> str:
        return self.agent_account.address if self.agent_account else "0x" + "0" * 40

    def _get_contract(self, address: str, abi: list[dict]) -> Contract | None:
        if not self.connected:
            return None
        return self.w3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=abi,
        )

    @property
    def agent_registry(self) -> Contract | None:
        return self._get_contract(self.settings.agent_registry_address, AGENT_REGISTRY_ABI)

    @property
    def hackathon_vault(self) -> Contract | None:
        return self._get_contract(self.settings.hackathon_vault_address, HACKATHON_VAULT_ABI)

    @property
    def risk_router(self) -> Contract | None:
        return self._get_contract(self.settings.risk_router_address, RISK_ROUTER_ABI)

    @property
    def validation_registry(self) -> Contract | None:
        return self._get_contract(self.settings.validation_registry_address, VALIDATION_REGISTRY_ABI)

    @property
    def reputation_registry(self) -> Contract | None:
        return self._get_contract(self.settings.reputation_registry_address, REPUTATION_REGISTRY_ABI)

    def send_tx(self, tx_data: dict[str, Any], private_key: str) -> str | None:
        """Build, sign, send a transaction with retry and gas buffer."""
        if not self.connected:
            logger.warning("Dry-run mode — tx not sent")
            return None

        for attempt in range(self.settings.max_retries):
            try:
                tx_data["nonce"] = self.w3.eth.get_transaction_count(
                    Account.from_key(private_key).address
                )
                if "gas" not in tx_data:
                    estimated = self.w3.eth.estimate_gas(tx_data)
                    tx_data["gas"] = int(estimated * self.settings.gas_buffer_multiplier)

                signed = self.w3.eth.account.sign_transaction(tx_data, private_key=private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
                logger.info(f"TX confirmed: {tx_hash.hex()} (gas={receipt['gasUsed']})")
                return tx_hash.hex()
            except Exception as e:
                logger.error(f"TX attempt {attempt+1}/{self.settings.max_retries} failed: {e}")
                if attempt == self.settings.max_retries - 1:
                    raise
        return None
