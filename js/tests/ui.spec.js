import { expect, test } from "@playwright/test";

/* spaday's generic-control conformance page (spaday.ui.conformance) rendered with WebAwesome's
 * design, served on 8029 by playwright.config.js. The checks mirror spaday's own against the native
 * baseline, so the two render the same behavior.
 */

const PAGE = "http://127.0.0.1:8029";

// a control's text input: the input WebAwesome's element wraps
const input = (page, id) => page.locator(`#${id} input`).last();

test("renders the controls as WebAwesome elements", async ({ page }) => {
  await page.goto(PAGE);
  await page.locator("#dialog").waitFor({ state: "attached" });
  expect(
    await page.evaluate(() =>
      ["save", "name", "agree", "dark", "plan", "dialog"].map(
        (id) => document.getElementById(id).localName,
      ),
    ),
  ).toEqual([
    "wa-button",
    "wa-input",
    "wa-checkbox",
    "wa-switch",
    "wa-select",
    "wa-dialog",
  ]);
  expect(await page.locator("[data-ui-fallback]").count()).toBe(0);
});

test("every control round-trips through the store", async ({ page }) => {
  await page.goto(PAGE);
  const state = page.locator("#state");
  await expect(state).toHaveText("|false|false|basic|false|false");
  await input(page, "name").fill("Ada");
  await expect(state).toHaveText("Ada|false|false|basic|false|false");
  await page.locator("#agree").click();
  await page.locator("#dark").click();
  await expect(state).toHaveText("Ada|true|true|basic|false|false");
  await page.locator("#save").click();
  await expect(state).toHaveText("Ada|true|true|basic|true|false");
  await page.locator("#reset").click();
  await expect(state).toHaveText("|true|true|basic|false|false");
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
    "|false|false|basic|false|false",
  );
});

test("labels, help, errors and disabled state render", async ({ page }) => {
  await page.goto(PAGE);
  await expect(page.getByText("Your name")).toBeVisible();
  await expect(page.getByText("Required")).toBeVisible();
  await expect(page.locator("#never")).toHaveJSProperty("disabled", true);
  await expect(page.locator("#save")).toHaveText("Save");
  await expect(page.locator("#save")).toHaveAttribute("variant", "brand");
});
