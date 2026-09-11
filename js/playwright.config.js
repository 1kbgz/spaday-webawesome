import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ["line"],
    ["html", { outputFile: "playwright-report/index.html", open: "never" }],
    ["junit", { outputFile: "junit.xml" }],
  ],
  use: {
    baseURL: "http://127.0.0.1:3000",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: [
    {
      command: "pnpm run start:tests",
      url: "http://127.0.0.1:3000",
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
    {
      // spaday's generic-control conformance page, rendered with this package's design
      command: "python -m spaday.ui.conformance 8029 --package webawesome",
      url: "http://127.0.0.1:8029",
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
    {
      command: "python -m spaday_webawesome.example",
      url: "http://127.0.0.1:8012",
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
    {
      // a downstream component library sharing the page with the generated catalog;
      // by path, not `-m`, because the tests directory is not an importable package
      command: "python ../spaday_webawesome/tests/integration.py",
      url: "http://127.0.0.1:8017",
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
  ],
});
