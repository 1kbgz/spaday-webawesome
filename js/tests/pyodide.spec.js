import fs from "fs";
import { expect, test } from "@playwright/test";

const built = fs.existsSync("dist/lite/index.html");

test("runs the complete example in Pyodide", async ({ page }) => {
  test.skip(!built, "run `make pyodide-example` first");
  test.setTimeout(180_000);

  await page.goto("/dist/lite/index.html");
  await page.waitForFunction(
    () =>
      document.documentElement.dataset.ready === "true" ||
      document.querySelector("#pyodide-status")?.textContent ===
        "Unable to start",
    undefined,
    { timeout: 150_000 },
  );
  await expect(page.locator("html")).toHaveAttribute("data-ready", "true");
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
