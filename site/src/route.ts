// Hash routes with shareable state: #/ledger?j=federal&open=C01
import { useCallback, useEffect, useState } from "react";

export type Route = { page: string; params: Record<string, string> };

export function parseHash(hash: string): Route {
  const raw = hash.replace(/^#\/?/, "");
  const [path, query = ""] = raw.split("?");
  const params: Record<string, string> = {};
  for (const [k, v] of new URLSearchParams(query)) params[k] = v;
  return { page: path || "overview", params };
}

export function buildHash(page: string, params: Record<string, string | undefined> = {}): string {
  const q = new URLSearchParams();
  for (const k of Object.keys(params).sort()) {
    const v = params[k];
    if (v !== undefined && v !== "") q.set(k, v);
  }
  const s = q.toString();
  return `#/${page}${s ? `?${s}` : ""}`;
}

export function useRoute(): [Route, (updates: Record<string, string | undefined>) => void] {
  const [route, setRoute] = useState<Route>(() => parseHash(location.hash));
  useEffect(() => {
    const f = () => setRoute(parseHash(location.hash));
    window.addEventListener("hashchange", f);
    return () => window.removeEventListener("hashchange", f);
  }, []);
  const update = useCallback((updates: Record<string, string | undefined>) => {
    setRoute((r) => {
      const merged: Record<string, string | undefined> = { ...r.params, ...updates };
      const params: Record<string, string> = {};
      for (const k of Object.keys(merged)) {
        const v = merged[k];
        if (v !== undefined && v !== "") params[k] = v;
      }
      try { history.replaceState(null, "", buildHash(r.page, params)); } catch { /* sandboxed */ }
      return { page: r.page, params };
    });
  }, []);
  return [route, update];
}
