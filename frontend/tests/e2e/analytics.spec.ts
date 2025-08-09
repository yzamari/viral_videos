import { test, expect } from '@playwright/test';

test.describe('Analytics Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login and navigate to analytics
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass123');
    await page.locator('button[type="submit"]').click();
    await page.waitForURL('/dashboard');
    
    await page.goto('/analytics');
  });

  test('should display analytics overview', async ({ page }) => {
    await expect(page.locator('h4')).toContainText('Analytics');
    
    // Check for key metric cards
    await expect(page.locator('[data-testid="metric-impressions"]')).toBeVisible();
    await expect(page.locator('[data-testid="metric-clicks"]')).toBeVisible();
    await expect(page.locator('[data-testid="metric-conversions"]')).toBeVisible();
    await expect(page.locator('[data-testid="metric-spend"]')).toBeVisible();
    await expect(page.locator('[data-testid="metric-roas"]')).toBeVisible();
  });

  test('should display performance charts', async ({ page }) => {
    // Check for charts
    await expect(page.locator('[data-testid="performance-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="platform-breakdown-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="audience-insights-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="creative-performance-chart"]')).toBeVisible();
  });

  test('should filter by date range', async ({ page }) => {
    // Click date range selector
    await page.locator('[data-testid="date-range-selector"]').click();
    
    // Select last 7 days
    await page.locator('button:has-text("Last 7 Days")').click();
    
    // Charts should update
    await expect(page.locator('[data-testid="performance-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="date-range-display"]')).toContainText('Last 7 Days');
    
    // Select custom range
    await page.locator('[data-testid="date-range-selector"]').click();
    await page.locator('button:has-text("Custom Range")').click();
    
    await page.fill('input[name="startDate"]', '2024-01-01');
    await page.fill('input[name="endDate"]', '2024-01-31');
    await page.locator('button:has-text("Apply")').click();
    
    // Should update display
    await expect(page.locator('[data-testid="date-range-display"]')).toContainText('Jan 1 - Jan 31');
  });

  test('should filter by campaign', async ({ page }) => {
    // Select campaign from dropdown
    await page.locator('[data-testid="campaign-selector"]').click();
    await page.locator('li:has-text("Test Campaign 1")').click();
    
    // Analytics should update for selected campaign
    await expect(page.locator('[data-testid="selected-campaign"]')).toContainText('Test Campaign 1');
    await expect(page.locator('[data-testid="performance-chart"]')).toBeVisible();
  });

  test('should switch between chart types', async ({ page }) => {
    // Click on chart type selector
    await page.locator('[data-testid="chart-type-selector"]').click();
    
    // Select bar chart
    await page.locator('button:has-text("Bar Chart")').click();
    await expect(page.locator('.recharts-bar')).toBeVisible();
    
    // Select line chart
    await page.locator('[data-testid="chart-type-selector"]').click();
    await page.locator('button:has-text("Line Chart")').click();
    await expect(page.locator('.recharts-line')).toBeVisible();
    
    // Select area chart
    await page.locator('[data-testid="chart-type-selector"]').click();
    await page.locator('button:has-text("Area Chart")').click();
    await expect(page.locator('.recharts-area')).toBeVisible();
  });

  test('should show platform breakdown', async ({ page }) => {
    // Check platform performance table
    await expect(page.locator('[data-testid="platform-table"]')).toBeVisible();
    
    // Should have rows for each platform
    await expect(page.locator('[data-testid="platform-youtube"]')).toBeVisible();
    await expect(page.locator('[data-testid="platform-tiktok"]')).toBeVisible();
    await expect(page.locator('[data-testid="platform-instagram"]')).toBeVisible();
    
    // Click on platform for details
    await page.locator('[data-testid="platform-youtube"]').click();
    
    // Should show platform-specific metrics
    await expect(page.locator('[data-testid="platform-detail-modal"]')).toBeVisible();
    await expect(page.locator('[data-testid="platform-detail-title"]')).toContainText('YouTube');
  });

  test('should show audience insights', async ({ page }) => {
    // Navigate to audience tab
    await page.locator('[data-testid="tab-audience"]').click();
    
    // Check demographic charts
    await expect(page.locator('[data-testid="age-distribution-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="gender-distribution-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="location-heatmap"]')).toBeVisible();
    await expect(page.locator('[data-testid="device-breakdown-chart"]')).toBeVisible();
  });

  test('should export analytics report', async ({ page }) => {
    // Click export button
    await page.locator('button:has-text("Export Report")').click();
    
    // Select report type
    await page.locator('input[value="pdf"]').check();
    
    // Select metrics to include
    await page.locator('input[value="performance"]').check();
    await page.locator('input[value="audience"]').check();
    await page.locator('input[value="creative"]').check();
    
    // Generate report
    const downloadPromise = page.waitForEvent('download');
    await page.locator('button:has-text("Generate Report")').click();
    
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('analytics-report');
    expect(download.suggestedFilename()).toContain('.pdf');
  });

  test('should set up performance alerts', async ({ page }) => {
    // Navigate to alerts tab
    await page.locator('[data-testid="tab-alerts"]').click();
    
    // Click create alert
    await page.locator('button:has-text("Create Alert")').click();
    
    // Fill alert form
    await page.fill('input[name="alertName"]', 'High CPA Alert');
    await page.selectOption('select[name="metric"]', 'cpa');
    await page.selectOption('select[name="condition"]', 'greater_than');
    await page.fill('input[name="threshold"]', '50');
    await page.selectOption('select[name="severity"]', 'high');
    
    // Save alert
    await page.locator('button:has-text("Save Alert")').click();
    
    // Should show in alerts list
    await expect(page.locator('[data-testid="alerts-list"]')).toContainText('High CPA Alert');
  });

  test('should show real-time updates', async ({ page }) => {
    // Enable real-time mode
    await page.locator('[data-testid="realtime-toggle"]').click();
    
    // Should show real-time indicator
    await expect(page.locator('[data-testid="realtime-indicator"]')).toBeVisible();
    await expect(page.locator('[data-testid="realtime-indicator"]')).toContainText('Live');
    
    // Charts should auto-update (wait for WebSocket update)
    await page.waitForTimeout(2000);
    
    // Check for updated timestamp
    await expect(page.locator('[data-testid="last-updated"]')).toContainText('Just now');
  });
});