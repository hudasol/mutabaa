// Each page is loaded when first visited. The offline build swaps this file for pagesEager.ts.
import { lazy } from "react";

export const Brief = lazy(() => import("./pages/Brief"));
export const Clocks = lazy(() => import("./pages/Clocks"));
export const Lab = lazy(() => import("./pages/Lab"));
export const Ledger = lazy(() => import("./pages/Ledger"));
export const Maturity = lazy(() => import("./pages/Maturity"));
export const Method = lazy(() => import("./pages/Method"));
export const Overview = lazy(() => import("./pages/Overview"));
export const Assurance = lazy(() => import("./pages/Assurance"));
export const Portfolio = lazy(() => import("./pages/Portfolio"));
export const Mine = lazy(() => import("./pages/Mine"));
export const Sources = lazy(() => import("./pages/Sources"));
