import { defineConfig } from "@playwright/test";

// Local runs can point at a preinstalled Chromium: PW_CHROMIUM=/opt/pw-browsers/chromium
const exe = process.env.PW_CHROMIUM;
export default defineConfig({
  testDir: "e2e",
  timeout: 30_000,
  fullyParallel: true,
  reporter: [["list"]],
  use: { baseURL: "http://localhost:4181", launchOptions: exe ? { executablePath: exe } : {} },
  webServer: { command: "npm run build && npx vite preview --port 4181 --strictPort", port: 4181, reuseExistingServer: !process.env.CI, timeout: 120_000 },
});
