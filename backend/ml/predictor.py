from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd


class SignalExplainer:
    """Generates human-readable explanations for trading signals."""
    
    def __init__(self, feature_columns: list[str]):
        self.feature_columns = feature_columns
    
    def explain_prediction(self, prob_up: float, features: dict[str, float], 
                          feature_importance: dict[str, float] | None = None) -> dict[str, str]:
        """Generate explanatory text for a prediction."""
        
        explanations = []
        
        # Price action interpretation
        if "ema_fast_gap" in features and "ema_slow_gap" in features:
            fast_gap = features["ema_fast_gap"]
            slow_gap = features["ema_slow_gap"]
            if fast_gap > slow_gap > 0:
                explanations.append("Strong uptrend: price above both EMAs with widening gap")
            elif slow_gap < 0 and fast_gap < slow_gap:
                explanations.append("Downtrend forming: price below slow EMA with negative gaps")
        
        # Momentum signals
        if "macd_hist" in features:
            macd_hist = features["macd_hist"]
            if macd_hist > 0:
                explanations.append("Positive MACD histogram suggests bullish momentum")
            elif macd_hist < 0:
                explanations.append("Negative MACD histogram suggests bearish momentum")
        
        # Volatility context
        if "volatility" in features:
            vol = features["volatility"]
            if vol > 0.03:
                explanations.append("⚠️ High market volatility detected")
            elif vol < 0.01:
                explanations.append("Market is in low-volatility regime")
        
        # Volume signal
        if "volume_spike" in features:
            vol_spike = features["volume_spike"]
            if vol_spike > 1.5:
                explanations.append("Significant volume spike detected with this move")
            elif vol_spike < 0.7:
                explanations.append("Volume below average - weak conviction signal")
        
        return {
            "factors": " | ".join(explanations) if explanations else "Neutral signal with mixed indicators",
            "probability_of_upside": f"{prob_up*100:.1f}%",
            "probability_of_downside": f"{(1-prob_up)*100:.1f}%",
        }


class Predictor:
    def __init__(self, model_path: Path, feature_schema_path: Path) -> None:
        self.model_path = Path(model_path)
        self.feature_schema_path = Path(feature_schema_path)
        self.model = None
        self.feature_columns: list[str] = []
        self.explainer: SignalExplainer | None = None

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Missing model artifact: {self.model_path}")
        if not self.feature_schema_path.exists():
            raise FileNotFoundError(f"Missing feature schema: {self.feature_schema_path}")
        self.model = joblib.load(self.model_path)
        payload = json.loads(self.feature_schema_path.read_text(encoding="utf-8"))
        self.feature_columns = list(payload["feature_columns"])
        self.explainer = SignalExplainer(self.feature_columns)

    def predict(self, features: dict[str, float] | pd.DataFrame) -> dict[str, float | str]:
        """Predict price direction with confidence and explanation."""
        if self.model is None:
            self.load()
        
        if isinstance(features, dict):
            frame = pd.DataFrame(
                [[features.get(column, 0.0) for column in self.feature_columns]], 
                columns=self.feature_columns
            )
            input_features = features
        else:
            frame = features[self.feature_columns]
            input_features = {col: float(frame[col].iloc[-1]) for col in self.feature_columns}
        
        probabilities = self.model.predict_proba(frame)[-1]
        prob_up = float(probabilities[1])
        
        # Confidence score — distance between prob_up and prob_down
        prob_down = 1 - prob_up
        confidence = abs(prob_up - prob_down)  # 0-1 scale
        
        # Generate explanation
        explanation = self.explainer.explain_prediction(prob_up, input_features) if self.explainer else {}
        
        signal = "BUY" if prob_up >= 0.55 else "SELL" if prob_up <= 0.45 else "HOLD"
        low_vol_filter = False
        
        return {
            "prob_up": round(prob_up, 4),
            "prob_down": round(prob_down, 4),
            "confidence": round(confidence, 4),
            "signal": signal,
            "volatility_filter": low_vol_filter,
            "explanation": explanation.get("factors", ""),
            "upside_probability": explanation.get("probability_of_upside", ""),
            "downside_probability": explanation.get("probability_of_downside", ""),
        }


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if sys.path[0] != str(Path(__file__).resolve().parent.parent.parent):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    
    # Fix Windows console encoding for emoji output
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    
    from backend.utils.config import get_settings
    from backend.data.feature_engineering import FeatureEngineering
    from backend.data.market_fetcher import MarketFetcher, DataMode
    
    settings = get_settings()
    predictor = Predictor(settings.model_path, settings.feature_schema_path)
    
    # Fetch REAL market data for prediction (not zeroed placeholders)
    print("\n" + "="*60)
    print("🤖 AURORA-AI PREDICTOR — LIVE TEST")
    print("="*60)
    
    try:
        print("Fetching latest market data...")
        fetcher = MarketFetcher(mode=DataMode(settings.data_mode))
        candles = fetcher.fetch_ohlcv(symbol="BTC/USD", timeframe="1m", limit=200)
        
        fe = FeatureEngineering()
        feature_vector = fe.generate(candles, sentiment_score=0.0)
        real_features = feature_vector.values
        
        price = float(candles["close"].iloc[-1])
        print(f"Current Price: ${price:,.2f}")
        print(f"Data Source:   {settings.data_mode}")
        print(f"Candles:       {len(candles)}")
        print("-" * 60)
        
        result = predictor.predict(real_features)
    except Exception as e:
        print(f"⚠️ Could not fetch live data ({e}), using model defaults...")
        # Fallback: use zeroed features matching the schema
        predictor.load()
        fallback_features = {col: 0.0 for col in predictor.feature_columns}
        result = predictor.predict(fallback_features)
    
    print(f"""
[AURORA AI]
Signal:     {result['signal']}
Confidence: {result['confidence']:.2f}
Prob UP:    {result['prob_up']:.2%}
Prob DOWN:  {result['prob_down']:.2%}
Reason:     ML + Signal Fusion
Reasoning:  {result['explanation']}
""")
    print("="*60 + "\n")
