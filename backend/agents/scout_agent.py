from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import requests


POSITIVE_TERMS = {"surge", "rally", "approval", "breakout", "adoption", "growth", "inflow", "bull"}
NEGATIVE_TERMS = {"hack", "lawsuit", "crash", "liquidation", "outflow", "bear", "ban", "fear"}


class ScoutAgent:
    def __init__(self, news_urls: tuple[str, ...], timeout: int = 5) -> None:
        self.news_urls = news_urls
        self.timeout = timeout

    def analyze(self, symbol: str, recent_return: float) -> dict[str, float | str]:
        headlines: list[str] = []
        for url in self.news_urls:
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                root = ET.fromstring(response.text)
                headlines.extend(
                    re.sub(r"\s+", " ", title.text or "").strip().lower()
                    for title in root.findall(".//item/title")[:8]
                )
            except Exception:
                continue

        if headlines:
            score = 0
            for title in headlines:
                score += sum(term in title for term in POSITIVE_TERMS)
                score -= sum(term in title for term in NEGATIVE_TERMS)
            sentiment = max(-1.0, min(1.0, score / max(len(headlines), 1)))
            source = "rss"
        else:
            sentiment = max(-1.0, min(1.0, recent_return * 8))
            source = "fallback"

        return {"sentiment_score": round(float(sentiment), 4), "source": source, "symbol": symbol}
