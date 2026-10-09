// Offline build: one HTML file with script, styles and fonts inlined. Opens from file:// or a USB stick.
// The page CSP is rewritten to allow exactly the inline blocks present (by SHA-256), nothing else.
import { createHash } from "node:crypto";
import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";

const sri = (s: string) => `'sha256-${createHash("sha256").update(s).digest("base64")}'`;

function inlineEverything(): Plugin {
  return {
    name: "inline-everything",
    enforce: "post",
    generateBundle(_o, bundle) {
      const htmlFile = Object.values(bundle).find((f) => f.fileName === "index.html");
      if (!htmlFile || htmlFile.type !== "asset") throw new Error("index.html not found");
      let html = String(htmlFile.source);
      const js: string[] = [], css: string[] = [];
      for (const [name, f] of Object.entries(bundle)) {
        if (f.type === "chunk" && f.isEntry) {
          html = html.replace(new RegExp(`<script[^>]*src="[^"]*${name.split("/").pop()}"[^>]*></script>`), "");
          js.push(f.code); delete bundle[name];
        } else if (f.type === "asset" && name.endsWith(".css")) {
          html = html.replace(new RegExp(`<link[^>]*href="[^"]*${name.split("/").pop()}"[^>]*>`), "");
          css.push(String(f.source)); delete bundle[name];
        }
      }
      const style = css.join("\n"), script = js.join("\n").replace(/<\/script/gi, "<\\/script");
      html = html.replace("</head>", () => `<style>${style}</style></head>`)
        .replace("</body>", () => `<script type="module">${script}</script></body>`);
      const csp = [
        "default-src 'none'", `script-src ${sri(script)}`, `style-src ${sri(style)}`, "style-src-attr 'unsafe-inline'",
        "font-src data:", "img-src data: blob:", "base-uri 'none'", "form-action 'none'",
      ].join("; ");
      htmlFile.source = html.replace(/(<meta http-equiv="Content-Security-Policy" content=")[^"]*(")/, `$1${csp}$2`);
    },
  };
}

export default defineConfig({
  plugins: [react(), inlineEverything()],
  base: "./",
  build: { outDir: "dist-offline", assetsInlineLimit: 100_000_000, cssCodeSplit: false, modulePreload: false },
});
