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
  await page.getByRole("combobox", { name: "Symbol" }).fill("MSFT");
  await expect(
    page
      .locator("#symbol-input")
      .getByText("MSFT · Microsoft", { exact: true }),
  ).toBeVisible();
  await page.getByRole("spinbutton", { name: "Quantity" }).fill("25");
  await page.getByRole("button", { name: "Preview order" }).click();
  await expect(page.locator("#order-preview")).toContainText(
    "Previewed 25 MSFT shares",
  );
});

test("renders reactive tree items as direct Web Awesome children", async ({
  page,
}) => {
  await page.goto("http://127.0.0.1:8013");
  const tree = page.locator("#reactive-tree");
  const root = tree.locator(":scope > wa-tree-item");
  const nested = root.locator(":scope > wa-tree-item");

  await expect(root).toHaveCount(1);
  await expect(nested).toHaveCount(2);
  await expect(root).toHaveJSProperty("isLeaf", false);
  await expect(nested.first()).toHaveAttribute("slot", "children");
  await expect(root).toHaveJSProperty("expanded", true);
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

test("the Python gallery renders horizontal and vertical radio groups", async ({
  page,
}) => {
  await page.goto("http://127.0.0.1:8013");
  const group = page
    .locator("wa-radio-group")
    .filter({ has: page.locator('wa-radio[value="starter"]') });
  await expect(group).toHaveJSProperty("orientation", "horizontal");
  const radios = group.locator("wa-radio");
  const first = await radios.first().boundingBox();
  const second = await radios.nth(1).boundingBox();
  expect(second.x).toBeGreaterThan(first.x + first.width - 1);
  expect(second.y).toBeCloseTo(first.y, 0);
  await group.evaluate((group) => {
    group.orientation = "vertical";
  });
  await expect
    .poll(async () => (await radios.nth(1).boundingBox()).y)
    .toBeGreaterThan(first.y + first.height - 1);
});

test("server suggestions can fill the symbol while custom values remain editable", async ({
  page,
}) => {
  await page.goto("http://127.0.0.1:8012");
  await page.getByText("Order controls", { exact: true }).click();
  const input = page.getByRole("combobox", { name: "Symbol" });
  await input.fill("ms");
  await page
    .getByRole("option", { name: "MSFT · Microsoft", exact: true })
    .click();
  await expect(input).toHaveValue("MSFT");
  await expect(page.getByRole("option")).toHaveCount(0);
  await input.fill("CUSTOM");
  await expect(page.locator("#symbol-input").getByRole("status")).toHaveText(
    "No matching suggestions.",
  );
  await expect(input).toHaveValue("CUSTOM");
  await page.getByRole("button", { name: "Preview order" }).click();
  await expect(page.locator("#order-preview")).toContainText("CUSTOM shares");
  await input.fill("");
  await expect(input).toHaveAttribute("aria-expanded", "false");
  await expect(page.getByRole("option")).toHaveCount(0);
});

test("a late suggestion response cannot replace newer results", async ({
  page,
}) => {
  let release;
  let held;
  const blocked = new Promise((resolve) => {
    held = resolve;
  });
  const wait = new Promise((resolve) => {
    release = resolve;
  });
  let finished;
  const done = new Promise((resolve) => {
    finished = resolve;
  });
  await page.route("**/api/symbols/suggestions", async (route) => {
    if (route.request().postDataJSON().query !== "A") return route.continue();
    const response = await route.fetch();
    held();
    await wait;
    await route.fulfill({ response }).catch(() => {});
    finished();
  });
  await page.goto("http://127.0.0.1:8012");
  await page.getByText("Order controls", { exact: true }).click();
  const input = page.getByRole("combobox", { name: "Symbol" });
  await input.fill("A");
  await blocked;
  await input.fill("MS");
  await expect(
    page.getByRole("option", { name: "MSFT · Microsoft", exact: true }),
  ).toBeVisible();
  release();
  await done;
  await expect(page.getByRole("option")).toHaveCount(1);
  await expect(page.getByRole("option")).toHaveText("MSFT · Microsoft");
});
