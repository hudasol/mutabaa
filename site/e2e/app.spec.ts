import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { pathToFileURL } from "node:url";
import path from "node:path";

const PAGES = ["overview", "ledger", "clocks", "lab", "maturity", "sources", "brief", "method", "assurance", "portfolio", "mine"];

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

test("[workflow] an uploaded CSV is kept when moving between pages and shown in the portfolio", async ({ page }) => {
  await page.goto("/#/lab");
  await page.getByRole("button", { name: "My CSV" }).first().click();
  const csv = "id,entity,sector,kind,audience,annual_transactions,maturity,oversight,audit_trail,uae_residency,fallback\n" +
    "a1,Alpha,Health,service,citizen,100,4,true,true,true,true\n" +
    "a2,Alpha,Health,service,citizen,100,2,true,true,true,true\n" +
    "b1,Beta,Health,service,citizen,100,3,true,true,true,true\n";
  await page.locator('input[type="file"]').setInputFiles({ name: "mine.csv", mimeType: "text/csv", buffer: Buffer.from(csv) });
  await expect(page.locator(".banner.yours")).toBeVisible();
  await page.getByRole("link", { name: "Portfolio" }).first().click();
  await expect(page.locator(".banner.yours")).toBeVisible();
  await expect(page.locator("table.heat tbody tr")).toHaveCount(2);
});

for (const [lang, label] of [["en", "Exploratory, not preregistered"], ["ar", "استكشافية، غير مسجّلة مسبقاً"]] as const) {
  test(`[honesty] the assurance page labels its analyses as exploratory (${lang})`, async ({ page }) => {
    await open(page, "assurance", { lang });
    await expect(page.getByRole("note").filter({ hasText: label })).toBeVisible();
  });
}

test("[honesty] the portfolio states how many rank moves exceed sampling noise", async ({ page }) => {
  await open(page, "portfolio");
  await expect(page.getByText(/Sampling noise check \(preregistered experiment E3\)/)).toBeVisible();
  await open(page, "assurance");
  await expect(page.getByText(/Wilson 95% interval/)).toBeVisible();
});

const MY_CSV = [
  "id,title,owner,metric,unit,target_number,deadline,measurement_source,undefined_terms,kind",
  "X01,Half of services on the new platform,Example Office,services moved,services,50,2027-12-31,Annual report,agentic,target",
  "X02,A new national gateway,,,,,within two years,,,deliverable",
  "X03,=HYPERLINK(1),,,,,,,,target",
].join("\n");

async function loadMine(page: Page, lang: "en" | "ar", theme: "light" | "dark") {
  await open(page, "mine", { lang, theme });
  await page.locator('input[type="file"]').setInputFiles({ name: "mine.csv", mimeType: "text/csv", buffer: Buffer.from(MY_CSV) });
}

test("[mine] a user file is scored in the browser, with questions and a persistent banner", async ({ page }) => {
  const external: string[] = [];
  page.on("request", (r) => { if (!r.url().startsWith("http://localhost:4181") && !r.url().startsWith("data:") && !r.url().startsWith("blob:")) external.push(r.url()); });
  await loadMine(page, "en", "light");
  await expect(page.getByRole("note").filter({ hasText: "Your file. Processed in this browser. Nothing is uploaded." })).toBeVisible();
  await expect(page.getByText("3 commitments scored.")).toBeVisible();
  await expect(page.getByRole("cell", { name: "X02" })).toBeVisible();
  await page.locator("details.qblock", { hasText: "X02" }).locator("summary").click();
  await expect(page.getByText(/By what calendar date must “A new national gateway” be met/)).toBeVisible();
  const dl = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export questions (CSV)" }).click();
  const text = await (await dl).createReadStream().then(async (s) => { let b = ""; for await (const c of s) b += c; return b; });
  expect(text).toContain(`"'=HYPERLINK(1)"`);
  expect(external).toEqual([]);
});

test("[mine] Arabic questions and right to left layout", async ({ page }) => {
  await loadMine(page, "ar", "light");
  await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
  const block = page.locator("details.qblock", { hasText: "X02" });
  await block.locator("summary").click();
  await expect(block.getByText(/في أي تاريخ ميلادي يجب تحقيق/)).toBeVisible();
});

test("[mine] a malformed file shows an error, not a crash", async ({ page }) => {
  await open(page, "mine");
  await page.locator('input[type="file"]').setInputFiles({ name: "bad.json", mimeType: "application/json", buffer: Buffer.from("[{oops") });
  await expect(page.getByRole("alert")).toContainText("not valid JSON");
});

for (const theme of ["light", "dark"] as const) {
  for (const lang of ["en", "ar"] as const) {
    test(`[mine] ${lang} ${theme} with results: no serious or critical axe violations`, async ({ page }) => {
      await loadMine(page, lang, theme);
      await page.locator("details.qblock").first().locator("summary").click();
      const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
      const bad = r.violations.filter((v) => v.impact === "serious" || v.impact === "critical");
      expect(bad.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(" ")).slice(0, 3).join(" | ")}`)).toEqual([]);
    });
  }
}

for (const p of ["overview", "lab"]) {
  test(`[a11y] the strip chart on ${p} has a table alternative with every definition`, async ({ page }) => {
    await open(page, p);
    await page.locator("details.strip-table summary").click();
    await expect(page.locator("details.strip-table tbody tr")).toHaveCount(72);
  });
}

test("[i18n] synthetic entity names follow the reader's language", async ({ page }) => {
  await open(page, "portfolio", { lang: "ar" });
  await expect(page.locator(".ename").first()).toContainText("اصطناعية");
});

for (const lang of ["en", "ar"] as const) {
  for (const p of ["overview", "lab", "portfolio", "maturity", "assurance", "brief"]) {
    test(`[honesty] ${p} labels its synthetic data (${lang})`, async ({ page }) => {
      await open(page, p, { lang });
      await expect(page.locator(".badge.synthetic, .banner.synthetic").first()).toBeVisible();
    });
  }
}

test("[honesty] the prototype and no endorsement statement is shown on a phone and in print", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 800 });
  await open(page, "brief");
  const foot = page.locator("footer.pagefoot");
  await expect(foot).toContainText("Not an official product of any government entity");
  await foot.scrollIntoViewIfNeeded();
  await expect(foot).toBeVisible();
  await page.emulateMedia({ media: "print" });
  await expect(foot).toBeVisible();
});

test("[robustness] an unknown stored language or theme falls back instead of crashing", async ({ page }) => {
  await page.addInitScript(() => { localStorage.setItem("lang", "xx"); localStorage.setItem("theme", "neon"); });
  await page.goto("/#/overview");
  await expect(page.locator("h1")).toBeVisible();
});

test("[print] the brief prints dark text on white even when the dark theme is chosen", async ({ page }) => {
  await open(page, "brief", { theme: "dark" });
  await page.emulateMedia({ media: "print" });
  const colours = await page.evaluate(() => {
    const cs = getComputedStyle(document.documentElement);
    return { paper: cs.getPropertyValue("--paper").trim(), ink: cs.getPropertyValue("--ink").trim() };
  });
  expect(colours).toEqual({ paper: "#fff", ink: "#000" });
});
