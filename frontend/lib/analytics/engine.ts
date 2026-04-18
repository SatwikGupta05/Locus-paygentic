import type { AnalyticsMetrics, EquityPoint, Trade } from "@/types";

function computeTradePnl(trade: Trade): number {
  const gross = trade.type === "sell" ? trade.cost : -trade.cost;
  return gross - trade.fee;
}

export function computeWinRate(trades: Trade[]): number {
  if (trades.length === 0) {
    return 0;
  }

  const wins = trades.filter((trade) => computeTradePnl(trade) > 0).length;
  return (wins / trades.length) * 100;
}

export function computeProfitFactor(trades: Trade[]): number {
  const pnls = trades.map(computeTradePnl);
  const positive = pnls.filter((pnl) => pnl > 0).reduce((sum, pnl) => sum + pnl, 0);
  const negative = pnls.filter((pnl) => pnl < 0).reduce((sum, pnl) => sum + pnl, 0);

  if (negative === 0) {
    return positive > 0 ? Number.POSITIVE_INFINITY : 0;
  }

  return positive / Math.abs(negative);
}

export function computeMaxDrawdown(equityCurve: number[]): number {
  if (equityCurve.length < 2) {
    return 0;
  }

  let peak = equityCurve[0];
  let maxDrawdown = 0;

  equityCurve.forEach((value) => {
    peak = Math.max(peak, value);
    const drawdown = peak === 0 ? 0 : ((peak - value) / peak) * 100;
    maxDrawdown = Math.max(maxDrawdown, drawdown);
  });

  return maxDrawdown;
}

export function computeSharpeRatio(equityCurve: number[]): number {
  if (equityCurve.length < 2) {
    return 0;
  }

  const returns: number[] = [];

  for (let index = 1; index < equityCurve.length; index += 1) {
    const previous = equityCurve[index - 1];
    const current = equityCurve[index];
    if (previous !== 0) {
      returns.push((current - previous) / previous);
    }
  }

  if (returns.length === 0) {
    return 0;
  }

  const mean = returns.reduce((sum, value) => sum + value, 0) / returns.length;
  const variance =
    returns.reduce((sum, value) => sum + (value - mean) ** 2, 0) / returns.length;
  const stdDev = Math.sqrt(variance);

  if (stdDev === 0) {
    return 0;
  }

  return (mean / stdDev) * Math.sqrt(252);
}

export function computeConsistency(equityCurve: number[]): number {
  if (equityCurve.length < 2) {
    return 0;
  }

  let positivePeriods = 0;

  for (let index = 1; index < equityCurve.length; index += 1) {
    if (equityCurve[index] > equityCurve[index - 1]) {
      positivePeriods += 1;
    }
  }

  return (positivePeriods / (equityCurve.length - 1)) * 100;
}

export function buildEquityCurve(trades: Trade[], startingCapital: number): EquityPoint[] {
  const sortedTrades = [...trades].sort((left, right) => left.time - right.time);
  let equity = startingCapital;

  return sortedTrades.map((trade) => {
    equity += computeTradePnl(trade);
    return {
      x: trade.time,
      y: equity
    };
  });
}

export function computeAnalyticsMetrics(
  trades: Trade[],
  startingCapital: number
): AnalyticsMetrics {
  const equityCurvePoints = buildEquityCurve(trades, startingCapital);
  const equityValues =
    equityCurvePoints.length > 0
      ? [startingCapital, ...equityCurvePoints.map((point) => point.y)]
      : [startingCapital];

  return {
    winRate: computeWinRate(trades),
    profitFactor: computeProfitFactor(trades),
    maxDrawdown: computeMaxDrawdown(equityValues),
    sharpeRatio: computeSharpeRatio(equityValues),
    consistency: computeConsistency(equityValues),
    equityCurve: equityCurvePoints
  };
}
