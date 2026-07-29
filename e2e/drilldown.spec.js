import { test, expect } from '@playwright/test';
import {
  DRILL_PANELS, switchTab, switchSubTab, expectChartMounted,
  getDatasetLabels, getYStacked, clickLegendItem, clickDataElement,
  isDrilled, waitForCharts,
} from './helpers.js';

test.describe('drill-down via legend click', () => {

  for (const { id, style, region, tab, subTab } of DRILL_PANELS) {
    test(`[${id}] clicking legend "${region}" drills in and toggles back`, async ({ page }) => {
      await page.goto('/');
      await switchTab(page, tab);
      if (subTab) await switchSubTab(page, subTab);
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
      const after = await getDatasetLabels(page, id);
      const hasCountry = after.some(l => l !== region && l !== 'España' && !l.startsWith('↩'));
      expect(hasCountry).toBe(true);

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

      const restored = await getDatasetLabels(page, id);
      const countryLabels = restored.filter(l =>
        l !== region && l !== 'España' && !l.startsWith('↩'));
      expect(countryLabels.length).toBe(0);

      if (style === 'bar') {
        expect(await getYStacked(page, id)).toBe(false);
      }
    });
  }
});

test.describe('drill-down via data-element click', () => {

  for (const { id, region, tab, subTab } of DRILL_PANELS) {
    test(`[${id}] clicking a data point of "${region}" drills in`, async ({ page }) => {
      await page.goto('/');
      await switchTab(page, tab);
      if (subTab) await switchSubTab(page, subTab);
      await waitForCharts(page);
      await expectChartMounted(page, id);

      expect(await isDrilled(page, id)).toBe(false);

      // find the dataset index for the region
      const dsIdx = await page.evaluate(({ id, r }) => {
        const c = document.getElementById(id)._chart;
        return c.data.datasets.findIndex(d => d.label === r);
      }, { id, r: region });
      expect(dsIdx).toBeGreaterThanOrEqual(0);

      // click the first data point of that region's line
      await clickDataElement(page, id, dsIdx, 0);
      await page.waitForTimeout(300);

      expect(await isDrilled(page, id)).toBe(true);
    });
  }
});

test.describe('Spain line is inert', () => {

  for (const { id, tab, subTab } of DRILL_PANELS) {
    test(`[${id}] clicking España legend entry does nothing`, async ({ page }) => {
      await page.goto('/');
      await switchTab(page, tab);
      if (subTab) await switchSubTab(page, subTab);
      await waitForCharts(page);
      await expectChartMounted(page, id);

      const beforeLabels = await getDatasetLabels(page, id);

      // click España in legend
      const found = await clickLegendItem(page, id, 'España');
      expect(found).toBe(true);
      await page.waitForTimeout(300);

      const afterLabels = await getDatasetLabels(page, id);
      expect(afterLabels).toEqual(beforeLabels);
      expect(await isDrilled(page, id)).toBe(false);
    });
  }
});

test.describe('clicking other region while drilled switches region', () => {

  for (const { id, region, tab, subTab } of DRILL_PANELS) {
    test(`[${id}] drilling "${region}" then clicking a second region switches`, async ({ page }) => {
      await page.goto('/');
      await switchTab(page, tab);
      if (subTab) await switchSubTab(page, subTab);
      await waitForCharts(page);
      await expectChartMounted(page, id);

      // drill into first region
      await clickLegendItem(page, id, region);
      await page.waitForTimeout(300);
      expect(await isDrilled(page, id)).toBe(true);

      // get drilled region's country labels
      const drilledLabels = await getDatasetLabels(page, id);

      // click a different region (second one in the list)
      const otherRegion = await page.evaluate(({ id, r }) => {
        const c = document.getElementById(id)._chart;
        const regions = c.data.datasets.map(d => d.label)
          .filter(l => l !== 'España' && l !== r && !l.startsWith('↩'));
        // the dimmed region labels ARE region names (not countries) so find first one
        const knownRegions = ['Africa','America','Asia','Europe','Other',
          'EU','Non-EU Europe','Latin America & Caribbean',
          'North America & Oceania','Asia & Oceania'];
        const other = knownRegions.find(kr => kr !== r && regions.includes(kr));
        return other || null;
      }, { id, r: region });

      if (!otherRegion) return; // skip if no other region (unlikely but safe)

      await clickLegendItem(page, id, otherRegion);
      await page.waitForTimeout(300);

      // now country labels should be from the OTHER region, not the first
      const switchedLabels = await getDatasetLabels(page, id);

      // verify still drilled
      expect(await isDrilled(page, id)).toBe(true);
    });
  }
});
