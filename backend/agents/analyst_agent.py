from __future__ import annotations


class AnalystAgent:
    def analyze(self, feature_vector: dict[str, float]) -> dict[str, float | str]:
        score = 0.0
        score += 0.35 if feature_vector["rsi"] < 35 else -0.35 if feature_vector["rsi"] > 65 else 0.0
        score += 0.25 if feature_vector["macd_hist"] > 0 else -0.25
        score += 0.20 if feature_vector["momentum"] > 0 else -0.20
        score += 0.20 if feature_vector["ema_fast_gap"] > feature_vector["ema_slow_gap"] else -0.20

        signal = "BULLISH" if score > 0.15 else "BEARISH" if score < -0.15 else "NEUTRAL"
        return {"technical_score": round(score, 4), "signal": signal}
