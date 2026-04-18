"use client";

import type { ReactNode } from "react";
import { StoreInitializer } from "./store-initializer";

export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <>
      <StoreInitializer />
      {children}
    </>
  );
}
