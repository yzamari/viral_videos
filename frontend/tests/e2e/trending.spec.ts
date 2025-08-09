import { test, expect } from '@playwright/test';

test.describe('Trending & Viral Opportunities', () => {
  test.beforeEach(async ({ page }) => {
    // Login and navigate to trending
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass123');
    await page.locator('button[type="submit"]').click();
    await page.waitForURL('/dashboard');
    
    await page.goto('/trending');
  });

  test('should display trending topics', async ({ page }) => {
    await expect(page.locator('h4')).toContainText('Trending');
    
    // Check for trending cards
    await expect(page.locator('[data-testid="trending-youtube"]')).toBeVisible();
    await expect(page.locator('[data-testid="trending-tiktok"]')).toBeVisible();
    await expect(page.locator('[data-testid="trending-instagram"]')).toBeVisible();
    await expect(page.locator('[data-testid="trending-twitter"]')).toBeVisible();
  });

  test('should show viral opportunities', async ({ page }) => {
    // Check viral opportunities section
    await expect(page.locator('[data-testid="viral-opportunities"]')).toBeVisible();
    
    // Should show viral score for each opportunity
    const opportunities = page.locator('[data-testid^="opportunity-"]');
    await expect(opportunities).toHaveCount(5);
    
    // Check first opportunity has required elements
    const firstOpportunity = opportunities.first();
    await expect(firstOpportunity.locator('[data-testid="viral-score"]')).toBeVisible();
    await expect(firstOpportunity.locator('[data-testid="platform-icon"]')).toBeVisible();
    await expect(firstOpportunity.locator('[data-testid="trend-description"]')).toBeVisible();
  });

  test('should filter by platform', async ({ page }) => {
    // Click platform filter
    await page.locator('[data-testid="platform-filter"]').click();
    
    // Select TikTok only
    await page.locator('input[value="tiktok"]').check();
    await page.locator('input[value="youtube"]').uncheck();
    await page.locator('input[value="instagram"]').uncheck();
    
    // Apply filter
    await page.locator('button:has-text("Apply")').click();
    
    // Should only show TikTok trends
    await expect(page.locator('[data-testid="trending-tiktok"]')).toBeVisible();
    await expect(page.locator('[data-testid="trending-youtube"]')).not.toBeVisible();
  });

  test('should search for specific trends', async ({ page }) => {
    // Enter search query
    await page.fill('input[placeholder="Search trends..."]', 'AI technology');
    await page.locator('button:has-text("Search")').click();
    
    // Should show search results
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible();
    await expect(page.locator('[data-testid="search-results"]')).toContainText('AI technology');
    
    // Results should be relevant
    const results = page.locator('[data-testid^="search-result-"]');
    await expect(results.first()).toContainText(/AI|technology|artificial/i);
  });

  test('should create campaign from trend', async ({ page }) => {
    // Click on a trending topic
    await page.locator('[data-testid="trend-item-1"]').click();
    
    // Should show trend details modal
    await expect(page.locator('[data-testid="trend-detail-modal"]')).toBeVisible();
    
    // Click create campaign button
    await page.locator('button:has-text("Create Campaign")').click();
    
    // Should navigate to campaign creation with pre-filled data
    await expect(page).toHaveURL('/campaigns/new');
    
    // Check if trend data is pre-filled
    const nameInput = page.locator('input[name="name"]');
    await expect(nameInput).toHaveValue(/trending/i);
  });

  test('should show trend analysis', async ({ page }) => {
    // Click analyze button on a trend
    await page.locator('[data-testid="trend-item-1"] button:has-text("Analyze")').click();
    
    // Should show analysis modal
    await expect(page.locator('[data-testid="trend-analysis-modal"]')).toBeVisible();
    
    // Check analysis components
    await expect(page.locator('[data-testid="growth-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="engagement-metrics"]')).toBeVisible();
    await expect(page.locator('[data-testid="audience-demographics"]')).toBeVisible();
    await expect(page.locator('[data-testid="content-recommendations"]')).toBeVisible();
  });

  test('should show hashtag performance', async ({ page }) => {
    // Navigate to hashtags tab
    await page.locator('[data-testid="tab-hashtags"]').click();
    
    // Should show hashtag table
    await expect(page.locator('[data-testid="hashtags-table"]')).toBeVisible();
    
    // Check hashtag data
    const hashtags = page.locator('[data-testid^="hashtag-row-"]');
    await expect(hashtags).toHaveCount(10);
    
    // Each hashtag should have metrics
    const firstHashtag = hashtags.first();
    await expect(firstHashtag.locator('[data-testid="hashtag-name"]')).toBeVisible();
    await expect(firstHashtag.locator('[data-testid="usage-count"]')).toBeVisible();
    await expect(firstHashtag.locator('[data-testid="trend-score"]')).toBeVisible();
  });

  test('should show content suggestions', async ({ page }) => {
    // Navigate to suggestions tab
    await page.locator('[data-testid="tab-suggestions"]').click();
    
    // Should show AI-generated suggestions
    await expect(page.locator('[data-testid="content-suggestions"]')).toBeVisible();
    
    // Check suggestion cards
    const suggestions = page.locator('[data-testid^="suggestion-card-"]');
    await expect(suggestions).toHaveCount(6);
    
    // Each suggestion should have required elements
    const firstSuggestion = suggestions.first();
    await expect(firstSuggestion.locator('[data-testid="suggestion-title"]')).toBeVisible();
    await expect(firstSuggestion.locator('[data-testid="suggestion-description"]')).toBeVisible();
    await expect(firstSuggestion.locator('[data-testid="predicted-performance"]')).toBeVisible();
    await expect(firstSuggestion.locator('button:has-text("Use This")')).toBeVisible();
  });

  test('should refresh trending data', async ({ page }) => {
    // Get initial timestamp
    const initialTimestamp = await page.locator('[data-testid="last-updated"]').textContent();
    
    // Click refresh button
    await page.locator('button[data-testid="refresh-trends"]').click();
    
    // Should show loading state
    await expect(page.locator('[data-testid="loading-indicator"]')).toBeVisible();
    
    // Wait for update
    await page.waitForSelector('[data-testid="loading-indicator"]', { state: 'hidden' });
    
    // Timestamp should be updated
    const newTimestamp = await page.locator('[data-testid="last-updated"]').textContent();
    expect(newTimestamp).not.toBe(initialTimestamp);
  });

  test('should export trending report', async ({ page }) => {
    // Click export button
    await page.locator('button:has-text("Export Trends")').click();
    
    // Select export options
    await page.locator('input[value="include_analysis"]').check();
    await page.locator('input[value="include_recommendations"]').check();
    
    // Download report
    const downloadPromise = page.waitForEvent('download');
    await page.locator('button:has-text("Download Report")').click();
    
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('trending-report');
  });
});