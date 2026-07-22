import { test, expect } from "@playwright/test";

test.describe("Browse Laws page", () => {
  test("loads and shows page heading", async ({ page }) => {
    await page.goto("/laws");
    await expect(page.getByText("Browse Laws").first()).toBeVisible({ timeout: 5_000 });
  });

  test("shows category dropdown and sort controls", async ({ page }) => {
    await page.goto("/laws");
    const selects = page.locator("select");
    await expect(selects.first()).toBeVisible({ timeout: 5_000 });
    const count = await selects.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });
});
