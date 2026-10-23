import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests",
  workers: 1,
  retries: 0,
  timeout: 30000,
  use: {
    baseURL: "http://127.0.0.1:18787",
    headless: true,
    viewport: { width: 1560, height: 1080 },
    trace: "retain-on-failure",
  },
  webServer: {
    command: "node tests/server.mjs",
    url: "http://127.0.0.1:18787/api/bootstrap",
    reuseExistingServer: false,
    timeout: 15000,
  },
});
