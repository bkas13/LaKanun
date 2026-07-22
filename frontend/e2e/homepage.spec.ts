import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => localStorage.setItem("welcome_seen", "1"));
  await page.reload();
  await page.waitForLoadState("networkidle");
});

test.describe("Homepage", () => {
  test("loads and shows branding", async ({ page }) => {
    await expect(page.locator("text=ल Kanun").first()).toBeVisible();
  });

  test("shows key navigation items", async ({ page }) => {
    const nav = page.locator("nav").first();
    await expect(nav).toBeVisible();
    await expect(nav.getByText("Browse Laws")).toBeVisible();
    await expect(nav.getByText("Know Your Rights")).toBeVisible();
  });

  test("search modal opens via / keyboard shortcut", async ({ page }) => {
    await page.keyboard.press("/");
    const searchInput = page.locator(".fixed input").first();
    await expect(searchInput).toBeVisible({ timeout: 5_000 });
  });
});
