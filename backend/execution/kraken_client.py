"""Kraken CLI wrapper using the CORRECT hackathon CLI syntax.

VALID commands:
  kraken -o json ticker BTCUSD
  kraken order buy BTCUSD 0.001 --type market
  kraken paper buy BTCUSD 0.001
  kraken mcp -s all --allow-dangerous

DO NOT USE: --sandbox, --json, order add, order create --pair
"""
from __future__ import annotations

import json
import logging
import subprocess
import time
from typing import Any

logger = logging.getLogger(__name__)


class KrakenClient:
    """Production Kraken CLI wrapper with hackathon-correct command syntax."""

    def __init__(
        self,
        binary: str = "kraken",
        api_key: str = "",
        secret: str = "",
        force_failure: bool = False,
        paper_mode: bool = True,
    ):
        self.binary = binary
        self.api_key = api_key
        self.secret = secret
        self.force_failure = force_failure
        self.paper_mode = paper_mode

    def _run(self, args: list[str]) -> tuple[dict[str, Any], list[str], float]:
        """Execute CLI command. Returns (parsed_json, full_command, latency_ms)."""
        if self.force_failure:
            raise Exception("Simulated Kraken CLI failure")

        command = [self.binary] + args
        logger.info(f"KRAKEN CLI → {' '.join(command)}")

        start = time.perf_counter()
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=10.0,
            )
        except subprocess.TimeoutExpired:
            raise Exception(f"Kraken CLI timed out: {' '.join(command)}")
        except FileNotFoundError:
            raise Exception(f"Kraken CLI binary not found: '{self.binary}'")

        latency = (time.perf_counter() - start) * 1000

        if result.returncode != 0:
            logger.error(f"Kraken CLI stderr: {result.stderr}")
            raise Exception(f"Kraken CLI failed: {result.stderr}")

        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError:
            parsed = {"raw_output": result.stdout.strip()}

        return parsed, command, latency

    # ─── Correct CLI methods ──────────────────────────────────────────────────

    def get_ticker(self, pair: str = "BTCUSD") -> tuple[dict[str, Any], list[str], float]:
        """kraken -o json ticker BTCUSD"""
        return self._run(["-o", "json", "ticker", pair])

    def place_order(
        self,
        pair: str,
        side: str,
        size: float,
        order_type: str = "market",
    ) -> tuple[dict[str, Any], list[str], float]:
        """
        Paper: kraken paper buy BTCUSD 0.001
        Live:  kraken order buy BTCUSD 0.001 --type market
        """
        side_lower = side.lower()
        if self.paper_mode:
            return self._run(["paper", side_lower, pair, str(size)])
        else:
            args = ["order", side_lower, pair, str(size)]
            if order_type:
                args.extend(["--type", order_type])
            return self._run(args)

    def get_balance(self) -> tuple[dict[str, Any], list[str], float]:
        """kraken -o json balance"""
        return self._run(["-o", "json", "balance"])

    def cancel_order(self, order_id: str) -> tuple[dict[str, Any], list[str], float]:
        """kraken order cancel <order_id>"""
        return self._run(["order", "cancel", order_id])
