import { test, expect } from '@playwright/test';

test.describe('Simple E2E Test', () => {
  test('should load the application', async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check if the app title is visible
    await expect(page).toHaveTitle(/Viral/i);
    
    console.log('✅ Application loaded successfully');
  });

  test('should show login form', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Look for login elements
    const loginButton = page.locator('button:has-text("Login"), button:has-text("Sign In")').first();
    
    if (await loginButton.isVisible()) {
      console.log('✅ Login button found');
      await loginButton.click();
    }
    
    // Check for username/email field
    const usernameField = page.locator('input[type="text"], input[type="email"], input[name="username"], input[name="email"]').first();
    if (await usernameField.isVisible()) {
      console.log('✅ Username field found');
    }
  });
});