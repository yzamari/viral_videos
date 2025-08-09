import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should display login page', async ({ page }) => {
    await expect(page).toHaveTitle(/ViralAI/);
    await expect(page.locator('h4')).toContainText('Sign In');
    await expect(page.locator('input[name="username"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show validation errors for empty fields', async ({ page }) => {
    await page.locator('button[type="submit"]').click();
    await expect(page.locator('text=Username is required')).toBeVisible();
    await expect(page.locator('text=Password is required')).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    // Fill login form
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass123');
    
    // Click login button
    await page.locator('button[type="submit"]').click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h4')).toContainText('Dashboard');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.fill('input[name="username"]', 'wronguser');
    await page.fill('input[name="password"]', 'wrongpass');
    await page.locator('button[type="submit"]').click();
    
    await expect(page.locator('.MuiAlert-root')).toContainText('Invalid credentials');
  });

  test('should register new user', async ({ page }) => {
    // Navigate to register
    await page.locator('text=Create Account').click();
    
    // Fill registration form
    await page.fill('input[name="username"]', `user_${Date.now()}`);
    await page.fill('input[name="email"]', `test_${Date.now()}@example.com`);
    await page.fill('input[name="password"]', 'SecurePass123!');
    await page.fill('input[name="confirmPassword"]', 'SecurePass123!');
    await page.fill('input[name="organization"]', 'Test Org');
    
    // Submit
    await page.locator('button[type="submit"]').click();
    
    // Should redirect to dashboard after successful registration
    await expect(page).toHaveURL('/dashboard');
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass123');
    await page.locator('button[type="submit"]').click();
    
    await page.waitForURL('/dashboard');
    
    // Click user menu
    await page.locator('[data-testid="user-menu"]').click();
    
    // Click logout
    await page.locator('text=Logout').click();
    
    // Should redirect to login
    await expect(page).toHaveURL('/login');
  });

  test('should persist authentication on refresh', async ({ page }) => {
    // Login
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass123');
    await page.locator('button[type="submit"]').click();
    
    await page.waitForURL('/dashboard');
    
    // Refresh page
    await page.reload();
    
    // Should still be on dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h4')).toContainText('Dashboard');
  });
});