import { useEffect, useMemo, useState } from "react";
import { C } from "./ctx";
import { useItemsState } from "./parts";
import { dict, type Lang } from "./i18n";
import { buildHash, useRoute } from "./route";
import Brief from "./pages/Brief";
import Clocks from "./pages/Clocks";
import Lab from "./pages/Lab";
import Ledger from "./pages/Ledger";
import Maturity from "./pages/Maturity";
import Method from "./pages/Method";
import Overview from "./pages/Overview";
import Assurance from "./pages/Assurance";
import Portfolio from "./pages/Portfolio";
import Sources from "./pages/Sources";
import raw from "./data/real.json";
import type { Payload } from "./types";

const data = raw as unknown as Payload;
const ROUTES = [
  ["overview", "nav_overview", Overview], ["ledger", "nav_ledger", Ledger], ["clocks", "nav_clocks", Clocks],
  ["lab", "nav_lab", Lab], ["portfolio", "nav_portfolio", Portfolio], ["maturity", "nav_maturity", Maturity], ["sources", "nav_sources", Sources],
  ["brief", "nav_brief", Brief], ["method", "nav_method", Method], ["assurance", "nav_assurance", Assurance],
] as const;

type Theme = "auto" | "light" | "dark";
const read = (k: string) => { try { return localStorage.getItem(k); } catch { return null; } };

export default function App() {
  const [lang, setLang] = useState<Lang>(() => (read("lang") as Lang) || (navigator.language.startsWith("ar") ? "ar" : "en"));
  const [theme, setTheme] = useState<Theme>(() => (read("theme") as Theme) || "auto");
  const [route, setParams] = useRoute();
  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    try { localStorage.setItem("lang", lang); } catch { /* storage unavailable */ }
  }, [lang]);
  useEffect(() => {
    if (theme === "auto") document.documentElement.removeAttribute("data-theme");
    else document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem("theme", theme); } catch { /* storage unavailable */ }
  }, [theme]);
  const t = dict[lang];
  const items = useItemsState(data);
  const ctx = useMemo(() => ({ lang, t, data, route, setParams, items }), [lang, t, route, setParams, items]);
  const current = ROUTES.find((x) => x[0] === route.page) ?? ROUTES[0];
  const Page = current[2];
  useEffect(() => { document.title = `${t[current[1]]} · ${t.appName}`; }, [t, current]);
  useEffect(() => { window.scrollTo?.(0, 0); }, [route.page]);
  return (
    <C.Provider value={ctx}>
      <a className="skip" href="#main">Skip to content</a>
      <div className="shell">
        <aside className="rail">
          <div className="brand"><b>{t.appName}</b><small>{t.theme_note}</small></div>
          <nav aria-label="Main">
            {ROUTES.map(([id, key]) => <a key={id} href={buildHash(id)} aria-current={current[0] === id ? "page" : undefined}>{t[key]}</a>)}
          </nav>
          <div className="tools">
            <button className="lang" onClick={() => setLang(lang === "en" ? "ar" : "en")} lang={lang === "en" ? "ar" : "en"}>{t.lang_switch}</button>
            <div className="seg small-seg" role="group" aria-label={t.th_label}>
              {(["auto", "light", "dark"] as Theme[]).map((k) => (
                <button key={k} aria-pressed={theme === k} onClick={() => setTheme(k)}>{t[`th_${k}` as "th_auto"]}</button>
              ))}
            </div>
          </div>
          <div className="foot">
            <span>{t.ft_asof} {data.build.data_as_of}</span>
            <span className="mono">{data.build.payload_sha256.slice(0, 12)}</span>
            <span>{t.footer}</span>
          </div>
        </aside>
        <main id="main"><Page /></main>
      </div>
    </C.Provider>
  );
}
