import { test, expect } from './fixtures.js';
import { ANNOTATION_PANELS, switchTab, expectChartMounted, getAnnotations, getChartLabels, waitForCharts } from './helpers.js';

test.describe('vline break/milestone annotations render at the right year', () => {
  for (const { id, label, year, tab } of ANNOTATION_PANELS) {
    test(`[${id}] "${label}" marker sits at ${year}`, async ({ page }) => {
      await page.goto('/');
      await switchTab(page, tab);
      await waitForCharts(page);
      await expectChartMounted(page, id);

      const annotations = await getAnnotations(page, id);
      expect(annotations, `chart "${id}" has no annotation plugin config`).not.toBeNull();

      const values = Object.values(annotations);
      const match = values.find((a) => a?.label?.content === label);
      expect(match, `no annotation with label "${label}" among: ${values.map((a) => a?.label?.content).join(', ')}`).toBeTruthy();
      expect(String(match.xMin)).toBe(year);
      expect(String(match.xMax)).toBe(year);
    });
  }
});

test.describe('COVID year-band shading covers the full 2020 column', () => {
  // Every year-indexed timeline chart that covers 2020 gets a yearBand()
  // box annotation instead of a single vline — index ± 0.5 on the category
  // scale, so it shades the whole column rather than collapsing to a
  // zero-width line. One representative panel per tab is enough to prove
  // the mechanism works everywhere it's wired (all of them share the same
  // yearBand() helper), rather than re-testing every single panel.
  const COVID_PANELS = [
    { id: 'fem-timeline', tab: 'feminicides' },
    { id: 'sx-totals', tab: 'sexual-crimes' },
    { id: 'sx-nationality-victims', tab: 'sexual-crimes' },
    { id: 'mi-inflow', tab: 'migration' },
    { id: 'mi-stock-region', tab: 'migration' },
    { id: 'hc-totals', tab: 'hate-crimes' },
  ];

  for (const { id, tab } of COVID_PANELS) {
    test(`[${id}] covid box spans index-0.5 to index+0.5 of the 2020 column`, async ({ page }) => {
      await page.goto('/');
      await switchTab(page, tab);
      await waitForCharts(page);
      await expectChartMounted(page, id);

      const [annotations, labels] = await Promise.all([getAnnotations(page, id), getChartLabels(page, id)]);
      expect(annotations, `chart "${id}" has no annotation plugin config`).not.toBeNull();

      const covid = Object.values(annotations).find((a) => a?.label?.content === 'COVID');
      expect(covid, `chart "${id}" has no COVID annotation`).toBeTruthy();
      expect(covid.type).toBe('box');

      const idx = labels.indexOf('2020');
      expect(idx).toBeGreaterThanOrEqual(0);
      expect(covid.xMin).toBeCloseTo(idx - 0.5, 5);
      expect(covid.xMax).toBeCloseTo(idx + 0.5, 5);
    });
  }
});
