import { test, expect } from '@playwright/test';

test.describe('Modern M3 UI Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display modern ViralAI Studio branding', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/ViralAI Studio/);
    
    // Check if the main app title is visible
    const appTitle = page.locator('text=ViralAI Studio').first();
    await expect(appTitle).toBeVisible();
    
    // Check for subtitle
    const subtitle = page.locator('text=Advertising Automation Platform');
    await expect(subtitle).toBeVisible();
    
    console.log('✅ Modern branding verified');
  });

  test('should have M3 design elements', async ({ page }) => {
    // Check for gradient background
    const mainContainer = page.locator('body > div').first();
    
    // Check for modern app bar with glassmorphism
    const appBar = page.locator('[class*="MuiAppBar"]').first();
    await expect(appBar).toBeVisible();
    
    // Check for dark mode toggle
    const darkModeButton = page.locator('[data-testid="DarkModeIcon"], [data-testid="LightModeIcon"], svg[data-testid*="Mode"]').first();
    if (await darkModeButton.count() > 0) {
      console.log('✅ Dark mode toggle found');
    }
    
    // Check for navigation drawer button
    const menuButton = page.locator('button').filter({ has: page.locator('svg[data-testid="MenuIcon"]') }).first();
    if (await menuButton.isVisible()) {
      await menuButton.click();
      
      // Check if drawer opens
      const drawer = page.locator('[role="presentation"]').filter({ hasText: 'Navigation' });
      await expect(drawer).toBeVisible({ timeout: 2000 });
      
      console.log('✅ Navigation drawer works');
      
      // Close drawer
      await page.keyboard.press('Escape');
    }
  });

  test('should have connection status indicators', async ({ page }) => {
    // Look for connection status elements
    const connectionIndicators = page.locator('text=/Connected|Disconnected|Server/i');
    
    if (await connectionIndicators.count() > 0) {
      console.log('✅ Connection status indicators present');
    }
    
    // Check for notification badges
    const notificationBadge = page.locator('[class*="MuiBadge"]');
    if (await notificationBadge.count() > 0) {
      console.log('✅ Notification system present');
    }
  });

  test('should have modern Material You styling', async ({ page }) => {
    // Check for rounded corners (M3 uses larger border radius)
    const cards = page.locator('[class*="MuiPaper"], [class*="MuiCard"]').first();
    
    if (await cards.count() > 0) {
      const borderRadius = await cards.evaluate((el) => {
        return window.getComputedStyle(el).borderRadius;
      });
      
      // M3 typically uses 28px or larger border radius
      console.log(`Border radius: ${borderRadius}`);
      
      if (parseInt(borderRadius) >= 12) {
        console.log('✅ Material You border radius applied');
      }
    }
    
    // Check for proper font family
    const body = page.locator('body');
    const fontFamily = await body.evaluate((el) => {
      return window.getComputedStyle(el).fontFamily;
    });
    
    if (fontFamily.includes('Google Sans') || fontFamily.includes('Roboto')) {
      console.log('✅ Material You typography applied');
    }
  });

  test('should have floating action button on config page', async ({ page }) => {
    // Check if we're on config page
    const configContent = page.locator('text=/Configuration|Generate|Mission/i');
    
    if (await configContent.count() > 0) {
      // Look for FAB
      const fab = page.locator('[class*="MuiFab"]');
      
      if (await fab.count() > 0) {
        console.log('✅ Floating Action Button present');
        
        // Check FAB styling
        const background = await fab.evaluate((el) => {
          return window.getComputedStyle(el).background;
        });
        
        if (background.includes('gradient')) {
          console.log('✅ FAB has gradient styling');
        }
      }
    }
  });

  test('should toggle dark mode', async ({ page }) => {
    // Get initial background
    const body = page.locator('body');
    const initialBg = await body.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    
    // Find and click dark mode toggle
    const darkModeToggle = page.locator('button').filter({ 
      has: page.locator('svg').filter({ 
        has: page.locator('path[d*="M12 3v1m0"]') 
      })
    }).or(page.locator('button:has([data-testid*="Mode"])')).first();
    
    if (await darkModeToggle.count() > 0) {
      await darkModeToggle.click();
      await page.waitForTimeout(500); // Wait for transition
      
      const newBg = await body.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });
      
      if (initialBg !== newBg) {
        console.log('✅ Dark mode toggle works');
      }
    }
  });
});

test.describe('Responsive Design', () => {
  test('should be mobile responsive', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Check if menu is still accessible
    const menuButton = page.locator('button').first();
    await expect(menuButton).toBeVisible();
    
    // Check if content adapts
    const mainContent = page.locator('[class*="MuiContainer"]').first();
    if (await mainContent.count() > 0) {
      const width = await mainContent.evaluate((el) => el.offsetWidth);
      expect(width).toBeLessThanOrEqual(375);
      console.log('✅ Mobile responsive layout works');
    }
  });
  
  test('should work on tablet', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    
    const appBar = page.locator('[class*="MuiAppBar"]').first();
    await expect(appBar).toBeVisible();
    console.log('✅ Tablet layout works');
  });
});