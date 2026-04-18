import "./globals.css";
import type { ReactNode } from "react";
import { StoreInitializer } from "../components/store-initializer";

export const metadata = {
  title: "AURORA - Autonomous AI Trading Agent",
  description: "Enterprise-grade autonomous trading with intelligent risk management and multi-exchange failover.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen text-slate-900 antialiased">
        <StoreInitializer />
        {children}
      </body>
    </html>
  );
}
