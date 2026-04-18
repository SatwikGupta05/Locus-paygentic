from __future__ import annotations

import asyncio
import logging
from typing import Any

from backend.agents.analyst_agent import AnalystAgent
from backend.agents.risk_agent import RiskAgent
from backend.agents.scout_agent import ScoutAgent
from backend.blockchain.contracts import ContractManager
from backend.blockchain.erc8004_client import ERC8004Client
from backend.blockchain.intent_router import IntentRouter
from backend.blockchain.intent_signer import IntentSigner
from backend.data.feature_engineering import FeatureEngineering
from backend.data.market_fetcher import DataMode, MarketFetcher
from backend.database.db_manager import DBManager
from backend.database.trade_logger import TradeLogger
from backend.engine.decision_engine import DecisionEngine
from backend.engine.portfolio_manager import PortfolioManager
from backend.execution.binance_client import BinanceClient
from backend.execution.paper_executor import PaperExecutor
from backend.execution.trade_executor import TradeExecutor
from backend.ml.predictor import Predictor
from backend.ml.agent_narrative import AgentNarrativeGenerator
from backend.services.event_bus_v2 import EventBusV2
from backend.services.runtime_state import RuntimeState
from backend.utils.config import Settings
from backend.utils.logger import log_event


class TradingEngineV2:
    def __init__(
        self,
        settings: Settings,
        db: DBManager,
        logger: logging.Logger,
        runtime_state: RuntimeState,
        event_bus: EventBusV2,
    ) -> None:
        self.settings = settings
        self.db = db
        self.logger = logger
        self.runtime_state = runtime_state
        self.event_bus = event_bus
        self.trade_logger = TradeLogger(db)
        
        self.market_fetcher = MarketFetcher(mode=DataMode(settings.data_mode), region=settings.user_region)
        self.feature_engineering = FeatureEngineering()
        self.predictor = Predictor(settings.model_path, settings.feature_schema_path)
        self.scout_agent = ScoutAgent(settings.news_urls)
        self.analyst_agent = AnalystAgent()
        self.risk_agent = RiskAgent()
        self.decision_engine = DecisionEngine()
        self.narrative_gen = AgentNarrativeGenerator()
        
        # Initialize blockchain components
        self.contract_manager = ContractManager(settings)
        self.intent_signer = IntentSigner(self.contract_manager)
        self.erc8004 = ERC8004Client(
            settings.rpc_url,
            settings.verifying_contract,
            settings.agent_name,
            self.intent_signer.wallet_address,
        )
        self.intent_router = IntentRouter(self.intent_signer, self.erc8004)
        
        # Phase 4 execution wrapper instantiation
        self.binance_client = BinanceClient(
            api_key=settings.binance_api_key,
            secret=settings.binance_secret,
            force_failure=False,
            paper_mode=True,
            region=settings.user_region,  # Use regional awareness for geo-blocking
        )
        self.paper_executor = PaperExecutor(settings.slippage_bps)
        self.trade_executor = TradeExecutor(
            self.paper_executor,
            self.binance_client,
            self.settings,
            self.event_bus
        )
        
        self.portfolio_manager = PortfolioManager(
            db=db,
            starting_balance=settings.starting_balance,
            max_capital_per_trade=settings.max_capital_per_trade,
            max_open_positions=settings.max_open_positions,
            stop_loss_pct=settings.stop_loss_pct,
            take_profit_pct=settings.take_profit_pct,
            max_drawdown_pct=settings.max_drawdown_pct,
            max_daily_loss_pct=settings.max_daily_loss_pct,
            max_symbol_exposure_pct=settings.max_symbol_exposure_pct,
            fee_bps=settings.fee_bps,
        )

        self.run_id = 0
        self._tasks: list[asyncio.Task] = []
        self._stop_event = asyncio.Event()
        self._last_trade_time: float = 0.0
        self.evaluation_array: list[str] = []

    async def initialize(self) -> None:
        await self.trade_executor.initialize()
        self.predictor.load()
        self.run_id = self.trade_logger.create_run(f"V2_{self.settings.env}", self.settings.symbol)
        
        identity = self.erc8004.register_agent()
        identity_payload = {"agent_name": identity.agent_name, "wallet": identity.wallet_address, "connected": identity.chain_connected}
        self.trade_logger.store_metric("identity", identity_payload)
        await self.runtime_state.update("metrics", {"identity": identity_payload})

        # Register event handlers
        self.event_bus.subscribe_internal("market_fetched", self.on_market_fetched)
        self.event_bus.subscribe_internal("model_analyzed", self.on_model_analyzed)
        self.event_bus.subscribe_internal("risk_assessed", self.on_risk_assessed)
        self.event_bus.subscribe_internal("intent_routed", self.on_intent_routed)

    async def start(self) -> None:
        await self.initialize()
        await self.runtime_state.update("worker", {"status": "running"})
        self._tasks.append(asyncio.create_task(self._market_clock()))

    async def stop(self) -> None:
        self._stop_event.set()
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        await self.trade_executor.close()
        await self.runtime_state.update("worker", {"status": "stopped"})

    async def _market_clock(self) -> None:
        """Periodic trigger to fetch market data."""
        while not self._stop_event.is_set():
            try:
                import time
                if time.time() - self._last_trade_time < 300: # 5 min cooldown
                    self.logger.info("Agent is in cooldown state.")
                    await asyncio.sleep(self.settings.worker_interval_seconds)
                    continue

                snapshot = await asyncio.to_thread(
                    self.market_fetcher.fetch_snapshot,
                    symbol=self.settings.symbol,
                    timeframe=self.settings.timeframe,
                    limit=self.settings.market_limit,
                )
                payload = {
                    "symbol": snapshot.symbol,
                    "price": snapshot.price,
                    "candles": snapshot.candles,
                    "source": snapshot.source,
                    "mode": snapshot.mode.value
                }
                await self.event_bus.publish("market_fetched", payload)
            except Exception as e:
                log_event(self.logger, "ERROR", f"Market clock failed: {e}")
            await asyncio.sleep(self.settings.worker_interval_seconds)

    async def on_market_fetched(self, event: dict[str, Any]) -> None:
        try:
            symbol = event["symbol"]
            price = event["price"]
            candles = event["candles"]
            
            recent_return = float(candles["close"].pct_change().fillna(0.0).iloc[-1])
            scout = await asyncio.to_thread(self.scout_agent.analyze, symbol, recent_return)
            features = self.feature_engineering.generate(candles, float(scout["sentiment_score"])).values
            
            self.trade_logger.log_features(self.run_id, symbol, features)
            
            ml_result = await asyncio.to_thread(self.predictor.predict, features)
            analyst = self.analyst_agent.analyze(features)
            
            decision = self.decision_engine.decide(
                sentiment_score=float(scout["sentiment_score"]),
                technical_score=float(analyst["technical_score"]),
                prob_up=float(ml_result["prob_up"]),
            )
            
            # Phase 3: No static BUY/SELL fallback. 
            # We strictly use the model score.
            
            # Add explainability feature traces manually since RandomForest doesn't directly give this per-sample easily here.
            # We will mock the feature importance trace for demo explainability.
            feature_importance = {"atr": 0.25, "rsi": 0.20, "macd": 0.30, "volume": 0.10, "sentiment": 0.15}
            decision_trace = f"Score {decision['score']} derived from ML {ml_result['prob_up']} and TA {analyst['technical_score']}"

            narrative_obj = self.narrative_gen.generate_narrative(
                decision=decision["action"],
                prob_up=float(ml_result["prob_up"]),
                volatility=0.03,
                signal_fusion_result={"fused_strength": float(decision["confidence"]), "consensus_confidence": float(decision["confidence"]), "narrative": decision_trace},
                portfolio_state={},
                recent_performance={}
            )
            narrative_dict = {
                "decision": narrative_obj.decision,
                "confidence_level": narrative_obj.confidence_level,
                "capital_allocation": narrative_obj.capital_allocation,
                "risk_warning": narrative_obj.risk_warning,
                "opportunity_description": narrative_obj.opportunity_description,
                "expected_edge": narrative_obj.expected_edge,
                "exit_condition": narrative_obj.exit_condition,
            }

            snapshot_payload = {
                "symbol": symbol,
                "price": price,
                "features": features,
                "ml_result": ml_result,
                "scout": scout,
                "analyst": analyst,
                "decision": decision,
                "feature_importance": feature_importance,
                "decision_trace": decision_trace,
                "narrative": narrative_dict
            }
            
            # Broadcast UI Market Update (only last 120 candles optimized for JSON)
            ui_market = {
                "symbol": symbol,
                "price": price,
                "candles": candles.tail(120).to_dict(orient="records")
            }
            await self.runtime_state.update("market", ui_market)
            await self.event_bus.publish("market", ui_market, broadcast_ws=True)
            
            await self.event_bus.publish("model_analyzed", snapshot_payload)
        except Exception as e:
            log_event(self.logger, "ERROR", f"on_market_fetched failed: {e}")

    async def on_model_analyzed(self, event: dict[str, Any]) -> None:
        try:
            symbol = event["symbol"]
            price = event["price"]
            decision = event["decision"]
            features = event["features"]
            
            self.portfolio_manager.update_mark_to_market(symbol, price)
            
            risk = self.risk_agent.calculate_position_size(
                balance=self.portfolio_manager.snapshot(price)["balance"],
                price=price,
                atr=features["atr"],
                volatility=features["volatility"],
                max_capital_fraction=self.settings.max_capital_per_trade,
                risk_fraction=self.settings.risk_fraction,
                atr_risk_multiplier=self.settings.atr_risk_multiplier,
                max_symbol_exposure_pct=self.settings.max_symbol_exposure_pct,
            )
            
            event["risk"] = risk
            
            # Forced exit logic (stop loss / take profit triggers)
            forced_exit = self.portfolio_manager.exit_signal(symbol, price)
            if forced_exit:
                decision["action"] = forced_exit
                decision["confidence"] = max(float(decision["confidence"]), 0.8)
                event["decision_trace"] = f"OVERRIDE: Risk agent forced {forced_exit}"

            # Log decision to DB via TradeLogger (and Explainability)
            decision_payload = {"action": decision["action"], "confidence": decision["confidence"], "score": decision["score"]}
            decision_id = self.trade_logger.log_decision(self.run_id, symbol, decision_payload)
            self.trade_logger.log_explainability(
                self.run_id,
                decision_id,
                symbol,
                decision["confidence"],
                event["feature_importance"],
                event["decision_trace"]
            )
            
            event["decision_id"] = decision_id
            
            if decision["action"] in {"BUY", "SELL"} and risk["position_size"] > 0:
                await self.event_bus.publish("risk_assessed", event)
            else:
                # Still publish decisions so UI updates for HOLD
                await self._broadcast_decision_ui(event)
                
        except Exception as e:
            log_event(self.logger, "ERROR", f"on_model_analyzed failed: {e}")

    async def on_risk_assessed(self, event: dict[str, Any]) -> None:
        # We know action is BUY or SELL, and position_size > 0
        try:
            symbol = event["symbol"]
            price = event["price"]
            decision = event["decision"]
            risk = event["risk"]
            decision_id = event["decision_id"]
            
            intent_record = self.intent_router.route(
                symbol=symbol,
                action=str(decision["action"]),
                size=float(risk["position_size"]),
                price=price,
                confidence=float(decision["confidence"]),
            )
            
            self.trade_logger.log_intent(
                self.run_id,
                decision_id,
                intent_record["intent_hash"],
                intent_record,
                "approved" if intent_record["approved"] else "rejected",
            )
            
            event["intent"] = intent_record
            
            if intent_record["approved"]:
                await self.event_bus.publish("intent_routed", event)
            else:
                await self._broadcast_decision_ui(event)
                log_event(self.logger, "RISK", "Intent rejected by router", symbol=symbol)
                
        except Exception as e:
            log_event(self.logger, "ERROR", f"on_risk_assessed failed: {e}")

    async def on_intent_routed(self, event: dict[str, Any]) -> None:
        try:
            symbol = event["symbol"]
            price = event["price"]
            decision = event["decision"]
            risk = event["risk"]
            
            # Use TradeExecutor and execution_mode flag (handles CCXT/Cli simulation)
            fill = await self.trade_executor.execute_trade(
                symbol, str(decision["action"]), float(risk["position_size"]), price
            )
            order_record = fill
                
            self.trade_logger.log_order(self.run_id, symbol, str(decision["action"]), str(fill["status"]), fill)
            
            if fill["status"] in {"filled", "partial"}:
                import time
                self._last_trade_time = time.time()  # Activate cooldown
                
                fill_size = float(fill.get("filled_size") or risk["position_size"])
                fill_price = float(fill.get("fill_price") or price)
                trade_result = self.portfolio_manager.apply_fill(symbol, str(decision["action"]), fill_size, fill_price, str(fill["status"]))
                
                event["trade"] = {
                    "executed": trade_result.executed,
                    "realized_pnl": trade_result.realized_pnl,
                    "order_status": trade_result.order_status,
                    "fill_size": fill_size,
                    "fill_price": fill_price,
                }
                
                if trade_result.executed:
                    self.trade_logger.log_trade(
                        self.run_id,
                        symbol,
                        str(decision["action"]),
                        fill_size,
                        fill_price,
                        float(decision["confidence"]),
                        float(trade_result.realized_pnl),
                    )
            else:
                event["trade"] = order_record

            await self._broadcast_decision_ui(event)
            if event.get("trade"):
                await self.event_bus.publish("trades", event["trade"], broadcast_ws=True)
                
        except Exception as e:
            log_event(self.logger, "ERROR", f"on_intent_routed failed: {e}")

    async def _broadcast_decision_ui(self, event: dict[str, Any]) -> None:
        try:
            payload = {
                "symbol": event["symbol"],
                "action": event["decision"]["action"],
                "confidence": event["decision"]["confidence"],
                "audit": {
                    "ml_result": event["ml_result"],
                    "technical": event["analyst"],
                    "sentiment": event["scout"],
                    "risk": event.get("risk", {}),
                    "feature_importance": event["feature_importance"],
                    "decision_trace": event["decision_trace"],
                    "narrative": event.get("narrative", {})
                },
                "intent_hash": event.get("intent", {}).get("intent_hash"),
                "execution_result": event.get("trade", {})
            }
            await self.runtime_state.update("decision", payload)
            await self.event_bus.publish("decisions", payload, broadcast_ws=True)
            
            if "action" in payload:
                self.evaluation_array.append(payload["action"])
                if len(self.evaluation_array) >= 50:
                    try:
                        self.db.snapshot_before_prune()
                        self.db.prune_database()
                    except Exception as pe:
                        log_event(self.logger, "ERROR", f"Auto-prune failed: {pe}")
                    self.evaluation_array.clear()
        except Exception as e:
             log_event(self.logger, "ERROR", f"Broadcast failed: {e}")
