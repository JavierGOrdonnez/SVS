import { expect } from '@playwright/test';

/** Panel IDs that use regionDrilldownChart (drill-down capable) */
export const DRILL_PANELS = [
  { id: 'sx-nationality-victims',      style: 'bar',  tab: 'violence',  region: 'Africa',  subTab: 'Sexual' },
  { id: 'sx-nationality-perpetrators',  style: 'bar',  tab: 'violence',  region: 'Africa',  subTab: 'Sexual' },
  { id: 'sx-peligrosidad',              style: 'line', tab: 'violence',  region: 'Africa',  subTab: 'Sexual' },
  { id: 'mi-stock-region',              style: 'bar',  tab: 'migration', region: 'Africa',  subTab: null },
];

/** Panel IDs that use vline annotations */
export const ANNOTATION_PANELS = [
  { id: 'fem-timeline', label: 'COVID', year: '2020', tab: 'violence' },
  { id: 'sx-totals',     label: 'LO 10/2022', year: '2022', tab: 'violence', subTab: 'Sexual' },
  { id: 'sx-clearance',  label: 'LO 10/2022', year: '2022', tab: 'violence', subTab: 'Sexual' },
  { id: 'sx-categories', label: 'LO 10/2022', year: '2022', tab: 'violence', subTab: 'Sexual' },
  { id: 'hc-totals',     label: 'no 2022', year: '2022', tab: 'violence', subTab: 'Odio' },
  { id: 'mi-inflow',     label: 'EVR→EMCR', year: '2008', tab: 'migration' },
];

/** Switch to a main tab by clicking its button */
export async function switchTab(page, tabId) {
  const tabBar = page.locator('#main-tabs');
  const btn = tabBar.locator(`button[data-id="${tabId}"]`);
  await btn.click();
  await page.waitForTimeout(500); // allow panels to mount
}

/** Switch to a sub-tab within the violence section */
export async function switchSubTab(page, subTabLabel) {
  const subBar = page.locator('#sub-tabs');
  const btn = subBar.locator('button', { hasText: subTabLabel });
  await btn.click();
  await page.waitForTimeout(500);
}

/** Assert that a chart panel's canvas has a Chart.js instance */
export async function expectChartMounted(page, panelId) {
  const mounted = await page.evaluate((id) => {
    const p = document.getElementById(id);
    return !!(p && p._chart && p._chart instanceof Chart);
  }, panelId);
  expect(mounted).toBe(true);
}

/** Get the chart instance's dataset count */
export async function getDatasetCount(page, panelId) {
  return page.evaluate((id) => document.getElementById(id)._chart.data.datasets.length, panelId);
}

/** Get the names of chart datasets (labels) */
export async function getDatasetLabels(page, panelId) {
  return page.evaluate((id) =>
    document.getElementById(id)._chart.data.datasets.map(d => d.label),
    panelId);
}

/** Get chart options.scales.y.stacked */
export async function getYStacked(page, panelId) {
  return page.evaluate((id) =>
    document.getElementById(id)._chart.options.scales.y.stacked,
    panelId);
}

/** Click a legend item by its text label. Returns true if item found. */
export async function clickLegendItem(page, panelId, label) {
  return page.evaluate(({ id, txt }) => {
    const c = document.getElementById(id)._chart;
    const legend = c.legend;
    const idx = legend.legendItems.findIndex(i => i.text === txt);
    if (idx === -1) return false;
    const hb = legend.legendHitBoxes[idx];
    const rect = c.canvas.getBoundingClientRect();
    const x = rect.left + hb.left + hb.width / 2;
    const y = rect.top + hb.top + hb.height / 2;
    // dispatch real mouse event on the canvas
    const evt = new MouseEvent('click', { clientX: x, clientY: y, bubbles: true });
    c.canvas.dispatchEvent(evt);
    return true;
  }, { id: panelId, txt: label });
}

/** Click a data element (line/bar point) by dataset index and data index. */
export async function clickDataElement(page, panelId, datasetIndex, dataIndex = 0) {
  await page.evaluate(({ id, dsIdx, di }) => {
    const c = document.getElementById(id)._chart;
    const meta = c.getDatasetMeta(dsIdx);
    if (!meta || !meta.data || !meta.data[di]) return;
    const el = meta.data[di];
    const rect = c.canvas.getBoundingClientRect();
    const x = rect.left + el.x;
    const y = rect.top + el.y;
    const evt = new MouseEvent('click', { clientX: x, clientY: y, bubbles: true, cancelable: true });
    c.canvas.dispatchEvent(evt);
  }, { id: panelId, dsIdx: datasetIndex, di: dataIndex });
}

/** Check whether the chart seems to be in drilled-down state (has country-level datasets) */
export async function isDrilled(page, panelId) {
  return page.evaluate((id) => {
    const c = document.getElementById(id)._chart;
    const labels = c.data.datasets.map(d => d.label);
    // If any dataset label is a known country (not a region, not España, not ↩), we're drilled
    const regions = ['Africa','America','Asia','Europe','Other','EU','Non-EU Europe',
      'Latin America & Caribbean','North America & Oceania','Asia & Oceania'];
    const hasCountry = labels.some(l =>
      !regions.includes(l) && l !== 'España' && !l.startsWith('↩'));
    return hasCountry;
  }, panelId);
}

/** Wait for all chart panels in the tab to mount */
export async function waitForCharts(page, timeout = 8000) {
  await page.waitForFunction(() => {
    const panels = document.querySelectorAll('svs-chart-panel');
    return Array.from(panels).every(p => p._chart && p._chart instanceof Chart);
  }, { timeout });
}
