import { createContext, useContext } from "react";
import type { Dict, Lang } from "./i18n";
import type { Route } from "./route";
import type { Payload } from "./types";

export type Ctx = {
  lang: Lang; t: Dict; data: Payload; route: Route;
  setParams: (u: Record<string, string | undefined>) => void;
};
export const C = createContext<Ctx>(null as unknown as Ctx);
export const useCtx = () => useContext(C);

export const pct = (x: number | null, d = 0) => (x === null ? "n/a" : `${(x * 100).toFixed(d)}%`);
export const L = (lang: Lang, en: string, ar: string) => (lang === "ar" ? ar : en);
export function download(name: string, text: string, type: string) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = document.createElement("a");
  a.href = url; a.download = name; a.click();
  URL.revokeObjectURL(url);
}
export async function copyText(text: string): Promise<boolean> {
  try { await navigator.clipboard.writeText(text); return true; } catch { return false; }
}
