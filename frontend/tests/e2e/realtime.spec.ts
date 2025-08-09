import { test, expect } from '@playwright/test';

test.describe('Real-time Features', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass123');
    await page.locator('button[type="submit"]').click();
    await page.waitForURL('/dashboard');
  });

  test('should show WebSocket connection status', async ({ page }) => {
    // Check connection indicator
    await expect(page.locator('[data-testid="ws-status"]')).toBeVisible();
    await expect(page.locator('[data-testid="ws-status"]')).toHaveClass(/connected/);
    
    // Tooltip should show connected
    await page.locator('[data-testid="ws-status"]').hover();
    await expect(page.locator('[role="tooltip"]')).toContainText('Connected');
  });

  test('should receive real-time campaign updates', async ({ page, context }) => {
    // Navigate to campaigns
    await page.goto('/campaigns');
    
    // Open another tab to create a campaign
    const page2 = await context.newPage();
    await page2.goto('/login');
    await page2.fill('input[name="username"]', 'testuser');
    await page2.fill('input[name="password"]', 'testpass123');
    await page2.locator('button[type="submit"]').click();
    await page2.waitForURL('/dashboard');
    
    // Create campaign in second tab
    await page2.goto('/campaigns/new');
    await page2.fill('input[name="name"]', 'Real-time Test Campaign');
    await page2.selectOption('select[name="objective"]', 'brand_awareness');
    await page2.locator('button:has-text("Quick Create")').click();
    
    // First tab should receive update
    await expect(page.locator('[data-testid="campaigns-table"]')).toContainText('Real-time Test Campaign');
    
    // Should show notification
    await expect(page.locator('[data-testid="notification"]')).toContainText('New campaign created');
    
    await page2.close();
  });

  test('should receive real-time analytics updates', async ({ page }) => {
    // Navigate to analytics
    await page.goto('/analytics');
    
    // Enable real-time mode
    await page.locator('[data-testid="realtime-toggle"]').click();
    
    // Get initial metric value
    const initialValue = await page.locator('[data-testid="metric-impressions"] .value').textContent();
    
    // Wait for WebSocket update (simulated by backend)
    await page.waitForTimeout(3000);
    
    // Value should update
    const newValue = await page.locator('[data-testid="metric-impressions"] .value').textContent();
    expect(newValue).not.toBe(initialValue);
    
    // Should show update animation
    await expect(page.locator('[data-testid="metric-impressions"]')).toHaveClass(/updating/);
  });

  test('should receive trending updates', async ({ page }) => {
    // Navigate to trending
    await page.goto('/trending');
    
    // Get initial trending topic
    const initialTopic = await page.locator('[data-testid="trend-item-1"] .title').textContent();
    
    // Wait for automatic refresh (every 60 seconds, but we'll trigger manually)
    await page.locator('button[data-testid="refresh-trends"]').click();
    
    // Should show loading
    await expect(page.locator('[data-testid="loading-indicator"]')).toBeVisible();
    
    // Wait for update
    await page.waitForSelector('[data-testid="loading-indicator"]', { state: 'hidden' });
    
    // Content should be updated
    const newTopic = await page.locator('[data-testid="trend-item-1"] .title').textContent();
    // Topics might be same, but timestamp should update
    await expect(page.locator('[data-testid="last-updated"]')).not.toContainText('Never');
  });

  test('should show workflow execution progress', async ({ page }) => {
    // Navigate to workflows
    await page.goto('/workflows');
    
    // Execute a workflow
    await page.locator('[data-testid="workflow-auto-optimizer"]').click();
    await page.locator('button:has-text("Execute Now")').click();
    await page.locator('button:has-text("Confirm")').click();
    
    // Should show real-time progress
    await expect(page.locator('[data-testid="execution-progress"]')).toBeVisible();
    
    // Progress bar should update
    await expect(page.locator('[data-testid="progress-bar"]')).toHaveAttribute('aria-valuenow', '0');
    await page.waitForTimeout(2000);
    
    const progress = await page.locator('[data-testid="progress-bar"]').getAttribute('aria-valuenow');
    expect(parseInt(progress || '0')).toBeGreaterThan(0);
    
    // Should show step updates
    await expect(page.locator('[data-testid="current-step"]')).toBeVisible();
  });

  test('should handle WebSocket reconnection', async ({ page, context }) => {
    // Simulate connection loss by blocking WebSocket
    await page.route('**/ws', route => route.abort());
    
    // Should show disconnected status
    await page.waitForSelector('[data-testid="ws-status"].disconnected');
    await expect(page.locator('[data-testid="connection-alert"]')).toContainText('Connection lost');
    
    // Unblock WebSocket
    await page.unroute('**/ws');
    
    // Should reconnect automatically
    await page.waitForSelector('[data-testid="ws-status"].connected');
    await expect(page.locator('[data-testid="connection-alert"]')).toContainText('Reconnected');
  });

  test('should sync data across tabs', async ({ context }) => {
    // Open two tabs
    const page1 = await context.newPage();
    const page2 = await context.newPage();
    
    // Login in both tabs
    for (const page of [page1, page2]) {
      await page.goto('/login');
      await page.fill('input[name="username"]', 'testuser');
      await page.fill('input[name="password"]', 'testpass123');
      await page.locator('button[type="submit"]').click();
      await page.waitForURL('/dashboard');
    }
    
    // Navigate both to campaigns
    await page1.goto('/campaigns');
    await page2.goto('/campaigns');
    
    // Pause campaign in first tab
    await page1.locator('[data-testid="campaign-row-1"] button:has-text("Pause")').click();
    
    // Second tab should update
    await expect(page2.locator('[data-testid="campaign-row-1"] [data-testid="status"]')).toContainText('Paused');
    
    await page1.close();
    await page2.close();
  });

  test('should show live notifications', async ({ page }) => {
    // Check notification center
    await expect(page.locator('[data-testid="notification-bell"]')).toBeVisible();
    
    // Should have no unread initially
    await expect(page.locator('[data-testid="unread-count"]')).not.toBeVisible();
    
    // Trigger an action that generates notification
    await page.goto('/campaigns');
    await page.locator('[data-testid="campaign-row-1"] button:has-text("Optimize")').click();
    await page.locator('button:has-text("Apply")').click();
    
    // Should show unread count
    await expect(page.locator('[data-testid="unread-count"]')).toBeVisible();
    await expect(page.locator('[data-testid="unread-count"]')).toContainText('1');
    
    // Click notification bell
    await page.locator('[data-testid="notification-bell"]').click();
    
    // Should show notification dropdown
    await expect(page.locator('[data-testid="notifications-dropdown"]')).toBeVisible();
    await expect(page.locator('[data-testid="notification-item"]')).toContainText('Campaign optimized');
    
    // Mark as read
    await page.locator('[data-testid="mark-all-read"]').click();
    await expect(page.locator('[data-testid="unread-count"]')).not.toBeVisible();
  });

  test('should update charts in real-time', async ({ page }) => {
    // Navigate to analytics
    await page.goto('/analytics');
    
    // Enable real-time
    await page.locator('[data-testid="realtime-toggle"]').click();
    
    // Get initial data point count
    const initialPoints = await page.locator('.recharts-line-dot').count();
    
    // Wait for new data point
    await page.waitForTimeout(5000);
    
    // Should have new data point
    const newPoints = await page.locator('.recharts-line-dot').count();
    expect(newPoints).toBeGreaterThan(initialPoints);
    
    // Chart should animate
    await expect(page.locator('.recharts-line')).toHaveClass(/animating/);
  });

  test('should show live user presence', async ({ page, context }) => {
    // Open second tab
    const page2 = await context.newPage();
    await page2.goto('/login');
    await page2.fill('input[name="username"]', 'testuser2');
    await page2.fill('input[name="password"]', 'testpass123');
    await page2.locator('button[type="submit"]').click();
    
    // Navigate to same campaign
    await page.goto('/campaigns/test-campaign-1');
    await page2.goto('/campaigns/test-campaign-1');
    
    // Should show other user viewing
    await expect(page.locator('[data-testid="active-users"]')).toContainText('2 users viewing');
    await expect(page.locator('[data-testid="user-avatar-testuser2"]')).toBeVisible();
    
    // When other user leaves
    await page2.close();
    
    // Should update presence
    await page.waitForTimeout(2000);
    await expect(page.locator('[data-testid="active-users"]')).toContainText('1 user viewing');
  });
});