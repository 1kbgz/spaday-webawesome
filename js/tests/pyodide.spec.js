import fs from "fs";
import { expect, test } from "@playwright/test";

const built = fs.existsSync("dist/lite/index.html");

async function renderedComponentTags(page, prefix, structuralTags = []) {
  return page.locator("body").evaluate(
    (body, { prefix, structuralTags }) => {
      const components = [...body.querySelectorAll("*")].filter((element) =>
        element.localName.startsWith(prefix),
      );
      const tags = [...new Set(components.map((element) => element.localName))];
      const structural = new Set(structuralTags);
      const unrendered = tags.filter(
        (tag) =>
          !structural.has(tag) &&
          !components
            .filter((element) => element.localName === tag)
            .some((element) => {
              const bounds = element.getBoundingClientRect();
              return bounds.width > 0 && bounds.height > 0;
            }),
      );
      return { count: tags.length, unrendered };
    },
    { prefix, structuralTags },
  );
}

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

test("runs the component gallery in Pyodide", async ({ page }) => {
  test.skip(!built, "run `make pyodide-example` first");
  test.setTimeout(180_000);

  await page.goto("/dist/lite/?example=gallery");
  await page.waitForFunction(
    () =>
      document.documentElement.dataset.ready === "true" ||
      document.querySelector("#pyodide-status")?.textContent ===
        "Unable to start",
    undefined,
    { timeout: 150_000 },
  );
  await expect(page.locator("html")).toHaveAttribute("data-ready", "true");
  await expect(page.locator("h1")).toHaveText("Component gallery");
  expect(await page.locator("wa-card.gallery-card").count()).toBeGreaterThan(
    40,
  );
  await expect(page.locator("wa-zoomable-frame")).toBeVisible();
  const rendered = await renderedComponentTags(page, "wa-", [
    "wa-animation",
    "wa-dropdown",
    "wa-dropdown-item",
    "wa-intersection-observer",
    "wa-markdown",
    "wa-mutation-observer",
    "wa-option",
    "wa-pagination",
    "wa-popover",
    "wa-popup",
    "wa-random-content",
    "wa-resize-observer",
    "wa-dialog",
    "wa-drawer",
    "wa-tab-panel",
    "wa-tooltip",
  ]);
  expect(rendered.count).toBe(70);
  expect(rendered.unrendered).toEqual([]);
  await page.getByRole("button", { name: "Open dialog" }).click();
  await expect(page.locator("#saved-dialog")).toHaveJSProperty("open", true);
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Open drawer" }).click();
  await expect(page.locator("#gallery-drawer")).toHaveJSProperty("open", true);
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Profile" }).click();
  await expect(page.locator("wa-popover")).toBeVisible();
  await page.locator("#gallery-tooltip-trigger").hover();
  await expect(
    page.locator("wa-tooltip", { hasText: "Contextual help" }),
  ).toHaveJSProperty("open", true);
  await expect(page.locator(".token-keyword").first()).toHaveText("from");
});
