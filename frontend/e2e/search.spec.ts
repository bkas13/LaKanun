import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => localStorage.setItem("welcome_seen", "1"));
  await page.reload();
  await page.waitForLoadState("networkidle");
});

test.describe("Search (Laws mode)", () => {
  test("opens search modal via / shortcut and searches", async ({ page }) => {
    await page.keyboard.press("/");
    const input = page.locator(".fixed input").first();
    await expect(input).toBeVisible({ timeout: 5_000 });
    await input.fill("murder");
    await input.press("Enter");
    await expect(page).toHaveURL(/\/laws\?q=/, { timeout: 10_000 });
  });
});

test.describe("Search (Issues mode)", () => {
  test("switches to issues mode and searches", async ({ page }) => {
    await page.keyboard.press("/");
    const input = page.locator(".fixed input").first();
    await expect(input).toBeVisible({ timeout: 5_000 });

    const issuesBtn = page.locator(".fixed .bg-white\\/10 button").nth(1);
    await issuesBtn.click();

    await input.fill("domestic violence");
    await input.press("Enter");
    await expect(page).toHaveURL(/\/issues\?q=/, { timeout: 10_000 });
  });
});

test.describe("Laws page with query", () => {
  test("loads results from URL query", async ({ page }) => {
    await page.goto("/laws?q=murder");
    await page.waitForTimeout(5000);
    const heading = page.getByText("Showing results for").or(page.getByText("Query")).first();
    await expect(heading).toBeVisible({ timeout: 10_000 });
  });
});
