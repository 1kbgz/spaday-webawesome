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

test("survives an application that already registered a WebAwesome element", async ({
  page,
}) => {
  // the fatal case: an app shipping its own copy of WebAwesome registers `wa-button` first. Without
  // the define-guard this bundle throws from `customElements.define` and registers nothing at all,
  // so the page renders zero components rather than one wrong one.
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.addInitScript(() => {
    customElements.define(
      "wa-button",
      class extends HTMLElement {
        connectedCallback() {
          this.dataset.theirs = "1";
        }
      },
    );
  });

  await page.goto("/dist/index.html");
  expect(errors).toEqual([]);
  // first registration wins, so `wa-button` stays theirs...
  expect(
    await page.evaluate(() => !!document.createElement("wa-button").shadowRoot),
  ).toBe(false);
  // ...but the rest of the catalog still registered, which is the difference between a degraded
  // page and a blank one
  expect(await page.evaluate(() => !!customElements.get("wa-card"))).toBe(true);
  expect(
    await page.evaluate(() => !!customElements.get("wa-zoomable-frame")),
  ).toBe(true);
});

test("publishes the WebAwesome version it bundles", async ({ page }) => {
  // a page holding a second copy can compare and refuse rather than half-work
  await page.goto("/dist/index.html");
  expect(
    await page.evaluate(() => globalThis.__spadayWebawesome?.version),
  ).toMatch(/^\d+\.\d+\.\d+/);
});

test("warns, naming what it serves, when another copy registered its elements first", async ({
  page,
}) => {
  // the page keeps the first registration, so the loser says which elements are not its own
  const warnings = [];
  page.on("console", (message) => {
    if (message.type() === "warning") warnings.push(message.text());
  });
  await page.addInitScript(() => {
    customElements.define("wa-button", class extends HTMLElement {});
  });
  await page.goto("/dist/index.html");
  await expect
    .poll(() => warnings.find((text) => text.includes("<wa-button>")))
    .toMatch(/ \d+\.\d+\.\d+\S*: another copy on the page already registered /);
  expect(warnings.find((text) => text.includes("<wa-button>"))).toContain(
    "@awesome.me/webawesome ",
  );
});
