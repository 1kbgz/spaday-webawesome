import { expect, test } from "@playwright/test";

test("registers and renders the full WebAwesome catalog", async ({ page }) => {
  await page.goto("/dist/index.html");
  await page.evaluate(() => {
    const button = document.createElement("wa-button");
    button.textContent = "Run";
    document.body.appendChild(button);
  });

  await expect(page.locator("wa-button")).toHaveText("Run");
  await expect
    .poll(() =>
      page.locator("wa-button").evaluate((button) => !!button.shadowRoot),
    )
    .toBe(true);
  expect(
    await page.evaluate(() => !!customElements.get("wa-zoomable-frame")),
  ).toBe(true);
});
