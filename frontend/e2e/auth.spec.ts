import { test, expect } from "@playwright/test";

const TEST_USER = { email: "lawyer@test.com", password: "Test1234!" };

test.describe("Login", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
  });

  test("renders login form", async ({ page }) => {
    await expect(page.getByPlaceholder("you@example.com")).toBeVisible();
    await expect(page.getByPlaceholder("Enter your password")).toBeVisible();
    await expect(page.getByRole("button", { name: /sign in/i })).toBeVisible();
  });

  test("logs in successfully and redirects to dashboard", async ({ page }) => {
    await page.getByPlaceholder("you@example.com").fill(TEST_USER.email);
    await page.getByPlaceholder("Enter your password").fill(TEST_USER.password);
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10_000 });
  });

  test("shows error on invalid credentials", async ({ page }) => {
    await page.getByPlaceholder("you@example.com").fill("wrong@test.com");
    await page.getByPlaceholder("Enter your password").fill("WrongPass123!");
    await page.getByRole("button", { name: /sign in/i }).click();
    const errorText = page.getByText(/invalid|incorrect|wrong|error/i).first();
    await expect(errorText).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Register page", () => {
  test("renders register form", async ({ page }) => {
    await page.goto("/register");
    await expect(page.getByRole("button", { name: /continue/i })).toBeVisible();
  });
});
