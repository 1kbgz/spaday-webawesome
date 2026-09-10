import { expect, test } from "@playwright/test";

/* A downstream component library on the same page as spaday-webawesome's generated catalog.
 *
 * The library imports WebAwesome by its bare specifiers, which the page's import map resolves to
 * spaday-webawesome's copy, and binds from Python through spaday's package surface. These check the
 * whole arrangement in a browser: one catalog, two libraries, wired together by spaday's own state.
 * See spaday_webawesome/tests/integration.py.
 */

const PAGE = "http://127.0.0.1:8017";

test("the downstream component renders out of WebAwesome's own elements", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto(PAGE);

  const metric = page.locator("#metric");
  await expect(metric.locator("wa-card")).toBeAttached();
  await expect(metric.locator(".demo-metric-label")).toHaveText("Fill rate");
  await expect(metric.locator(".demo-metric-value")).toHaveText("98.6%");
  // the composed WebAwesome elements really upgraded, rather than sitting inert
  expect(
    await metric
      .locator("wa-card")
      .evaluate(
        (el) => !!el.shadowRoot && el.constructor.name !== "HTMLElement",
      ),
  ).toBe(true);
  // a second copy of the catalog would have thrown from customElements.define
  expect(errors).toEqual([]);
});

test("one catalog serves both libraries", async ({ page }) => {
  await page.goto(PAGE);
  await expect(page.locator("#metric wa-card")).toBeAttached();
  const r = await page.evaluate(() => {
    const first = document.querySelector("#first-party wa-button");
    const downstream = document.querySelector("#metric wa-button");
    return {
      // the first-party tree and the downstream component resolve to the same class
      sameClass: first.constructor === downstream.constructor,
      registered: customElements.get("wa-button") === first.constructor,
      version: globalThis.__spadayWebawesome?.version,
    };
  });
  expect(r.sameClass).toBe(true);
  expect(r.registered).toBe(true);
  expect(r.version).toMatch(/^\d+\.\d+\.\d+/);
});

test("spaday state wires the two libraries together", async ({ page }) => {
  await page.goto(PAGE);
  const metric = page.locator("#metric");
  await expect(metric).toHaveAttribute("data-tone", "neutral");

  // a first-party WaButton drives a store field a downstream prop is bound to
  await page.locator("#to-success").click();
  await expect(metric).toHaveAttribute("data-tone", "success");
  await expect(metric.locator(".demo-metric-badge")).toHaveText("success");
  // and a first-party component reading the same field agrees
  await expect(page.locator("#echo")).toContainText("success");

  await page.locator("#to-danger").click();
  await expect(metric).toHaveAttribute("data-tone", "danger");
  await expect(page.locator("#echo")).toContainText("danger");
});

test("the downstream element's events reach the page", async ({ page }) => {
  await page.goto(PAGE);
  await expect(page.locator("#metric wa-button")).toBeAttached();
  const detail = page.evaluate(
    () =>
      new Promise((resolve) =>
        document.addEventListener(
          "demo-metric-details",
          (event) => resolve(event.detail),
          { once: true },
        ),
      ),
  );
  await page.locator("#metric wa-button").click();
  expect(await detail).toEqual({ label: "Fill rate", value: "98.6%" });
});

test("the downstream bundle satisfies the Python surface it is bound to", async ({
  page,
}) => {
  await page.goto(PAGE);
  const script = await (
    await page.request.get(`${PAGE}/conformance.js`)
  ).text();
  await expect(page.locator("#metric wa-card")).toBeAttached();
  expect(await page.evaluate(script)).toEqual([]);
});

test("the package's own bundle satisfies its generated catalog", async ({
  page,
}) => {
  // a substitute bundle asserts an empty result against this catalog, which it can only do if the
  // bundle the catalog was generated for does too
  await page.goto(PAGE);
  const script = await (
    await page.request.get(`${PAGE}/conformance-webawesome.js`)
  ).text();
  await expect(page.locator("#to-success")).toBeAttached();
  expect(await page.evaluate(script)).toEqual([]);
});
