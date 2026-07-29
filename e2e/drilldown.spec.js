import { test, expect } from './fixtures.js';
import {
  DRILL_PANELS, switchTab, expectChartMounted,
  getDatasetLabels, getYStacked, clickLegendItem, clickDataElement,
  isDrilled, waitForCharts,
} from './helpers.js';

test.describe('drill-down via legend click', () => {

  for (const { id, style, region, tab, regions } of DRILL_PANELS) {
    test(`[${id}] clicking legend "${region}" drills in and toggles back`, async ({ page }) => {
      await page.goto('/');
      await switchTab(page, tab);
      await waitForCharts(page);
      await expectChartMounted(page, id);

      // capture labels before drill
      const before = await getDatasetLabels(page, id);
      expect(before).not.toContain('Marruecos');

      // click region in legend
      const found = await clickLegendItem(page, id, region);
      expect(found).toBe(true);
      await page.waitForTimeout(300);

      // should now have country data
      expect(await isDrilled(page, id, regions)).toBe(true);

      if (style === 'bar') {
        expect(await getYStacked(page, id)).toBe(true);
      }

      // click same region again (or back-handle) to return to aggregate
      if (style === 'bar') {
        const hasBack = await clickLegendItem(page, id, `↩ ${region}`);
        expect(hasBack).toBe(true);
      } else {
        await clickLegendItem(page, id, region);
      }
      await page.waitForTimeout(300);

      // back to the exact same aggregate view we started from — comparing
      // directly against `before` (rather than trying to guess which labels
      // are "countries") also correctly handles the sibling region names
      // that reappear once undrilled, which a country-vs-region heuristic
      // would otherwise misclassify.
      const restored = await getDatasetLabels(page, id);
      expect(restored).toEqual(before);

      if (style === 'bar') {
        expect(await getYStacked(page, id)).toBe(false);
      }
    });
  }
});

// No chart in docs/app.js wires up a data-point/element click handler —
// regionDrilldownChart() only defines `plugins.legend.onClick`. Drilling in
// by clicking a bar/line point directly is not an interaction the app
// currently supports, so there is nothing here to test yet. Kept as an
// explicit skip (not deleted) pending a product decision on whether to add
// that interaction — see e2e/README.md.
test.describe('drill-down via data-element click', () => {

  for (const { id, region, tab } of DRILL_PANELS) {
    test.skip(`[${id}] clicking a data point of "${region}" drills in`, async ({ page }) => {
      await page.goto('/');
      await switchTab(page, tab);
      await waitForCharts(page);
      await expectChartMounted(page, id);

      const dsIdx = await page.evaluate(({ id, r }) => {
        const c = document.getElementById(id)._chart;
        return c.data.datasets.findIndex(d => d.label === r);
      }, { id, r: region });
      expect(dsIdx).toBeGreaterThanOrEqual(0);

      await clickDataElement(page, id, dsIdx, 0);
      await page.waitForTimeout(300);
    });
  }
});

test.describe('Spain line is inert', () => {

  for (const { id, tab, hasSpain, regions } of DRILL_PANELS) {
    test(`[${id}] clicking España legend entry does nothing`, async ({ page }) => {
      // mi-stock-region's underlying data has no `spain` series at all
      // (unlike the two sexual-crimes drill panels) — no España legend
      // entry exists there to click, so there's nothing to assert.
      test.skip(!hasSpain, 'panel has no España reference line in its data');

      await page.goto('/');
      await switchTab(page, tab);
      await waitForCharts(page);
      await expectChartMounted(page, id);

      const beforeLabels = await getDatasetLabels(page, id);

      // click España in legend
      const found = await clickLegendItem(page, id, 'España');
      expect(found).toBe(true);
      await page.waitForTimeout(300);

      const afterLabels = await getDatasetLabels(page, id);
      expect(afterLabels).toEqual(beforeLabels);
      expect(await isDrilled(page, id, regions)).toBe(false);
    });
  }
});

test.describe('clicking other region while drilled switches region', () => {

  for (const { id, region, tab, regions } of DRILL_PANELS) {
    test(`[${id}] drilling "${region}" then clicking a second region switches`, async ({ page }) => {
      await page.goto('/');
      await switchTab(page, tab);
      await waitForCharts(page);
      await expectChartMounted(page, id);

      // drill into first region
      await clickLegendItem(page, id, region);
      await page.waitForTimeout(300);
      expect(await isDrilled(page, id, regions)).toBe(true);

      const drilledLabels = await getDatasetLabels(page, id);

      // click a second region straight from this panel's own region list
      const otherRegion = regions.find((r) => r !== region);
      expect(otherRegion).toBeTruthy();

      await clickLegendItem(page, id, otherRegion);
      await page.waitForTimeout(300);

      // labels actually changed (drilled into a different region's countries)
      const switchedLabels = await getDatasetLabels(page, id);
      expect(switchedLabels).not.toEqual(drilledLabels);

      // verify still drilled
      expect(await isDrilled(page, id, regions)).toBe(true);
    });
  }
});
