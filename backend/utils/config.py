from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
MODELS_DIR = ROOT_DIR / "models"
DATA_DIR = ROOT_DIR / "data"
STATE_DIR = BACKEND_DIR / "state"
LOGS_DIR = BACKEND_DIR / "logs"
MIGRATIONS_DIR = BACKEND_DIR / "database" / "migrations"


load_dotenv(ROOT_DIR / ".env")


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


@dataclass(slots=True)
class Settings:
    env: str = os.getenv("ENV", "DEMO").upper()
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = _get_int("PORT", 8000)
    symbol: str = os.getenv("DEFAULT_SYMBOL", "BTC/USD")
    timeframe: str = os.getenv("TIMEFRAME", "1m")
    market_limit: int = _get_int("MARKET_LIMIT", 200)
    worker_interval_seconds: float = _get_float("WORKER_INTERVAL_SECONDS", 5)
    auto_start_worker: bool = _get_bool("AUTO_START_WORKER", True)
    data_mode: str = os.getenv("DATA_MODE", "").upper()
    historical_days: int = _get_int("HISTORICAL_DAYS", 30)
    starting_balance: float = _get_float("STARTING_BALANCE", 10000)
    max_capital_per_trade: float = _get_float("MAX_CAPITAL_PER_TRADE", 0.10)
    max_open_positions: int = _get_int("MAX_OPEN_POSITIONS", 2)
    stop_loss_pct: float = _get_float("STOP_LOSS_PCT", 0.02)
    take_profit_pct: float = _get_float("TAKE_PROFIT_PCT", 0.05)
    max_drawdown_pct: float = _get_float("MAX_DRAWDOWN_PCT", 0.15)
    max_daily_loss_pct: float = _get_float("MAX_DAILY_LOSS_PCT", 0.05)
    max_symbol_exposure_pct: float = _get_float("MAX_SYMBOL_EXPOSURE_PCT", 0.20)
    atr_risk_multiplier: float = _get_float("ATR_RISK_MULTIPLIER", 1.5)
    fee_bps: float = _get_float("FEE_BPS", 20)
    slippage_bps: float = _get_float("SLIPPAGE_BPS", 10)
    risk_fraction: float = _get_float("RISK_FRACTION", 0.02)
    kraken_binary: str = os.getenv("KRAKEN_BINARY", "kraken")
    max_consecutive_losses: int = _get_int("MAX_CONSECUTIVE_LOSSES", 5)
    min_confidence: float = _get_float("MIN_CONFIDENCE", 0.15)
    kraken_api_key: str = os.getenv("KRAKEN_API_KEY", "")
    kraken_secret: str = os.getenv("KRAKEN_SECRET", "")
    binance_api_key: str = os.getenv("BINANCE_API_KEY", "")
    binance_secret: str = os.getenv("BINANCE_SECRET", "")
    user_region: str = os.getenv("USER_REGION", "india").lower()  # india, default, us, eu, etc
    execution_mode: str = os.getenv("EXECUTION_MODE", "SIMULATED").upper()
    blockchain_enabled: bool = _get_bool("BLOCKCHAIN_ENABLED", False)
    force_kraken_failure: bool = _get_bool("FORCE_KRAKEN_FAILURE", False)
    wallet_private_key: str = os.getenv("WALLET_PRIVATE_KEY", "")
    agent_wallet_private_key: str = os.getenv("AGENT_WALLET_PRIVATE_KEY", "") or os.getenv("WALLET_PRIVATE_KEY", "")
    agent_wallet_address: str = os.getenv("AGENT_WALLET_ADDRESS", "")
    rpc_url: str = os.getenv("SEPOLIA_RPC_URL", "") or os.getenv("RPC_URL", "")
    chain_id: int = _get_int("CHAIN_ID", 11155111)
    # ─── Shared Sepolia Contract Addresses ───
    agent_registry_address: str = os.getenv("IDENTITY_REGISTRY_ADDRESS") or os.getenv("AGENT_REGISTRY_ADDRESS", "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3")
    hackathon_vault_address: str = os.getenv("CAPITAL_VAULT_ADDRESS") or os.getenv("HACKATHON_VAULT_ADDRESS", "0x0E7CD8ef9743FEcf94f9103033a044caBD45fC90")
    risk_router_address: str = os.getenv("RISK_ROUTER_ADDRESS", "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC")
    reputation_registry_address: str = os.getenv("REPUTATION_REGISTRY_ADDRESS", "0x423a9904e39537a9997fbaF0f220d79D7d545763")
    validation_registry_address: str = os.getenv("VALIDATION_REGISTRY_ADDRESS", "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1")
    # ─── Agent Identity ───
    agent_id: int = _get_int("AGENT_ID", 0)
    agent_name: str = os.getenv("AGENT_NAME", "AURORA-AI")
    agent_uri: str = os.getenv("AGENT_URI", "https://aurora-ai-agent.dev/metadata.json")
    # ─── PRISM API ───
    prism_api_key: str = os.getenv("PRISM_API_KEY", "")
    prism_base_url: str = os.getenv("PRISM_BASE_URL", "https://api.prismapi.ai")
    # ─── Resilience ───
    max_retries: int = _get_int("MAX_RETRIES", 3)
    gas_buffer_multiplier: float = _get_float("GAS_BUFFER_MULTIPLIER", 1.2)
    enable_paper_mode: bool = _get_bool("ENABLE_PAPER_MODE", True)
    trading_pair: str = os.getenv("TRADING_PAIR", "XBTUSD")
    # ─── Legacy compat ───
    verifying_contract: str = os.getenv("RISK_ROUTER_ADDRESS", "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    news_urls: tuple[str, ...] = tuple(
        item.strip()
        for item in os.getenv(
            "NEWS_FEEDS",
            "https://www.coindesk.com/arc/outboundfeeds/rss/,https://cointelegraph.com/rss",
        ).split(",")
        if item.strip()
    )
    db_path: Path = STATE_DIR / "aurora.db"
    log_path: Path = LOGS_DIR / "aurora.log"
    model_path: Path = MODELS_DIR / "model.pkl"
    feature_schema_path: Path = MODELS_DIR / "feature_schema.json"
    training_report_path: Path = MODELS_DIR / "training_report.json"
    backtest_report_path: Path = MODELS_DIR / "backtest_report.json"
    historical_data_path: Path = DATA_DIR / "historical" / "market_data.parquet"

    def __post_init__(self) -> None:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "historical").mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        if not self.data_mode:
            self.data_mode = "SYNTHETIC" if self.env == "DEMO" else "PAPER" if self.env == "PAPER" else "LIVE"
        if self.env not in {"DEMO", "PAPER", "LIVE"}:
            raise ValueError(f"Unsupported ENV={self.env}")
        if self.data_mode not in {"LIVE", "PAPER", "SYNTHETIC"}:
            raise ValueError(f"Unsupported DATA_MODE={self.data_mode}")


def get_settings() -> Settings:
    return Settings()
