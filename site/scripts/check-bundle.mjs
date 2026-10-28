// Fails when the built site grows past its budget. Sizes are gzip bytes of what the browser downloads.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { gzipSync } from "node:zlib";
import { join } from "node:path";

const BUDGET = {
  entryJs: 110_000, // the script every visitor downloads first
  allJs: 135_000, // entry plus every lazily loaded page
  css: 6_000,
  offlineHtml: 600_000, // the single file build, fonts included
};

const gz = (p) => gzipSync(readFileSync(p)).length;
const assets = join("dist", "assets");
const js = readdirSync(assets).filter((f) => f.endsWith(".js"));
const css = readdirSync(assets).filter((f) => f.endsWith(".css"));
const sizes = {
  entryJs: gz(join(assets, js.find((f) => f.startsWith("index-")))),
  allJs: js.reduce((n, f) => n + gz(join(assets, f)), 0),
  css: css.reduce((n, f) => n + gz(join(assets, f)), 0),
};
try { statSync(join("dist-offline", "index.html")); sizes.offlineHtml = gz(join("dist-offline", "index.html")); } catch { /* offline build not present */ }

let failed = false;
for (const [k, limit] of Object.entries(BUDGET)) {
  if (sizes[k] === undefined) continue;
  const over = sizes[k] > limit;
  failed ||= over;
  console.log(`${over ? "FAIL" : "ok  "} ${k.padEnd(12)} ${String(sizes[k]).padStart(8)} / ${limit} bytes gzip`);
}
process.exit(failed ? 1 : 0);
