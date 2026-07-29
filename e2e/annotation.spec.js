import { test, expect } from './fixtures.js';
import { ANNOTATION_PANELS, switchTab, expectChartMounted, getAnnotations, waitForCharts } from './helpers.js';

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
