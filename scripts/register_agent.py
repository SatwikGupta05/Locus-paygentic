#!/usr/bin/env python3
"""
AURORA-AI Agent Registration and Initialization Script

This script handles:
1. Agent wallet validation
2. On-chain agent identity registration (ERC-8004)
3. Sandbox capital claiming from HackathonVault
4. Metadata generation for agent discovery
"""
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

import argparse
import json
import logging
from typing import Any

from backend.blockchain.agent_registry import AgentRegistrar
from backend.blockchain.contracts import ContractManager
from backend.utils.config import get_settings, ROOT_DIR
from backend.utils.logger import create_logger

logger = logging.getLogger(__name__)


def generate_agent_metadata() -> dict[str, Any]:
    """Generate metadata.json for AURORA agent."""
    return {
        "name": "AURORA-AI Trading Agent",
        "version": "1.0.0",
        "description": "Autonomous AI trading agent with ERC-8004 trustless validation",
        "capabilities": [
            "autonomous_trading",
            "risk_management",
            "ml_predictions",
            "eip712_signing",
            "validation_checkpoints",
            "reputation_building",
        ],
        "features": {
            "data_sources": ["Kraken", "CCXT", "PRISM"],
            "strategies": ["ml_prediction", "technical_analysis", "sentiment_analysis"],
            "risk_controls": ["drawdown_limits", "position_sizing", "circuit_breaker"],
            "blockchain": "ERC-8004 compliant",
        },
        "endpoints": {
            "health": "http://localhost:8000/health",
            "config": "http://localhost:8000/config",
            "metrics": "http://localhost:8000/metrics",
        },
    }


def run_registration(
    settings_override: dict[str, str] | None = None,
    auto_claim: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Execute agent registration flow.
    
    Returns:
        Registration result with agent_id, status, and transaction hashes
    """
    settings = get_settings()
    if settings_override:
        for key, value in settings_override.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

    logger.info("=" * 80)
    logger.info("AURORA-AI AGENT REGISTRATION")
    logger.info("=" * 80)

    # ─── Step 1: Validate wallet credentials ───────────────────────────────
    logger.info("\n[1/4] Validating wallet credentials...")
    if not settings.wallet_private_key:
        logger.error("❌ WALLET_PRIVATE_KEY not configured")
        return {"status": "error", "message": "Missing WALLET_PRIVATE_KEY"}
    if not settings.agent_wallet_private_key:
        logger.error("❌ AGENT_WALLET_PRIVATE_KEY not configured")
        return {"status": "error", "message": "Missing AGENT_WALLET_PRIVATE_KEY"}

    cm = ContractManager(settings)
    if not cm.connected:
        logger.warning("⚠️  Web3 not connected — dry-run mode only")
        return {
            "status": "dry_run",
            "message": "Web3 connection failed — check SEPOLIA_RPC_URL",
            "operator": cm.operator_address,
            "agent": cm.agent_address,
        }

    logger.info(f"✅ Operator wallet: {cm.operator_address}")
    logger.info(f"✅ Agent wallet: {cm.agent_address}")

    # ─── Step 2: Register agent identity ──────────────────────────────────
    logger.info("\n[2/4] Registering agent identity on ERC-8004 (AgentRegistry)...")
    registrar = AgentRegistrar(cm)

    if registrar.is_registered():
        logger.info(f"✅ Agent already registered with ID: {settings.agent_id}")
        agent_info = registrar.get_agent_info()
        if agent_info:
            logger.info(f"   Details: {json.dumps(agent_info, indent=2)}")
    else:
        logger.info("⏳ Submitting registration transaction...")
        if dry_run:
            logger.info("🔹 DRY-RUN: Skipping transaction")
        else:
            reg_result = registrar.register()
            logger.info(f"📋 Registration result: {json.dumps(reg_result, indent=2)}")

    # ─── Step 3: Claim sandbox capital ────────────────────────────────────
    logger.info("\n[3/4] Claiming sandbox capital from HackathonVault...")
    if not auto_claim:
        logger.info("⏭️  Skipping vault claim (--no-claim flag set)")
    else:
        logger.info("⏳ Submitting claim transaction...")
        if dry_run:
            logger.info("🔹 DRY-RUN: Skipping transaction")
        else:
            claim_result = registrar.claim_allocation()
            logger.info(f"💰 Claim result: {json.dumps(claim_result, indent=2)}")

    # ─── Step 4: Generate and save metadata ───────────────────────────────
    logger.info("\n[4/4] Generating agent metadata...")
    metadata = generate_agent_metadata()
    metadata_path = ROOT_DIR / "agent-metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))
    logger.info(f"✅ Metadata saved to: {metadata_path}")
    logger.info(f"📋 Metadata:\n{json.dumps(metadata, indent=2)}")

    logger.info("\n" + "=" * 80)
    logger.info("✨ AURORA-AI Agent Ready for Trading!")
    logger.info("=" * 80)
    logger.info(f"Agent ID: {settings.agent_id}")
    logger.info(f"Agent Wallet: {cm.agent_address}")
    logger.info(f"Operator: {cm.operator_address}")
    logger.info(f"Network: Sepolia (ChainID: {settings.chain_id})")
    logger.info(f"RPC: {settings.rpc_url}")
    logger.info("\nNext: Start the trading service with: python -m backend.main")
    logger.info("=" * 80 + "\n")

    return {
        "status": "success",
        "agent_id": settings.agent_id,
        "operator": cm.operator_address,
        "agent": cm.agent_address,
        "metadata": metadata,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Register AURORA-AI agent on ERC-8004 and claim sandbox capital"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate registration without sending transactions",
    )
    parser.add_argument(
        "--no-claim",
        action="store_true",
        help="Skip vault capital claiming",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    # Setup logging
    log_path = ROOT_DIR / "logs" / "registration.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger_instance = create_logger(str(log_path), level=getattr(logging, args.log_level))

    try:
        result = run_registration(
            auto_claim=not args.no_claim,
            dry_run=args.dry_run,
        )
        if result.get("status") == "error":
            sys.exit(1)
    except Exception as e:
        logger_instance.exception("Registration failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
