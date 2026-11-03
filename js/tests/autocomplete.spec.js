import { expect, test } from "@playwright/test";

async function mount(page, props = {}) {
  await page.goto("/dist/index.html");
  await page.evaluate(async (props) => {
    await customElements.whenDefined("spaday-wa-autocomplete");
    const form = document.createElement("form");
    const control = document.createElement("spaday-wa-autocomplete");
    Object.assign(control, {
      label: "Symbol",
      name: "symbol",
      suggestionsUrl: "/suggestions",
      ...props,
    });
    form.append(control);
    const next = document.createElement("input");
    next.setAttribute("aria-label", "Next field");
    form.append(next);
    const button = document.createElement("button");
    button.textContent = "Submit";
    form.append(button);
    document.body.append(form);
    window.submissions = 0;
    window.changes = [];
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      window.submissions++;
    });
    control.addEventListener("change", () =>
      window.changes.push(control.value),
    );
    await control.updateComplete;
  }, props);
  return page.getByRole("combobox", { name: "Symbol" });
}

const options = [
  { value: "MSFT", label: "MSFT · Microsoft" },
  { value: "META", label: "META · Meta" },
];

async function suggestions(page) {
  await page.route("**/suggestions", (route) =>
    route.fulfill({ json: options }),
  );
}

test("keyboard selection retains focus, updates form data, and does not submit", async ({
  page,
}) => {
  await suggestions(page);
  const input = await mount(page);
  const control = page.locator("spaday-wa-autocomplete");
  const before = await control.boundingBox();
  await input.fill("M");
  await expect(page.getByRole("option")).toHaveCount(2);
  await expect(input).toHaveAttribute("aria-expanded", "true");
  expect((await control.boundingBox()).height).toBeCloseTo(before.height, 0);
  await expect
    .poll(async () => (await page.getByRole("listbox").boundingBox()).width)
    .toBeCloseTo(before.width, 0);
  await input.press("ArrowDown");
  await expect(input).toHaveAttribute("aria-activedescendant", "suggestion-0");
  await input.press("ArrowDown");
  await expect(page.getByRole("option").nth(1)).toHaveAttribute(
    "aria-selected",
    "true",
  );
  await input.press("Enter");
  await expect(input).toHaveValue("META");
  await expect(input).toBeFocused();
  await expect(input).toHaveAttribute("aria-expanded", "false");
  await expect(input).not.toHaveAttribute("aria-activedescendant");
  expect(
    await page.evaluate(() =>
      new FormData(document.querySelector("form")).get("symbol"),
    ),
  ).toBe("META");
  expect(await page.evaluate(() => window.submissions)).toBe(0);
  expect(await page.evaluate(() => window.changes)).toEqual(["META"]);
});

test("click selection, free text, Escape, Tab and reset use input semantics", async ({
  page,
}) => {
  await suggestions(page);
  const input = await mount(page, { defaultValue: "AAPL" });
  await input.fill("M");
  await page.getByRole("option", { name: "MSFT · Microsoft" }).click();
  await expect(input).toHaveValue("MSFT");
  await input.fill("CUSTOM");
  await expect(page.getByRole("option")).toHaveCount(2);
  await input.press("Escape");
  await expect(input).toHaveAttribute("aria-expanded", "false");
  await expect(input).toHaveValue("CUSTOM");
  await input.press("ArrowUp");
  await expect(input).toHaveAttribute("aria-activedescendant", "suggestion-1");
  await input.press("Tab");
  await expect(page.getByRole("textbox", { name: "Next field" })).toBeFocused();
  await expect(input).toHaveValue("CUSTOM");
  await page.getByRole("button", { name: "Submit" }).click();
  expect(await page.evaluate(() => window.submissions)).toBe(1);
  await page.evaluate(() => document.querySelector("form").reset());
  await expect(input).toHaveValue("AAPL");
});

test("strict mode rejects free text while preserving required and custom validation", async ({
  page,
}) => {
  await suggestions(page);
  const input = await mount(page, { allowCustom: false, required: true });
  const control = page.locator("spaday-wa-autocomplete");
  expect(await control.evaluate((element) => element.checkValidity())).toBe(
    false,
  );
  await input.fill("M");
  await expect(page.getByRole("option")).toHaveCount(2);
  expect(await control.evaluate((element) => element.checkValidity())).toBe(
    false,
  );
  await page.getByRole("option").first().click();
  expect(await control.evaluate((element) => element.checkValidity())).toBe(
    true,
  );
  await control.evaluate((element) =>
    element.setCustomValidity("Server rejected symbol"),
  );
  expect(await control.evaluate((element) => element.validationMessage)).toBe(
    "Server rejected symbol",
  );
  await input.fill("OTHER");
  expect(await control.evaluate((element) => element.checkValidity())).toBe(
    false,
  );
});

test("stale responses, Escape and disconnect cannot reopen suggestions", async ({
  page,
}) => {
  const pending = [];
  await page.route("**/suggestions", async (route) => {
    await new Promise((resolve) => pending.push({ route, resolve }));
  });
  const input = await mount(page);
  await input.fill("M");
  await expect.poll(() => pending.length).toBe(1);
  await input.fill("A");
  await expect.poll(() => pending.length).toBe(2);
  await pending[1].route.fulfill({ json: [{ value: "AAPL", label: "Apple" }] });
  pending[1].resolve();
  await expect(page.getByRole("option", { name: "Apple" })).toBeVisible();
  await pending[0].route.fulfill({ json: options });
  pending[0].resolve();
  await expect(page.getByRole("option")).toHaveCount(1);
  await input.fill("N");
  await expect.poll(() => pending.length).toBe(3);
  await input.press("Escape");
  await pending[2].route.fulfill({ json: options });
  pending[2].resolve();
  await expect(input).toHaveAttribute("aria-expanded", "false");
  await input.fill("D");
  await expect.poll(() => pending.length).toBe(4);
  await page.locator("spaday-wa-autocomplete").evaluate((element) => {
    window.detachedControl = element;
    element.remove();
  });
  await pending[3].route.fulfill({ json: options });
  pending[3].resolve();
  expect(
    await page.evaluate(() =>
      window.detachedControl.input.getAttribute("aria-expanded"),
    ),
  ).toBe("false");
});

for (const response of [{ status: 500 }, { json: { bad: true } }, { json: [] }])
  test(`empty/error response ${JSON.stringify(response)} clears stale options`, async ({
    page,
  }) => {
    await suggestions(page);
    const input = await mount(page);
    await input.fill("M");
    await expect(page.getByRole("option")).toHaveCount(2);
    await page.unroute("**/suggestions");
    await page.route("**/suggestions", (route) => route.fulfill(response));
    await input.fill("X");
    await expect(page.getByRole("status")).toHaveText(
      response.json instanceof Array
        ? "No matching suggestions."
        : "Suggestions unavailable.",
    );
    await expect(input).toHaveAttribute("aria-expanded", "false");
    expect(
      await page
        .locator("spaday-wa-autocomplete")
        .evaluate((element) => element.checkValidity()),
    ).toBe(true);
  });

test("programmatic edits, disabled and readonly fields cancel pending lookups", async ({
  page,
}) => {
  await suggestions(page);
  const input = await mount(page);
  const control = page.locator("spaday-wa-autocomplete");
  await input.fill("M");
  await expect(page.getByRole("option")).toHaveCount(2);
  await control.evaluate((element) => {
    element.value = "";
  });
  await expect(input).toHaveAttribute("aria-expanded", "false");
  await input.fill("M");
  await expect(page.getByRole("option")).toHaveCount(2);
  await control.evaluate((element) => {
    element.disabled = true;
  });
  await expect(input).toBeDisabled();
  await expect(input).toHaveAttribute("aria-expanded", "false");
  await control.evaluate((element) => {
    element.disabled = false;
    element.readonly = true;
  });
  await input.focus();
  await input.press("ArrowDown");
  await expect(input).toHaveAttribute("aria-expanded", "false");
  await expect(input).not.toBeEditable();
});

test("composition waits for committed text and suggestion labels render as text", async ({
  page,
}) => {
  const queries = [];
  await page.route("**/suggestions", (route) => {
    queries.push(route.request().postDataJSON().query);
    return route.fulfill({
      json: [{ value: "猫", label: "<img src=x onerror=alert(1)>" }],
    });
  });
  const input = await mount(page);
  await input.focus();
  await input.dispatchEvent("compositionstart", {
    bubbles: true,
    composed: true,
  });
  await input.fill("ね");
  // Longer than debounce: intermediate IME text must not reach the endpoint.
  await page.waitForTimeout(250);
  expect(queries).toEqual([]);
  await input.fill("猫");
  await input.dispatchEvent("compositionend", {
    bubbles: true,
    composed: true,
  });
  await expect(page.getByRole("option")).toHaveText(
    "<img src=x onerror=alert(1)>",
  );
  expect(queries).toEqual(["猫"]);
  expect(await page.locator("spaday-wa-autocomplete img").count()).toBe(0);
});
