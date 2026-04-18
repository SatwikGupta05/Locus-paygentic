"use client";

import styles from "@/components/dashboard/Dashboard.module.css";
import { useMarketStore } from "@/store/marketStore";
import { useSystemStore } from "@/store/systemStore";
import type { ExchangeName } from "@/types";
import { formatCurrency } from "@/utils/formatters";

const exchangeOrder: ExchangeName[] = ["kraken", "binance", "kucoin"];

function ExchangeLogo({ exchange }: { exchange: ExchangeName }) {
  const initials = exchange === "kraken" ? "K" : exchange === "binance" ? "B" : "Kc";
  return <span className={styles.exchangeLogo}>{initials}</span>;
}

export function ExchangeSelector() {
  const activeExchanges = useMarketStore((state) => state.activeExchanges);
  const exchanges = useMarketStore((state) => state.exchanges);
  const setActiveExchanges = useMarketStore((state) => state.setActiveExchanges);
  const exchangeHealth = useSystemStore((state) => state.exchangeHealth);

  const toggle = (exchange: ExchangeName) => {
    const next = activeExchanges.includes(exchange)
      ? activeExchanges.filter((entry) => entry !== exchange)
      : [...activeExchanges, exchange];
    if (next.length > 0) {
      setActiveExchanges(next);
    }
  };

  return (
    <div className={styles.selectorWrap}>
      <div className={styles.selectorRow}>
        {exchangeOrder.map((exchange) => {
          const active = activeExchanges.includes(exchange);
          return (
            <button
              key={exchange}
              type="button"
              className={`${styles.selectorButton} ${active ? styles.selectorButtonActive : ""}`}
              data-ex={exchange}
              onClick={() => toggle(exchange)}
            >
              <div className={styles.exchangeInfo}>
                <ExchangeLogo exchange={exchange} />
                <div className={styles.selectorLabel}>
                  <span className={`${styles.healthDot} ${styles[exchangeHealth[exchange].toLowerCase()]}`} />
                  {exchange}
                </div>
              </div>
              <div className={styles.selectorPrice}>{formatCurrency(exchanges[exchange].price)}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
