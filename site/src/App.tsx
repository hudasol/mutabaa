import { useEffect, useMemo, useState } from "react";
import { C } from "./ctx";
import { dict, type Lang } from "./i18n";
import { Brief, Clocks, Lab, Ledger, Maturity, Method, Overview } from "./pages";
import raw from "./data/real.json";
import type { Payload } from "./types";

const data = raw as unknown as Payload;
const ROUTES = [
  ["overview", "nav_overview", Overview], ["ledger", "nav_ledger", Ledger], ["clocks", "nav_clocks", Clocks],
  ["lab", "nav_lab", Lab], ["maturity", "nav_maturity", Maturity], ["brief", "nav_brief", Brief], ["method", "nav_method", Method],
] as const;

const route = () => (location.hash.replace(/^#\/?/, "") || "overview");

export default function App() {
  const [lang, setLang] = useState<Lang>(() => {
    try { return (localStorage.getItem("lang") as Lang) || (navigator.language.startsWith("ar") ? "ar" : "en"); } catch { return "en"; }
  });
  const [r, setR] = useState(route());
  useEffect(() => { const f = () => setR(route()); window.addEventListener("hashchange", f); return () => window.removeEventListener("hashchange", f); }, []);
  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    try { localStorage.setItem("lang", lang); } catch { /* storage unavailable */ }
  }, [lang]);
  const t = dict[lang];
  const ctx = useMemo(() => ({ lang, t, data }), [lang, t]);
  const current = ROUTES.find((x) => x[0] === r) ?? ROUTES[0];
  const Page = current[2];
  useEffect(() => { document.title = `${t[current[1]]} · ${t.appName}`; }, [t, current]);
  return (
    <C.Provider value={ctx}>
      <div className="shell">
        <aside className="rail">
          <div className="brand"><b>{t.appName}</b><small>{t.theme_note}</small></div>
          <nav aria-label="Main">
            {ROUTES.map(([id, key]) => <a key={id} href={`#/${id}`} aria-current={current[0] === id ? "page" : undefined}>{t[key]}</a>)}
          </nav>
          <button className="lang" onClick={() => setLang(lang === "en" ? "ar" : "en")} lang={lang === "en" ? "ar" : "en"}>{t.lang_switch}</button>
          <div className="foot"><span>{t.footer}</span></div>
        </aside>
        <main id="main"><Page /></main>
      </div>
    </C.Provider>
  );
}
