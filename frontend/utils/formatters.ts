export function formatCurrency(value: number, digits = 2): string {
  if (!Number.isFinite(value)) {
    return "--";
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  }).format(value);
}

export function formatNumber(value: number, digits = 2): string {
  if (!Number.isFinite(value)) {
    return "--";
  }

  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  }).format(value);
}

export function formatPercent(value: number, digits = 2): string {
  if (!Number.isFinite(value)) {
    return "--";
  }

  return `${formatNumber(value, digits)}%`;
}

export function formatLatency(timestamp: number): string {
  if (!timestamp) {
    return "--";
  }

  return `${Math.max(0, Date.now() - timestamp)} ms`;
}

export function formatAddress(value: string): string {
  if (!value) {
    return "--";
  }

  return `${value.slice(0, 6)}...${value.slice(-4)}`;
}
