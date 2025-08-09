import { test, expect } from '@playwright/test';

test.describe('Workflow Automation', () => {
  test.beforeEach(async ({ page }) => {
    // Login and navigate to workflows
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass123');
    await page.locator('button[type="submit"]').click();
    await page.waitForURL('/dashboard');
    
    await page.goto('/workflows');
  });

  test('should display workflows list', async ({ page }) => {
    await expect(page.locator('h4')).toContainText('Workflows');
    
    // Check for pre-built workflows
    await expect(page.locator('[data-testid="workflow-viral-hunter"]')).toBeVisible();
    await expect(page.locator('[data-testid="workflow-auto-optimizer"]')).toBeVisible();
    await expect(page.locator('[data-testid="workflow-ab-tester"]')).toBeVisible();
  });

  test('should create new workflow', async ({ page }) => {
    // Click create workflow button
    await page.locator('button:has-text("Create Workflow")').click();
    
    // Fill workflow details
    await page.fill('input[name="workflowName"]', 'Test Automation Workflow');
    await page.fill('textarea[name="description"]', 'Automated test workflow');
    
    // Add trigger
    await page.locator('button:has-text("Add Trigger")').click();
    await page.selectOption('select[name="triggerType"]', 'scheduled');
    await page.fill('input[name="schedule"]', '0 9 * * *'); // Daily at 9 AM
    
    // Add action
    await page.locator('button:has-text("Add Action")').click();
    await page.selectOption('select[name="actionType"]', 'optimize_campaign');
    await page.fill('input[name="optimizationGoal"]', 'cpa');
    
    // Save workflow
    await page.locator('button:has-text("Save Workflow")').click();
    
    // Should show success message
    await expect(page.locator('.MuiAlert-root')).toContainText('Workflow created successfully');
    
    // Should appear in list
    await expect(page.locator('[data-testid="workflow-list"]')).toContainText('Test Automation Workflow');
  });

  test('should edit workflow', async ({ page }) => {
    // Click on existing workflow
    await page.locator('[data-testid="workflow-viral-hunter"]').click();
    
    // Click edit button
    await page.locator('button:has-text("Edit")').click();
    
    // Update description
    await page.fill('textarea[name="description"]', 'Updated workflow description');
    
    // Update trigger condition
    await page.fill('input[name="viralThreshold"]', '0.9');
    
    // Save changes
    await page.locator('button:has-text("Save Changes")').click();
    
    // Should show success message
    await expect(page.locator('.MuiAlert-root')).toContainText('Workflow updated successfully');
  });

  test('should execute workflow manually', async ({ page }) => {
    // Click on workflow
    await page.locator('[data-testid="workflow-auto-optimizer"]').click();
    
    // Click execute button
    await page.locator('button:has-text("Execute Now")').click();
    
    // Confirm execution
    await page.locator('button:has-text("Confirm")').click();
    
    // Should show execution started
    await expect(page.locator('[data-testid="execution-status"]')).toContainText('Running');
    
    // Wait for execution to complete
    await page.waitForSelector('[data-testid="execution-status"]:has-text("Completed")', { timeout: 10000 });
    
    // Should show execution results
    await expect(page.locator('[data-testid="execution-results"]')).toBeVisible();
  });

  test('should view workflow execution history', async ({ page }) => {
    // Click on workflow
    await page.locator('[data-testid="workflow-viral-hunter"]').click();
    
    // Navigate to history tab
    await page.locator('[data-testid="tab-history"]').click();
    
    // Should show execution history
    await expect(page.locator('[data-testid="execution-history"]')).toBeVisible();
    
    // Check history entries
    const historyEntries = page.locator('[data-testid^="execution-"]');
    await expect(historyEntries).toHaveCount(5);
    
    // Click on execution for details
    await historyEntries.first().click();
    
    // Should show execution details
    await expect(page.locator('[data-testid="execution-detail-modal"]')).toBeVisible();
    await expect(page.locator('[data-testid="execution-timeline"]')).toBeVisible();
    await expect(page.locator('[data-testid="execution-logs"]')).toBeVisible();
  });

  test('should enable/disable workflow', async ({ page }) => {
    // Find workflow with toggle
    const workflow = page.locator('[data-testid="workflow-ab-tester"]');
    const toggle = workflow.locator('[data-testid="workflow-toggle"]');
    
    // Check current state
    const isEnabled = await toggle.getAttribute('aria-checked') === 'true';
    
    // Toggle workflow
    await toggle.click();
    
    // State should change
    const newState = await toggle.getAttribute('aria-checked') === 'true';
    expect(newState).not.toBe(isEnabled);
    
    // Should show notification
    await expect(page.locator('.MuiAlert-root')).toContainText(
      newState ? 'Workflow enabled' : 'Workflow disabled'
    );
  });

  test('should delete workflow', async ({ page }) => {
    // Create a test workflow first
    await page.locator('button:has-text("Create Workflow")').click();
    await page.fill('input[name="workflowName"]', 'Workflow to Delete');
    await page.locator('button:has-text("Save Workflow")').click();
    
    // Find the created workflow
    const workflow = page.locator('[data-testid="workflow-list"]').locator('text=Workflow to Delete');
    await workflow.click();
    
    // Click delete button
    await page.locator('button:has-text("Delete")').click();
    
    // Confirm deletion
    await page.locator('button:has-text("Confirm Delete")').click();
    
    // Should be removed from list
    await expect(page.locator('[data-testid="workflow-list"]')).not.toContainText('Workflow to Delete');
  });

  test('should show workflow analytics', async ({ page }) => {
    // Click on workflow
    await page.locator('[data-testid="workflow-auto-optimizer"]').click();
    
    // Navigate to analytics tab
    await page.locator('[data-testid="tab-analytics"]').click();
    
    // Should show workflow metrics
    await expect(page.locator('[data-testid="workflow-metrics"]')).toBeVisible();
    await expect(page.locator('[data-testid="execution-count"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-rate"]')).toBeVisible();
    await expect(page.locator('[data-testid="avg-duration"]')).toBeVisible();
    
    // Should show performance chart
    await expect(page.locator('[data-testid="workflow-performance-chart"]')).toBeVisible();
  });

  test('should test workflow before saving', async ({ page }) => {
    // Click create workflow
    await page.locator('button:has-text("Create Workflow")').click();
    
    // Fill basic details
    await page.fill('input[name="workflowName"]', 'Test Workflow');
    
    // Add trigger and action
    await page.locator('button:has-text("Add Trigger")').click();
    await page.selectOption('select[name="triggerType"]', 'manual');
    
    await page.locator('button:has-text("Add Action")').click();
    await page.selectOption('select[name="actionType"]', 'send_notification');
    
    // Click test button
    await page.locator('button:has-text("Test Workflow")').click();
    
    // Should show test results
    await expect(page.locator('[data-testid="test-results"]')).toBeVisible();
    await expect(page.locator('[data-testid="test-status"]')).toContainText('Success');
  });

  test('should clone existing workflow', async ({ page }) => {
    // Click on workflow
    await page.locator('[data-testid="workflow-viral-hunter"]').click();
    
    // Click clone button
    await page.locator('button:has-text("Clone")').click();
    
    // Update name
    await page.fill('input[name="workflowName"]', 'Cloned Viral Hunter');
    
    // Save cloned workflow
    await page.locator('button:has-text("Save Clone")').click();
    
    // Should show in list
    await expect(page.locator('[data-testid="workflow-list"]')).toContainText('Cloned Viral Hunter');
  });
});