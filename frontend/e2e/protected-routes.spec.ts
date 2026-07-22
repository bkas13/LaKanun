import { test, expect } from "@playwright/test";

test.describe("Protected routes", () => {
  test("dashboard redirects to login when not authenticated", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/, { timeout: 10_000 });
  });

  test("bookmarks redirects to login when not authenticated", async ({ page }) => {
    await page.goto("/dashboard/bookmarks");
    await expect(page).toHaveURL(/\/login/, { timeout: 10_000 });
  });

  test("admin redirects to login when not authenticated", async ({ page }) => {
    await page.goto("/admin");
    await expect(page).toHaveURL(/\/login/, { timeout: 10_000 });
  });
});

test.describe("Authenticated access", () => {
  test("can access dashboard after login", async ({ page }) => {
    await page.goto("/login");
    await page.getByPlaceholder("you@example.com").fill("lawyer@test.com");
    await page.getByPlaceholder("Enter your password").fill("Test1234!");
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10_000 });

    await page.goto("/dashboard/bookmarks");
    await expect(page).not.toHaveURL(/\/login/, { timeout: 5_000 });
  });
});
