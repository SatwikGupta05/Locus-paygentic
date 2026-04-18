"""PRISM API client (Strykr) with graceful fallback to existing data sources."""
from __future__ import annotations

import logging
import time
from typing import Any

import httpx

logger = logging.getLogger("aurora")


class PrismClient:
    """Fetches real-time market data, signals, and risk from the PRISM API.

    If PRISM is unavailable, returns None so callers can fallback to
    existing data sources (CCXT, synthetic, etc.).
    """

    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {"X-API-Key": api_key} if api_key else {}
        self._available = bool(api_key)
        self._unavailable_logged = False  # Track if we've logged unavailability

    async def _get(self, path: str, max_retries: int = 2) -> dict[str, Any] | None:
        """Make a GET request to PRISM API with retry and error handling."""
        if not self._available:
            return None
        
        url = f"{self.base_url}{path}"
        last_error = None
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(url, headers=self.headers)
                    
                    # Handle different status codes
                    if resp.status_code == 404:
                        # 404 means endpoint doesn't exist - don't retry
                        if not self._unavailable_logged:
                            logger.info(f"PRISM API endpoint not available ({path})")
                            self._unavailable_logged = True
                        return None
                    
                    resp.raise_for_status()
                    return resp.json()
                    
            except (httpx.TimeoutException, httpx.ReadError, httpx.ConnectError) as e:
                # Transient network errors - retry with backoff
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s
                    logger.debug(f"PRISM API transient error ({path}), retrying in {wait_time}s: {type(e).__name__}")
                    time.sleep(wait_time)
            except httpx.HTTPStatusError as e:
                # HTTP errors like 500, 503 might be transient
                if e.response.status_code >= 500:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.debug(f"PRISM API server error {e.response.status_code} ({path}), retrying in {wait_time}s")
                        time.sleep(wait_time)
                    else:
                        logger.warning(f"PRISM API server error {e.response.status_code} ({path}) after retries")
                        return None
                else:
                    logger.debug(f"PRISM API error {e.response.status_code} ({path})")
                    return None
            except Exception as e:
                logger.debug(f"PRISM API error ({path}): {type(e).__name__}: {e}")
                return None
        
        if last_error:
            logger.warning(f"PRISM API failed after {max_retries} attempts ({path}): {last_error}")
        return None

    async def resolve(self, asset: str) -> dict[str, Any] | None:
        """Resolve asset metadata via /resolve/{asset}."""
        return await self._get(f"/resolve/{asset}")

    async def get_price(self, symbol: str) -> dict[str, Any] | None:
        """Get real-time price via /resolve/{symbol}.
        
        Args:
            symbol (str): Trading pair symbol (e.g. BTC/USD)
        """
        # PRISM expects the base asset, e.g. BTC instead of BTC/USD
        base_symbol = symbol.split('/')[0] if '/' in symbol else symbol
        
        data = await self._get(f"/resolve/{base_symbol}")
        if data:
            price = data.get("price") or data.get("data", {}).get("price")
            if price is not None:
                logger.info(f"[AURORA] PRISM {base_symbol} price: {price}")
                return {
                    "symbol": symbol,
                    "price": price,
                    "source": "PRISM"
                }
        return None

    async def get_signals(self, symbol: str) -> dict[str, Any] | None:
        """Get trading signals via /signals/{symbol}."""
        base_symbol = symbol.split('/')[0] if '/' in symbol else symbol
        return await self._get(f"/signals/{base_symbol}")

    async def get_risk(self, symbol: str) -> dict[str, Any] | None:
        """Get risk metrics via /risk/{symbol}."""
        base_symbol = symbol.split('/')[0] if '/' in symbol else symbol
        return await self._get(f"/risk/{base_symbol}")

    async def get_market_intelligence(self, symbol: str) -> dict[str, Any]:
        """Aggregate all PRISM endpoints into a single intelligence payload.

        Returns a dict with available data — callers check for None fields
        and fallback accordingly.
        """
        price_data = await self.get_price(symbol)
        signals_data = await self.get_signals(symbol)
        risk_data = await self.get_risk(symbol)

        return {
            "source": "PRISM" if any([price_data, signals_data, risk_data]) else "unavailable",
            "timestamp": int(time.time()),
            "price": price_data,
            "signals": signals_data,
            "risk": risk_data,
        }
