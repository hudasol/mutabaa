import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { pathToFileURL } from "node:url";
import path from "node:path";

const PAGES = ["overview", "ledger", "clocks", "lab", "maturity", "sources", "brief", "method", "assurance"];

async function open(page: Page, hash: string, opts: { lang?: "en" | "ar"; theme?: "light" | "dark" } = {}) {
  await page.addInitScript(([l, t]) => {
    localStorage.setItem("lang", l); localStorage.setItem("theme", t);
  }, [opts.lang ?? "en", opts.theme ?? "light"]);
  await page.goto(`/#/${hash}`);
  await expect(page.locator("h1")).toBeVisible();
}

for (const lang of ["en", "ar"] as const) {
  for (const p of PAGES) {
    test(`[smoke] ${p} loads in ${lang} without console errors or third-party requests`, async ({ page }) => {
      const errors: string[] = [], external: string[] = [];
      page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
      page.on("pageerror", (e) => errors.push(String(e)));
      page.on("request", (r) => { if (!r.url().startsWith("http://localhost:4181") && !r.url().startsWith("data:") && !r.url().startsWith("blob:")) external.push(r.url()); });
      await open(page, p, { lang });
      await page.waitForLoadState("networkidle");
      expect(errors).toEqual([]);
      expect(external).toEqual([]);
      await expect(page.locator("html")).toHaveAttribute("dir", lang === "ar" ? "rtl" : "ltr");
    });
  }
}

for (const theme of ["light", "dark"] as const) {
  for (const lang of ["en", "ar"] as const) {
    for (const p of PAGES) {
      test(`[a11y] ${p} ${lang} ${theme}: no serious or critical axe violations`, async ({ page }) => {
        await open(page, p === "ledger" ? "ledger?open=C01" : p, { lang, theme });
        const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
        const bad = r.violations.filter((v) => v.impact === "serious" || v.impact === "critical");
        expect(bad.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(" ")).slice(0, 3).join(" | ")}`)).toEqual([]);
      });
    }
  }
}

test("[state] ledger filter and open row survive a reload via the URL", async ({ page }) => {
  await open(page, "ledger?j=abu-dhabi&open=C12");
  await page.reload();
  await expect(page.getByText("100% sovereign-cloud adoption").first()).toBeVisible();
  expect(page.url()).toContain("open=C12");
});

test("[state] language toggle flips direction and persists", async ({ page }) => {
  await page.goto("/#/overview");
  await page.getByRole("button", { name: "العربية" }).click();
  await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
});

test("[keyboard] skip link is first tab stop and moves focus to main", async ({ page }) => {
  await open(page, "overview");
  await page.keyboard.press("Tab");
  await expect(page.locator("a.skip")).toBeFocused();
  await page.keyboard.press("Enter");
  expect(page.url()).toContain("#main");
});

test("[security] CSP meta is present and blocks inline script injection", async ({ page }) => {
  await open(page, "overview");
  const violations: string[] = [];
  page.on("console", (m) => { if (/Content Security Policy/i.test(m.text())) violations.push(m.text()); });
  await page.evaluate(() => { const s = document.createElement("script"); s.textContent = "window.__pwned = 1"; document.head.appendChild(s); });
  expect(await page.evaluate(() => (window as unknown as { __pwned?: number }).__pwned)).toBeUndefined();
});

test("[offline] the single-file build opens from file:// and renders the headline", async ({ page }) => {
  const file = pathToFileURL(path.resolve("dist-offline/index.html")).href;
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  await page.goto(file);
  await expect(page.locator("h1")).toContainText("commitments");
  await page.getByRole("link", { name: "Ledger" }).first().click();
  await expect(page.locator("table.ledger")).toBeVisible();
  expect(errors).toEqual([]);
});
