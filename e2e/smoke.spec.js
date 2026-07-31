import { test, expect } from './fixtures.js';
import { TAB_PANELS, switchTab, expectChartMounted, chartHasData, waitForCharts } from './helpers.js';

// Scope: the three tabs the dashboard's data-quality work has focused on so
// far (feminicides, sexual crime, migration & cohorts). Hate crime is left
// out of the depth pass for now — see e2e/README.md.
const TABS = ['feminicides', 'sexual-crimes', 'migration'];

test.describe('tab navigation', () => {
  for (const tab of TABS) {
    test(`[${tab}] switching to the tab shows its section and hides the others`, async ({ page }) => {
      await page.goto('/');
      await switchTab(page, tab);

      const activeSection = page.locator(`#tab-${tab}`);
      await expect(activeSection).toHaveClass(/active/);

      const otherSections = await page.locator('.tab-panel:not(.active)').all();
      // every other mounted section must NOT be the one we just switched to
      for (const el of otherSections) {
        await expect(el).not.toHaveAttribute('id', `tab-${tab}`);
      }

      const btn = page.locator('#main-tabs').locator(`button[data-id="${tab}"]`);
      await expect(btn).toHaveAttribute('aria-selected', 'true');
    });
  }
});

test.describe('every chart panel mounts with real data', () => {
  for (const tab of TABS) {
    test(`[${tab}] all registered panels mount a Chart.js instance with non-empty data`, async ({ page }) => {
      const consoleErrors = [];
      page.on('pageerror', (err) => consoleErrors.push(err.message));
      page.on('console', (msg) => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });

      await page.goto('/');
      await switchTab(page, tab);
      await waitForCharts(page);

      for (const id of TAB_PANELS[tab]) {
        await expectChartMounted(page, id);
        expect(await chartHasData(page, id), `panel "${id}" has no non-null data points`).toBe(true);
      }

      expect(consoleErrors, `console/page errors while viewing ${tab}: ${consoleErrors.join(' | ')}`).toEqual([]);
    });
  }
});

test.describe('caveat lists', () => {
  const CAVEAT_IDS = { feminicides: 'cav-fem', 'sexual-crimes': 'cav-sexual', migration: 'cav-mig' };

  for (const tab of TABS) {
    test(`[${tab}] caveat list renders at least one item`, async ({ page }) => {
      await page.goto('/');
      await switchTab(page, tab);
      const count = await page.evaluate((id) => {
        const el = document.getElementById(id);
        return el?.items?.length ?? 0;
      }, CAVEAT_IDS[tab]);
      expect(count).toBeGreaterThan(0);
    });
  }
});

test('headline KPI cards render with real values on first load', async ({ page }) => {
  await page.goto('/');
  const cards = page.locator('#headlines svs-stat-card');
  await expect(cards).toHaveCount(5);
  const values = await cards.evaluateAll((els) => els.map((el) => el.getAttribute('value')));
  for (const v of values) {
    expect(v, `headline card rendered a placeholder value: ${values.join(', ')}`).not.toBe('—');
    expect(v).not.toBeNull();
  }
});

test.describe('confidence filter UI toggles', () => {
  test('clicking a confidence pill flips its pressed state and fires conf-change', async ({ page }) => {
    await page.goto('/');
    await switchTab(page, 'feminicides');
    await waitForCharts(page);

    const filter = page.locator('svs-confidence-filter');
    const mediumBtn = filter.locator('button[data-tier="medium"]');
    await expect(mediumBtn).toHaveAttribute('aria-pressed', 'true');

    const eventFired = page.evaluate(() => new Promise((resolve) => {
      document.querySelector('svs-confidence-filter').addEventListener('conf-change', (e) => resolve(e.detail.active), { once: true });
    }));
    await mediumBtn.click();
    const active = await eventFired;

    await expect(mediumBtn).toHaveAttribute('aria-pressed', 'false');
    expect(active.medium).toBe(false);
  });
});
