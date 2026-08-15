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

test("runs the Python console with live metrics and order preview", async ({
  page,
}) => {
  await page.goto("http://127.0.0.1:8012");
  await expect(page.locator("wa-card")).toBeVisible();
  const sessions = page.locator(".metrics article").first().locator("strong");
  const initial = await sessions.textContent();
  await expect
    .poll(() => sessions.textContent(), { timeout: 5_000 })
    .not.toBe(initial);

  await page.getByText("Order controls", { exact: true }).click();
  await page.getByRole("textbox", { name: "Symbol" }).fill("MSFT");
  await page.getByRole("spinbutton", { name: "Quantity" }).fill("25");
  await page.getByRole("button", { name: "Preview order" }).click();
  await expect(page.locator("#order-preview")).toContainText(
    "Previewed 25 MSFT shares",
  );
});
