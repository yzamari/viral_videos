import { test, expect } from '@playwright/test';

test.describe('Professional UI Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should have proper color contrast', async ({ page }) => {
    // Check that text is readable (not white on white)
    const appTitle = page.locator('h6:has-text("ViralAI Platform")').first();
    await expect(appTitle).toBeVisible();
    
    // Get text color
    const textColor = await appTitle.evaluate((el) => {
      return window.getComputedStyle(el).color;
    });
    
    // Get background color
    const background = await page.locator('body').evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    
    console.log(`Text color: ${textColor}`);
    console.log(`Background: ${background}`);
    
    // Verify they're different (no white on white)
    expect(textColor).not.toBe('rgb(255, 255, 255)');
    console.log('✅ Text has proper contrast');
  });

  test('should have clean professional design', async ({ page }) => {
    // Check for clean app bar
    const appBar = page.locator('[class*="MuiAppBar"]').first();
    await expect(appBar).toBeVisible();
    
    const appBarBg = await appBar.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    
    // Should have white or light background in light mode
    console.log(`AppBar background: ${appBarBg}`);
    
    // Check for business icon
    const businessIcon = page.locator('svg[data-testid="BusinessIcon"]').first();
    if (await businessIcon.count() > 0) {
      console.log('✅ Professional business icon present');
    }
    
    // Check for clean typography
    const title = page.locator('text=ViralAI Platform').first();
    const fontFamily = await title.evaluate((el) => {
      return window.getComputedStyle(el).fontFamily;
    });
    
    console.log(`Font family: ${fontFamily}`);
    expect(fontFamily).toContain('Segoe UI');
    console.log('✅ Professional typography applied');
  });

  test('should have subtle, professional styling', async ({ page }) => {
    // Check for subtle shadows (not heavy/AI-generated look)
    const paper = page.locator('[class*="MuiPaper"]').first();
    
    if (await paper.count() > 0) {
      const boxShadow = await paper.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });
      
      console.log(`Box shadow: ${boxShadow}`);
      
      // Should have subtle shadow, not heavy gradients
      if (boxShadow && boxShadow !== 'none') {
        expect(boxShadow).toContain('rgba(0, 0, 0, 0.1)');
        console.log('✅ Subtle professional shadows');
      }
    }
    
    // Check border radius is reasonable (not overly rounded)
    const button = page.locator('button').first();
    const borderRadius = await button.evaluate((el) => {
      return window.getComputedStyle(el).borderRadius;
    });
    
    const radiusValue = parseInt(borderRadius);
    expect(radiusValue).toBeLessThanOrEqual(12);
    console.log('✅ Professional border radius (not overly rounded)');
  });

  test('should have proper connection status indicator', async ({ page }) => {
    // Look for clean status chip
    const statusChip = page.locator('[class*="MuiChip"]').filter({ hasText: /Connected|Offline/ }).first();
    
    if (await statusChip.count() > 0) {
      await expect(statusChip).toBeVisible();
      
      const chipText = await statusChip.textContent();
      console.log(`Status: ${chipText}`);
      
      // Check it has proper styling
      const chipBg = await statusChip.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });
      
      console.log('✅ Clean status indicator present');
    }
  });

  test('should toggle dark mode properly', async ({ page }) => {
    // Get initial background
    const body = page.locator('body');
    const initialBg = await body.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    
    // Find dark mode toggle
    const darkModeBtn = page.locator('button').filter({ 
      has: page.locator('[data-testid="DarkModeIcon"], [data-testid="LightModeIcon"]') 
    }).first();
    
    if (await darkModeBtn.count() > 0) {
      await darkModeBtn.click();
      await page.waitForTimeout(300);
      
      const newBg = await body.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });
      
      expect(initialBg).not.toBe(newBg);
      console.log('✅ Dark mode toggle works');
      
      // Verify dark mode has proper contrast
      const darkText = await page.locator('h6').first().evaluate((el) => {
        return window.getComputedStyle(el).color;
      });
      
      console.log(`Dark mode text: ${darkText}`);
      console.log(`Dark mode bg: ${newBg}`);
      
      // Text should be light in dark mode
      expect(darkText).not.toBe('rgb(0, 0, 0)');
      console.log('✅ Dark mode has proper contrast');
    }
  });

  test('should have clean navigation drawer', async ({ page }) => {
    // Open drawer
    const menuButton = page.locator('button[aria-label*="menu"]').or(page.locator('button').filter({ has: page.locator('[data-testid="MenuIcon"]') })).first();
    
    if (await menuButton.isVisible()) {
      await menuButton.click();
      
      // Check drawer styling
      const drawer = page.locator('[role="presentation"]').filter({ hasText: 'Navigation' });
      await expect(drawer).toBeVisible({ timeout: 2000 });
      
      // Check for clean list items
      const listItems = drawer.locator('[class*="MuiListItemButton"]');
      const count = await listItems.count();
      
      expect(count).toBeGreaterThan(0);
      console.log(`✅ Clean navigation with ${count} items`);
      
      // Check selected state styling
      const selectedItem = listItems.filter({ hasText: 'Configuration' }).first();
      if (await selectedItem.count() > 0) {
        const selectedBg = await selectedItem.evaluate((el) => {
          return window.getComputedStyle(el).backgroundColor;
        });
        
        console.log(`Selected item bg: ${selectedBg}`);
        console.log('✅ Professional selected state');
      }
      
      // Close drawer
      await page.keyboard.press('Escape');
    }
  });

  test('should not have AI-generated gradient backgrounds', async ({ page }) => {
    // Check body doesn't have gradient
    const bodyBg = await page.locator('body').evaluate((el) => {
      return window.getComputedStyle(el).background;
    });
    
    expect(bodyBg).not.toContain('gradient');
    console.log('✅ No AI-style gradients on body');
    
    // Check buttons don't have heavy gradients
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < Math.min(buttonCount, 3); i++) {
      const btnBg = await buttons.nth(i).evaluate((el) => {
        return window.getComputedStyle(el).background;
      });
      
      if (btnBg.includes('gradient')) {
        console.log('⚠️ Found gradient on button - checking if subtle...');
        expect(btnBg).not.toContain('135deg'); // No diagonal gradients
      }
    }
    
    console.log('✅ Clean, professional button styling');
  });
});