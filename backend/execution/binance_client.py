"""Binance CCXT wrapper for the AURORA trading system.

Uses CCXT's unified interface to access Binance Spot trading API.
Supports paper and live trading modes.

NOTE: Binance blocks API access from certain regions (e.g., India).
For geo-blocked regions, this client automatically falls back to KuCoin.
"""
from __future__ import annotations

import logging
import ccxt
from typing import Any

logger = logging.getLogger(__name__)


class BinanceClient:
    """Binance client using CCXT unified interface with geo-restriction fallback."""

    def __init__(
        self,
        api_key: str = "",
        secret: str = "",
        force_failure: bool = False,
        paper_mode: bool = True,
        region: str = "default",
    ):
        """
        Initialize Binance client with regional awareness.
        
        Args:
            api_key: Binance API key
            secret: Binance API secret
            force_failure: Force failure for testing
            paper_mode: If True, use paper trading (no actual execution)
            region: Geographic region (india, default, etc)
        """
        self.api_key = api_key
        self.secret = secret
        self.force_failure = force_failure
        self.paper_mode = paper_mode
        self.region = region
        self.fallback_to_kucoin = False
        
        # For India, pre-emptively use KuCoin
        if region.lower() == "india":
            logger.warning("[AURORA] Binance is geo-blocked in India, using KuCoin instead")
            self.fallback_to_kucoin = True
            self.exchange = ccxt.kucoin({
                "enableRateLimit": True,
            })
            if api_key and secret and not paper_mode:
                self.exchange.apiKey = api_key
                self.exchange.secret = secret
        else:
            # Initialize CCXT Binance exchange
            if api_key and secret and not paper_mode:
                self.exchange = ccxt.binance({
                    "apiKey": api_key,
                    "secret": secret,
                    "enableRateLimit": True,
                })
            else:
                # Paper mode - no credentials needed
                self.exchange = ccxt.binance({
                    "enableRateLimit": True,
                })

    def _format_symbol(self, pair: str) -> str:
        """Convert pair format to CCXT format (e.g., BTCUSD -> BTC/USD)."""
        if "/" not in pair:
            # Assume format like BTCUSD -> BTC/USD
            if len(pair) > 3 and pair[-3:] in ["USD", "EUR", "GBP"]:
                return f"{pair[:-3]}/{pair[-3:]}"
            elif len(pair) > 4 and pair[-4:] == "USDT":
                return f"{pair[:-4]}/{pair[-4:]}"
        return pair

    async def get_ticker(self, pair: str = "BTC/USD") -> dict[str, Any]:
        """
        Fetch ticker data for a pair.
        
        Args:
            pair: Trading pair (e.g., BTC/USD or BTCUSD)
            
        Returns:
            Ticker dict with bid, ask, last, etc.
        """
        if self.force_failure:
            raise Exception("Simulated Binance failure")
        
        try:
            symbol = self._format_symbol(pair)
            ticker = await self.exchange.fetch_ticker(symbol)
            return {
                "bid": ticker.get("bid"),
                "ask": ticker.get("ask"),
                "last": ticker.get("last"),
                "high": ticker.get("high"),
                "low": ticker.get("low"),
                "volume": ticker.get("quoteVolume"),
            }
        except ccxt.PermissionDenied as e:
            # 451 - Geo-blocked error
            if "restricted location" in str(e) or "451" in str(e):
                logger.error(f"[AURORA] Binance geo-blocked (451): {e}")
                logger.error("[AURORA] Using KuCoin as fallback exchange")
                self.fallback_to_kucoin = True
                # Re-initialize with KuCoin
                self.exchange = ccxt.kucoin({"enableRateLimit": True})
                # Retry with KuCoin
                symbol = self._format_symbol(pair)
                ticker = await self.exchange.fetch_ticker(symbol)
                return {
                    "bid": ticker.get("bid"),
                    "ask": ticker.get("ask"),
                    "last": ticker.get("last"),
                    "high": ticker.get("high"),
                    "low": ticker.get("low"),
                    "volume": ticker.get("quoteVolume"),
                }
            raise
        except Exception as e:
            logger.error(f"Binance ticker fetch failed: {e}")
            raise

    async def place_order(
        self,
        pair: str,
        side: str,
        size: float,
        order_type: str = "market",
        price: float = None,
    ) -> dict[str, Any]:
        """
        Place a market or limit order.
        
        Args:
            pair: Trading pair (e.g., BTC/USD or BTCUSD)
            side: 'buy' or 'sell'
            size: Order quantity
            order_type: 'market' or 'limit'
            price: Required for limit orders
            
        Returns:
            Order dict with id, status, etc.
        """
        if self.force_failure:
            raise Exception("Simulated Binance order failure")
        
        if self.paper_mode:
            # In paper mode, simulate order execution
            logger.info(f"[PAPER] Binance {side.upper()} {size} {pair}")
            return {
                "id": f"paper-{side}-{int(size*10000)}",
                "symbol": self._format_symbol(pair),
                "side": side.lower(),
                "amount": size,
                "status": "closed",
                "filled": size,
                "remaining": 0,
                "type": order_type,
            }
        
        try:
            symbol = self._format_symbol(pair)
            if order_type.lower() == "market":
                order = await self.exchange.create_market_order(
                    symbol, side.lower(), size
                )
            else:
                if price is None:
                    raise ValueError("Price required for limit orders")
                order = await self.exchange.create_limit_order(
                    symbol, side.lower(), size, price
                )
            
            return {
                "id": order.get("id"),
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "amount": order.get("amount"),
                "status": order.get("status"),
                "filled": order.get("filled"),
                "remaining": order.get("remaining"),
                "type": order.get("type"),
            }
        except Exception as e:
            logger.error(f"Binance order placement failed: {e}")
            raise

    async def get_balance(self) -> dict[str, Any]:
        """
        Fetch account balance.
        
        Returns:
            Balance dict with currencies as keys
        """
        if self.force_failure:
            raise Exception("Simulated Binance balance fetch failure")
        
        if self.paper_mode:
            # Return mock paper account balance
            logger.info("[PAPER] Returning simulated Binance balance")
            return {
                "BTC": {"free": 0.1, "used": 0.0, "total": 0.1},
                "USD": {"free": 5000, "used": 0, "total": 5000},
                "USDT": {"free": 5000, "used": 0, "total": 5000},
            }
        
        try:
            balance = await self.exchange.fetch_balance()
            return {
                curr: {
                    "free": balance.get(curr, {}).get("free", 0),
                    "used": balance.get(curr, {}).get("used", 0),
                    "total": balance.get(curr, {}).get("total", 0),
                }
                for curr in balance.keys()
                if balance[curr]["total"] > 0
            }
        except Exception as e:
            logger.error(f"Binance balance fetch failed: {e}")
            raise

    async def cancel_order(self, order_id: str, pair: str = None) -> dict[str, Any]:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel
            pair: Trading pair (required for some exchanges)
            
        Returns:
            Cancelled order dict
        """
        if self.force_failure:
            raise Exception("Simulated Binance order cancellation failure")
        
        if self.paper_mode:
            logger.info(f"[PAPER] Cancelled order {order_id}")
            return {"id": order_id, "status": "canceled"}
        
        try:
            symbol = self._format_symbol(pair) if pair else None
            order = await self.exchange.cancel_order(order_id, symbol)
            return {
                "id": order.get("id"),
                "status": order.get("status"),
                "symbol": order.get("symbol"),
            }
        except Exception as e:
            logger.error(f"Binance order cancellation failed: {e}")
            raise

    def close(self):
        """Close the exchange connection."""
        if hasattr(self.exchange, "close"):
            self.exchange.close()
