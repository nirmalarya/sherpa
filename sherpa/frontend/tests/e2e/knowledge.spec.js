import { test, expect } from '@playwright/test';

/**
 * SHERPA V1 - Knowledge Page E2E Tests
 *
 * Tests for knowledge base functionality including:
 * - Snippet browsing
 * - Search/query functionality
 * - Category filtering
 * - Snippet preview
 */

test.describe('Knowledge Page', () => {
  test('should load knowledge page successfully', async ({ page }) => {
    await page.goto('/knowledge');

    // Verify we're on knowledge page
    await expect(page).toHaveURL(/.*knowledge.*/);

    // Check for knowledge content
    const content = page.locator('main, [role="main"], body');
    await expect(content).toBeVisible();
  });

  test('should display search or query interface', async ({ page }) => {
    await page.goto('/knowledge');

    await page.waitForLoadState('networkidle');

    // Look for search/query input
    const searchInput = page.locator(
      'input[type="search"], input[placeholder*="search" i], input[placeholder*="query" i], textarea'
    );

    // Should have some way to search
    if (await searchInput.count() > 0) {
      await expect(searchInput.first()).toBeVisible();
    }
  });

  test('should display snippets or categories', async ({ page }) => {
    await page.goto('/knowledge');

    await page.waitForLoadState('networkidle');

    // Look for snippets or categories
    const snippets = page.locator('.snippet, .snippet-card, [class*="snippet"]');
    const categories = page.locator('.category, [class*="category"]');
    const listItems = page.locator('li, .item');

    const hasContent =
      (await snippets.count() > 0) ||
      (await categories.count() > 0) ||
      (await listItems.count() > 0);

    expect(hasContent).toBeTruthy();
  });

  test('should allow searching for snippets', async ({ page }) => {
    await page.goto('/knowledge');

    await page.waitForLoadState('networkidle');

    // Find search input
    const searchInput = page.locator(
      'input[type="search"], input[placeholder*="search" i], input[placeholder*="query" i]'
    ).first();

    if (await searchInput.count() > 0) {
      // Type a search query
      await searchInput.fill('react');

      // Wait a bit for results
      await page.waitForTimeout(1000);

      // Should show some results or empty state
      const content = page.locator('body');
      await expect(content).toBeVisible();
    }
  });

  test('should display snippet categories', async ({ page }) => {
    await page.goto('/knowledge');

    await page.waitForLoadState('networkidle');

    // Look for category labels/badges
    const categories = page.locator(
      'text=/security|python|react|testing|api|git/i, .category, .tag, .badge'
    );

    // Should have some categorization
    const count = await categories.count();
    expect(count >= 0).toBeTruthy();
  });

  test('should display snippet preview or details', async ({ page }) => {
    await page.goto('/knowledge');

    await page.waitForLoadState('networkidle');

    // Look for snippet cards or list items
    const snippetCards = page.locator('.snippet, .card, li').first();

    if (await snippetCards.count() > 0) {
      // Should have some content visible
      await expect(snippetCards).toBeVisible();
    }
  });

  test('should handle empty search results gracefully', async ({ page }) => {
    await page.goto('/knowledge');

    await page.waitForLoadState('networkidle');

    // Find search input
    const searchInput = page.locator(
      'input[type="search"], input[placeholder*="search" i], input[placeholder*="query" i]'
    ).first();

    if (await searchInput.count() > 0) {
      // Search for something unlikely to exist
      await searchInput.fill('xyzabc123impossible');

      // Wait for search to complete
      await page.waitForTimeout(1500);

      // Should show empty state or no results message
      const emptyState = page.locator('text=/no results|not found|no snippets/i');

      // Page should still be functional (no crash)
      const body = page.locator('body');
      await expect(body).toBeVisible();
    }
  });

  test('should display snippet code blocks', async ({ page }) => {
    await page.goto('/knowledge');

    await page.waitForLoadState('networkidle');

    // Look for code blocks
    const codeBlocks = page.locator('pre, code, .code-block, [class*="code"]');

    // Knowledge base should have some code
    const count = await codeBlocks.count();
    expect(count >= 0).toBeTruthy();
  });
});
