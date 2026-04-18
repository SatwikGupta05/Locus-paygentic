"use client";

import { useEffect, useRef, useState } from "react";
import styles from "./Dashboard.module.css";
import { MiniCandleChart } from "@/components/charts/MiniCandleChart";
import { useMarketStore } from "@/store/marketStore";
import type { ExchangeName } from "@/types";
import { formatCurrency, formatLatency, formatPercent } from "@/utils/formatters";

const exchangeOrder: ExchangeName[] = ["kraken", "binance", "kucoin"];

export function MarketStateCard() {
  const { pair, bestPrice, bestExchange, spread, exchanges, volatilityRegime } = useMarketStore();
  const previousPrice = useRef(bestPrice);
  const [tickClass, setTickClass] = useState("");

  useEffect(() => {
    if (!bestPrice || previousPrice.current === bestPrice) {
      return;
    }

    setTickClass(bestPrice > previousPrice.current ? styles.tickUp : styles.tickDown);
    previousPrice.current = bestPrice;

    const timeout = window.setTimeout(() => setTickClass(""), 600);
    return () => window.clearTimeout(timeout);
  }, [bestPrice]);

  return (
    <section className={`${styles.card} ${styles.span8}`}>
      <div className={styles.cardHeader}>
        <div>
          <div className={styles.cardTitle}>Market State</div>
          <div className={`${styles.livePrice} ${tickClass}`}>{formatCurrency(bestPrice)}</div>
          <div className={styles.subtle}>
            {pair} via {bestExchange}
          </div>
        </div>
        <div className={styles.stack}>
          <span className={`${styles.badge} ${styles.badgeLive}`}>Spread {formatPercent(spread, 3)}</span>
          <span className={styles.badge}>Volatility {volatilityRegime}</span>
        </div>
      </div>
      <div className={styles.table}>
        {exchangeOrder.map((exchange) => (
          <div
            key={exchange}
            className={`${styles.marketRow} ${bestExchange === exchange ? styles.bestRow : ""}`}
          >
            <span className={styles.rowLabel}>{exchange}</span>
            <span className={styles.rowVal}>{formatCurrency(exchanges[exchange].price)}</span>
            <span className={styles.rowVal}>{formatCurrency(exchanges[exchange].bid)}</span>
            <span className={styles.rowVal}>{formatCurrency(exchanges[exchange].ask)}</span>
            <span className={styles.rowVal}>{formatLatency(exchanges[exchange].lastUpdate)}</span>
          </div>
        ))}
      </div>
      <div className={styles.chartWrap}>
        <MiniCandleChart candles={exchanges[bestExchange].candles} />
      </div>
    </section>
  );
}
