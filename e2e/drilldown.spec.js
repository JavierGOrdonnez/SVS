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

test.describe('drill-down via data-element click', () => {

  for (const { id, region, tab, regions, dataFile, dataKey } of DRILL_PANELS) {
    test(`[${id}] clicking a data point of "${region}" drills in`, async ({ page }) => {
      await page.goto('/');
      await switchTab(page, tab);
      await waitForCharts(page);
      await expectChartMounted(page, id);

      expect(await isDrilled(page, id, regions)).toBe(false);

      // find the dataset index for the region
      const dsIdx = await page.evaluate(({ id, r }) => {
        const c = document.getElementById(id)._chart;
        return c.data.datasets.findIndex(d => d.label === r);
      }, { id, r: region });
      expect(dsIdx).toBeGreaterThanOrEqual(0);

      // click the first data point of that region's line
      await clickDataElement(page, id, dsIdx, 0);
      await page.waitForTimeout(300);

      expect(await isDrilled(page, id, regions)).toBe(true);
    });

    // Regression guard against an implementation that drills into "whatever
    // dataset happens to be first" regardless of which point was actually
    // clicked. Chart.js's default click handling reports the elements found
    // by the chart's hover `interaction` mode (here 'index'/intersect:false,
    // set in baseOpts for tooltips) — that mode returns one element per
    // dataset at the nearest x-index, not just the element under the
    // cursor, so naively using its first entry would always drill into
    // `region` (Africa, coincidentally index 0 in every DRILL_PANELS entry)
    // even when a different region's line/bar was clicked.
    const secondRegion = regions.find((r) => r !== region);
    if (secondRegion) {
      test(`[${id}] clicking a data point of "${secondRegion}" drills into that region specifically`, async ({ page }) => {
        await page.goto('/');
        await switchTab(page, tab);
        await waitForCharts(page);
        await expectChartMounted(page, id);

        const dsIdx = await page.evaluate(({ id, r }) => {
          const c = document.getElementById(id)._chart;
          return c.data.datasets.findIndex(d => d.label === r);
        }, { id, r: secondRegion });
        expect(dsIdx).toBeGreaterThanOrEqual(0);

        await clickDataElement(page, id, dsIdx, 0);
        await page.waitForTimeout(300);

        expect(await isDrilled(page, id, regions)).toBe(true);

        const expectedCountries = await page.evaluate(async ({ file, key, r }) => {
          const d = await fetch(`data/${file}`).then((res) => res.json());
          return d[key].by_country[r].countries;
        }, { file: dataFile, key: dataKey, r: secondRegion });

        const labels = await getDatasetLabels(page, id);
        for (const country of expectedCountries) {
          expect(labels).toContain(country);
        }
      });
    }
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
