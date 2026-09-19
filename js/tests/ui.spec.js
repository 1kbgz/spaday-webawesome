import { expect, test } from "@playwright/test";

/* spaday's generic-control conformance page (spaday.ui.conformance) rendered with WebAwesome's
 * design, served on 8029 by playwright.config.js. The checks mirror spaday's own against the native
 * baseline, so the two render the same behavior.
 */

const PAGE = "http://127.0.0.1:8029";

// text-like controls render their editable element inside WebAwesome's shadow root
const input = (page, id) => page.locator(`#${id} input`).last();
const textarea = (page, id) => page.locator(`#${id} textarea`).last();

test("renders the controls as WebAwesome elements", async ({ page }) => {
  await page.goto(PAGE);
  await page.locator("#dialog").waitFor({ state: "attached" });
  expect(
    await page.evaluate(() =>
      [
        "save",
        "name",
        "notes",
        "count",
        "date",
        "agree",
        "dark",
        "plan",
        "priority",
        "volume",
        "alert",
        "progress",
        "dialog",
      ].map((id) => document.getElementById(id).localName),
    ),
  ).toEqual([
    "wa-button",
    "wa-input",
    "wa-textarea",
    "wa-input",
    "wa-input",
    "wa-checkbox",
    "wa-switch",
    "wa-select",
    "wa-radio-group",
    "wa-slider",
    "wa-callout",
    "wa-progress-bar",
    "wa-dialog",
  ]);
  expect(await page.locator("[data-ui-fallback]").count()).toBe(0);
});

test("every control round-trips through the store", async ({ page }) => {
  await page.goto(PAGE);
  const state = page.locator("#state");
  await expect(state).toHaveText(
    "||2|2026-09-14|false|false|basic|1|5|25|false|false",
  );
  await input(page, "name").fill("Ada");
  await expect(state).toHaveText(
    "Ada||2|2026-09-14|false|false|basic|1|5|25|false|false",
  );
  await page.locator("#agree").click();
  await page.locator("#dark").click();
  await expect(state).toHaveText(
    "Ada||2|2026-09-14|true|true|basic|1|5|25|false|false",
  );
  await page.locator("#save").click();
  await expect(state).toHaveText(
    "Ada||2|2026-09-14|true|true|basic|1|5|25|true|false",
  );
  await page.locator("#reset").click();
  await expect(state).toHaveText(
    "||2|2026-09-14|true|true|basic|1|5|25|false|false",
  );
});

test("text, number, date, radio and slider values round-trip", async ({
  page,
}) => {
  await page.goto(PAGE);
  const state = page.locator("#state");
  await textarea(page, "notes").fill("Ready");
  await input(page, "count").fill("4");
  await input(page, "date").fill("2026-10-01");
  await page.getByRole("radio", { name: "High" }).click();
  await page.locator("#volume").evaluate((element) => {
    element.value = 8;
    element.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await expect(state).toHaveText(
    "|Ready|4|2026-10-01|false|false|basic|2|8|25|false|false",
  );
  await expect(page.locator("#alert")).toContainText("Portable");
  await expect(page.locator("#progress")).toHaveJSProperty("value", 50);
  await expect(
    page.getByRole("radiogroup", { name: "Priority" }),
  ).toBeVisible();
});

test("a select changes the bound field", async ({ page }) => {
  await page.goto(PAGE);
  await page.locator("#plan").click();
  await page.getByRole("option", { name: "Plus" }).click();
  await expect(page.locator("#state")).toContainText("|plus|");
});

test("the dialog opens from state, closes from a button and reports its own close", async ({
  page,
}) => {
  await page.goto(PAGE);
  const dialog = page.locator("#dialog");
  await expect(dialog).toHaveJSProperty("open", false);
  await page.locator("#open").click();
  await expect(dialog).toHaveJSProperty("open", true);
  await expect(dialog).toContainText("Confirm");
  await page.locator("#close").click();
  await expect(dialog).toHaveJSProperty("open", false);
  await page.locator("#open").click();
  await expect(dialog).toHaveJSProperty("open", true);
  await page.keyboard.press("Escape");
  await expect(dialog).toHaveJSProperty("open", false);
  await expect(page.locator("#state")).toHaveText(
    "||2|2026-09-14|false|false|basic|1|5|25|false|false",
  );
});

test("labels, help, errors and disabled state render", async ({ page }) => {
  await page.goto(PAGE);
  await expect(page.locator("#name")).toHaveJSProperty("hint", "Your name");
  await expect(page.getByText("Required")).toBeVisible();
  await expect(page.locator("#never")).toHaveJSProperty("disabled", true);
  await expect(page.locator("#save")).toHaveText("Save");
  await expect(page.locator("#save")).toHaveAttribute("variant", "brand");
});
