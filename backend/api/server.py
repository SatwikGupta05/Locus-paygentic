from __future__ import annotations

import asyncio
import traceback
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.database.db_manager import DBManager
from backend.services.event_bus_v2 import EventBusV2
from backend.services.runtime_state import RuntimeState
from backend.services.trading_service import TradingService
from backend.utils.config import MIGRATIONS_DIR, get_settings
from backend.utils.logger import create_logger, log_event


def create_app() -> FastAPI:
    settings = get_settings()
    logger = create_logger(settings.log_path)
    db = DBManager(settings.db_path, MIGRATIONS_DIR)
    runtime_state = RuntimeState()
    event_bus = EventBusV2()
    trading_service = TradingService(settings, db, logger, runtime_state, event_bus)

    async def _service_loop() -> None:
        while True:
            try:
                await trading_service.process_cycle()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                tb = traceback.format_exc()
                log_event(logger, "WORKER", "Trading cycle failed", error=str(exc))
                logger.error(f"[AURORA ERROR] Trading cycle exception:\n{tb}")
            await asyncio.sleep(settings.worker_interval_seconds)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        loop_task: asyncio.Task | None = None
        await trading_service.initialize()
        await runtime_state.update("worker", {"status": "running" if settings.auto_start_worker else "idle"})
        if settings.auto_start_worker:
            loop_task = asyncio.create_task(_service_loop())
        yield
        if loop_task is not None:
            loop_task.cancel()
            await asyncio.gather(loop_task, return_exceptions=True)
        await runtime_state.update("worker", {"status": "stopped"})

    app = FastAPI(title="AURORA AI Trading Agents", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.settings = settings
    app.state.db = db
    app.state.runtime_state = runtime_state
    app.state.service = trading_service
    app.state.worker = None
    app.state.event_bus = event_bus

    # ─── REST Endpoints ──────────────────────────────────────────────────

    @app.get("/health")
    async def get_health() -> dict:
        worker_state = await runtime_state.get("worker", {})
        return {
            "status": "healthy",
            "mode": settings.env,
            "data_mode": settings.data_mode,
            "symbol": settings.symbol,
            "worker": worker_state,
            "agent_name": settings.agent_name,
        }

    @app.get("/config")
    async def get_config() -> dict:
        """Non-sensitive configuration for frontend display."""
        return {
            "env": settings.env,
            "data_mode": settings.data_mode,
            "symbol": settings.symbol,
            "timeframe": settings.timeframe,
            "starting_balance": settings.starting_balance,
            "max_capital_per_trade": settings.max_capital_per_trade,
            "max_open_positions": settings.max_open_positions,
            "stop_loss_pct": settings.stop_loss_pct,
            "take_profit_pct": settings.take_profit_pct,
            "max_drawdown_pct": settings.max_drawdown_pct,
            "max_daily_loss_pct": settings.max_daily_loss_pct,
            "risk_fraction": settings.risk_fraction,
            "max_consecutive_losses": settings.max_consecutive_losses,
            "min_confidence": settings.min_confidence,
            "agent_name": settings.agent_name,
            "agent_personality": "Short-horizon volatility-aware autonomous trader with cryptographic intent verification",
        }

    @app.get("/status")
    async def get_status() -> dict:
        return trading_service.get_status()

    @app.get("/market")
    async def get_market() -> dict:
        return await runtime_state.get("market", {})

    @app.get("/decision")
    async def get_decision() -> dict:
        return await runtime_state.get("decision", {})

    @app.get("/trades")
    async def get_trades() -> dict:
        return {"items": trading_service.get_recent_trades()}

    @app.get("/metrics")
    async def get_metrics() -> dict:
        return await runtime_state.get("metrics", {})

    @app.get("/intents")
    async def get_intents() -> dict:
        return {"items": trading_service.get_recent_intents()}

    @app.get("/orders")
    async def get_orders() -> dict:
        return {"items": trading_service.get_recent_orders()}

    @app.get("/reputation")
    async def get_reputation() -> dict:
        return trading_service.get_reputation()

    @app.get("/agent")
    async def get_agent() -> dict:
        try:
            return trading_service.get_agent_details()
        except Exception as exc:
            logger.error(f"[AURORA] /agent endpoint failed: {exc}")
            return {
                "agent_id": settings.agent_id,
                "agent_name": settings.agent_name,
                "agent_wallet": trading_service.contract_manager.agent_address,
                "operator_wallet": trading_service.contract_manager.operator_address,
                "identity_registry": settings.agent_registry_address,
                "risk_router": settings.risk_router_address,
                "validation_registry": settings.validation_registry_address,
                "reputation_registry": settings.reputation_registry_address,
                "capital_claimed": False,
                "allocation": "0.05",
                "reputation": {},
                "validation_txs": [],
                "error": str(exc),
            }

    @app.get("/strategy")
    async def get_strategy() -> dict:
        payload = trading_service.get_strategy_summary()
        pipeline = await runtime_state.get("pipeline_stage", {"stage": "IDLE"})
        payload["current_stage"] = pipeline.get("stage", payload.get("current_stage", "IDLE"))
        return payload

    @app.get("/audit-trail")
    async def get_audit_trail() -> dict:
        return {"items": trading_service.get_audit_trail()}

    @app.get("/pipeline")
    async def get_pipeline_stage() -> dict:
        return await runtime_state.get("pipeline_stage", {"stage": "IDLE"})

    @app.post("/execute-manual-trade")
    async def execute_manual_trade(request: dict = Body(...)) -> dict:
        """Execute a manual BUY/SELL trade with specified amount and optional price."""
        try:
            side = request.get("side", "BUY").upper()
            amount = float(request.get("amount", 0))
            price = request.get("price")
            symbol = request.get("symbol", settings.symbol)

            # Validate inputs
            if side not in ["BUY", "SELL"]:
                return {
                    "success": False,
                    "message": "Invalid side. Must be 'BUY' or 'SELL'.",
                    "executed": False,
                }

            if amount <= 0:
                return {
                    "success": False,
                    "message": "Amount must be greater than 0.",
                    "executed": False,
                }

            # Execute the trade
            result = await trading_service.execute_manual_trade(
                side=side, amount=amount, price=price, symbol=symbol
            )

            logger.info(
                f"[MANUAL TRADE] {side} {amount} {symbol} @ ${price or 'market'} - Result: {result}"
            )

            return {
                "success": result.get("success", False),
                "message": result.get("message", "Trade execution completed"),
                "executed": result.get("executed", False),
                "trade": result.get("trade"),
                "order_id": result.get("order_id"),
            }

        except Exception as exc:
            logger.error(f"[MANUAL TRADE ERROR] {exc}", exc_info=True)
            return {
                "success": False,
                "message": f"Trade execution failed: {str(exc)}",
                "executed": False,
                "error": str(exc),
            }

    # ─── WebSocket Endpoints ─────────────────────────────────────────────

    async def _ws_handler(channel: str, websocket: WebSocket) -> None:
        await event_bus.subscribe_ws(channel, websocket)
        try:
            while True:
                await asyncio.sleep(3600)
        except WebSocketDisconnect:
            await event_bus.unsubscribe_ws(channel, websocket)

    @app.websocket("/ws/market")
    async def market_socket(websocket: WebSocket) -> None:
        await _ws_handler("market", websocket)

    @app.websocket("/ws/trades")
    async def trades_socket(websocket: WebSocket) -> None:
        await _ws_handler("trades", websocket)

    @app.websocket("/ws/decisions")
    async def decisions_socket(websocket: WebSocket) -> None:
        await _ws_handler("decisions", websocket)

    @app.websocket("/ws/pipeline")
    async def pipeline_socket(websocket: WebSocket) -> None:
        """Unified pipeline feed — streams ALL event types (stages, intents, orders, etc.)."""
        await _ws_handler("pipeline", websocket)

    @app.websocket("/ws/orders")
    async def orders_socket(websocket: WebSocket) -> None:
        """Order lifecycle state transitions."""
        await _ws_handler("orders", websocket)

    return app
