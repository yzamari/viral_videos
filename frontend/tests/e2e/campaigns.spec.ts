import { test, expect } from '@playwright/test';

test.describe('Campaign Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass123');
    await page.locator('button[type="submit"]').click();
    await page.waitForURL('/dashboard');
    
    // Navigate to campaigns
    await page.goto('/campaigns');
  });

  test('should display campaigns list', async ({ page }) => {
    await expect(page.locator('h4')).toContainText('Campaigns');
    await expect(page.locator('[data-testid="campaigns-table"]')).toBeVisible();
    await expect(page.locator('button:has-text("Create Campaign")')).toBeVisible();
  });

  test('should create new campaign', async ({ page }) => {
    // Click create campaign button
    await page.locator('button:has-text("Create Campaign")').click();
    await expect(page).toHaveURL('/campaigns/new');
    
    // Step 1: Basic Info
    await page.fill('input[name="name"]', 'Test Campaign ' + Date.now());
    await page.selectOption('select[name="objective"]', 'brand_awareness');
    await page.locator('button:has-text("Next")').click();
    
    // Step 2: Platforms
    await page.locator('input[value="youtube"]').check();
    await page.locator('input[value="tiktok"]').check();
    await page.locator('input[value="instagram"]').check();
    await page.locator('button:has-text("Next")').click();
    
    // Step 3: Budget
    await page.fill('input[name="totalBudget"]', '5000');
    await page.fill('input[name="dailyBudget"]', '200');
    await page.locator('button:has-text("Next")').click();
    
    // Step 4: Targeting
    await page.fill('input[name="ageMin"]', '18');
    await page.fill('input[name="ageMax"]', '35');
    await page.selectOption('select[name="gender"]', 'all');
    await page.fill('input[name="locations"]', 'United States, Canada');
    await page.fill('input[name="interests"]', 'Technology, Gaming, Entertainment');
    await page.locator('button:has-text("Next")').click();
    
    // Step 5: Schedule
    await page.fill('input[name="startDate"]', '2024-01-01');
    await page.fill('input[name="endDate"]', '2024-01-31');
    await page.locator('button:has-text("Next")').click();
    
    // Step 6: Review & Launch
    await expect(page.locator('[data-testid="campaign-summary"]')).toBeVisible();
    await page.locator('button:has-text("Launch Campaign")').click();
    
    // Should redirect to campaign detail page
    await expect(page).toHaveURL(/\/campaigns\/[a-z0-9-]+/);
    await expect(page.locator('.MuiAlert-root')).toContainText('Campaign created successfully');
  });

  test('should edit existing campaign', async ({ page }) => {
    // Click on first campaign in list
    await page.locator('[data-testid="campaigns-table"] tbody tr').first().click();
    
    // Should navigate to campaign detail
    await expect(page).toHaveURL(/\/campaigns\/[a-z0-9-]+/);
    
    // Click edit button
    await page.locator('button:has-text("Edit")').click();
    
    // Update campaign name
    await page.fill('input[name="name"]', 'Updated Campaign Name');
    
    // Save changes
    await page.locator('button:has-text("Save Changes")').click();
    
    // Should show success message
    await expect(page.locator('.MuiAlert-root')).toContainText('Campaign updated successfully');
  });

  test('should pause and resume campaign', async ({ page }) => {
    // Navigate to first active campaign
    await page.locator('[data-testid="campaigns-table"] tbody tr').first().click();
    
    // Click pause button
    await page.locator('button:has-text("Pause")').click();
    
    // Confirm pause
    await page.locator('button:has-text("Confirm")').click();
    
    // Should show paused status
    await expect(page.locator('[data-testid="campaign-status"]')).toContainText('Paused');
    
    // Click resume button
    await page.locator('button:has-text("Resume")').click();
    
    // Should show active status
    await expect(page.locator('[data-testid="campaign-status"]')).toContainText('Active');
  });

  test('should optimize campaign', async ({ page }) => {
    // Navigate to campaign detail
    await page.locator('[data-testid="campaigns-table"] tbody tr').first().click();
    
    // Click optimize button
    await page.locator('button:has-text("Optimize")').click();
    
    // Should show optimization modal
    await expect(page.locator('[data-testid="optimization-modal"]')).toBeVisible();
    
    // Select optimization strategy
    await page.locator('input[value="performance_based"]').check();
    
    // Apply optimization
    await page.locator('button:has-text("Apply Optimization")').click();
    
    // Should show success message
    await expect(page.locator('.MuiAlert-root')).toContainText('Optimization applied successfully');
  });

  test('should filter campaigns', async ({ page }) => {
    // Filter by status
    await page.selectOption('select[name="status"]', 'active');
    await expect(page.locator('[data-testid="campaigns-table"] tbody tr')).toHaveCount(3);
    
    // Filter by platform
    await page.locator('input[value="youtube"]').check();
    await expect(page.locator('[data-testid="campaigns-table"] tbody tr')).toHaveCount(2);
    
    // Search by name
    await page.fill('input[placeholder="Search campaigns..."]', 'Test');
    await expect(page.locator('[data-testid="campaigns-table"] tbody tr')).toHaveCount(1);
    
    // Clear filters
    await page.locator('button:has-text("Clear Filters")').click();
    await expect(page.locator('[data-testid="campaigns-table"] tbody tr').count()).toBeGreaterThan(0);
  });

  test('should bulk select and delete campaigns', async ({ page }) => {
    // Select all campaigns
    await page.locator('input[data-testid="select-all"]').check();
    
    // Should show bulk actions
    await expect(page.locator('[data-testid="bulk-actions"]')).toBeVisible();
    
    // Click delete button
    await page.locator('button:has-text("Delete Selected")').click();
    
    // Confirm deletion
    await page.locator('button:has-text("Confirm Delete")').click();
    
    // Should show success message
    await expect(page.locator('.MuiAlert-root')).toContainText('Campaigns deleted successfully');
  });

  test('should export campaign data', async ({ page }) => {
    // Click export button
    const downloadPromise = page.waitForEvent('download');
    await page.locator('button:has-text("Export")').click();
    
    // Select export format
    await page.locator('button:has-text("Export as CSV")').click();
    
    // Wait for download
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('campaigns');
    expect(download.suggestedFilename()).toContain('.csv');
  });
});