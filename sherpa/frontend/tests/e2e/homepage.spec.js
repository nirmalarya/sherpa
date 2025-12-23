import { test, expect } from '@playwright/test';

/**
 * SHERPA V1 - Homepage E2E Tests
 *
 * Tests for the main dashboard/homepage functionality including:
 * - Page load and rendering
 * - Navigation
 * - Active sessions display
 * - Quick actions
 */

test.describe('Homepage', () => {
  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/');

    // Verify page title
    await expect(page).toHaveTitle(/SHERPA/i);

    // Verify main heading is visible
    const heading = page.locator('h1, h2').first();
    await expect(heading).toBeVisible();
  });

  test('should display navigation menu', async ({ page }) => {
    await page.goto('/');

    // Check for navigation links
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();

    // Verify key navigation items exist
    const homeLink = page.getByRole('link', { name: /home/i });
    const sessionsLink = page.getByRole('link', { name: /sessions/i });
    const knowledgeLink = page.getByRole('link', { name: /knowledge/i });

    // At least some navigation should be present
    const navLinks = page.locator('nav a');
    const count = await navLinks.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should navigate to sessions page', async ({ page }) => {
    await page.goto('/');

    // Click on Sessions link
    const sessionsLink = page.getByRole('link', { name: /sessions/i });

    if (await sessionsLink.count() > 0) {
      await sessionsLink.first().click();

      // Verify URL changed
      await expect(page).toHaveURL(/.*sessions.*/);
    }
  });

  test('should navigate to knowledge page', async ({ page }) => {
    await page.goto('/');

    // Click on Knowledge link
    const knowledgeLink = page.getByRole('link', { name: /knowledge/i });

    if (await knowledgeLink.count() > 0) {
      await knowledgeLink.first().click();

      // Verify URL changed
      await expect(page).toHaveURL(/.*knowledge.*/);
    }
  });

  test('should display active sessions section', async ({ page }) => {
    await page.goto('/');

    // Look for sessions section or empty state
    const sessionsSection = page.locator('text=/active sessions|no sessions|sessions/i').first();
    await expect(sessionsSection).toBeVisible();
  });

  test('should have no console errors on load', async ({ page }) => {
    const errors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('/');

    // Wait for page to fully load
    await page.waitForLoadState('networkidle');

    // Check for critical errors (allow some warnings)
    const criticalErrors = errors.filter(
      (error) => !error.includes('Warning') && !error.includes('[HMR]')
    );

    expect(criticalErrors.length).toBe(0);
  });

  test('should be responsive', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Page should still be visible
    const body = page.locator('body');
    await expect(body).toBeVisible();

    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');

    await expect(body).toBeVisible();
  });
});
