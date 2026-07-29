import { expect } from '@playwright/test';

/**
 * Panel IDs that use regionDrilldownChart (drill-down capable).
 * `tab` is one of #main-tabs' data-id values: feminicides | sexual-crimes |
 * migration | hate-crimes. There are no sub-tabs in the current dashboard
 * (feminicides/sexual-crimes/hate-crimes were split off #main-tabs directly
 * — see docs/index.html's comment above <svs-confidence-filter>), so panel
 * entries only need a single `tab` id.
 *
 * `regions` is each panel's *actual* region-name set (straight from
 * docs/data/{sexual_crimes,migration}.json), used by isDrilled()/the
 * "switch region" test to tell a region-line label apart from a
 * drilled-in country label. sexual-crimes' two nationality panels and
 * sx-peligrosidad share one 5-region taxonomy (Africa/America/Asia/Europe/
 * Other); migration's stock-by-region panel uses a different 6-region set
 * (Africa/Latin America/Anglo/EU/Non-EU Europe/Asia) — an earlier version of
 * this file hardcoded one shared whitelist across both, which silently
 * mismatched migration's names ("Latin America"/"Anglo" vs. the sexual-crime
 * panels' "America"/"Other") and made isDrilled() report a false "drilled"
 * even at rest for mi-stock-region.
 *
 * `hasSpain` marks whether the panel's data includes a `spain` series (drawn
 * as the white "España" reference line) — true for both sexual-crimes
 * panels, false for mi-stock-region (migration's stock_by_region has no
 * `spain` key at all, so there's no España legend entry to test there).
 */
export const DRILL_PANELS = [
  { id: 'sx-nationality-victims', style: 'bar', tab: 'sexual-crimes', region: 'Africa', hasSpain: true,
    regions: ['Africa', 'America', 'Asia', 'Europe', 'Other'] },
  { id: 'sx-nationality-perpetrators', style: 'bar', tab: 'sexual-crimes', region: 'Africa', hasSpain: true,
    regions: ['Africa', 'America', 'Asia', 'Europe', 'Other'] },
  { id: 'sx-peligrosidad', style: 'line', tab: 'sexual-crimes', region: 'Africa', hasSpain: true,
    regions: ['Africa', 'America', 'Asia', 'Europe', 'Other'] },
  { id: 'mi-stock-region', style: 'bar', tab: 'migration', region: 'Africa', hasSpain: false,
    regions: ['Africa', 'Latin America', 'Anglo', 'EU', 'Non-EU Europe', 'Asia'] },
];

/** Panel IDs that use vline annotations */
export const ANNOTATION_PANELS = [
  { id: 'fem-timeline', label: 'COVID',        year: '2020', tab: 'feminicides' },
  { id: 'sx-totals',     label: 'LO 10/2022',  year: '2022', tab: 'sexual-crimes' },
  { id: 'sx-clearance',  label: 'LO 10/2022',  year: '2022', tab: 'sexual-crimes' },
  { id: 'sx-categories', label: 'LO 10/2022',  year: '2022', tab: 'sexual-crimes' },
  { id: 'mi-inflow',     label: 'EVR→EMCR',    year: '2008', tab: 'migration' },
  { id: 'hc-totals',     label: 'no 2022 report', year: '2022', tab: 'hate-crimes' },
];

/**
 * All chart-panel ids per top-level tab, straight off docs/index.html, for
 * smoke-testing "every panel in this tab actually mounts a chart with data".
 * Kept here (not derived from the DOM) so a panel silently missing from
 * app.js's `register()` calls still gets caught instead of the test just
 * shrinking to whatever happens to mount.
 */
export const TAB_PANELS = {
  feminicides: ['fem-timeline', 'fem-ageband', 'fem-ageband-perp', 'fem-counts', 'fem-rates'],
  'sexual-crimes': ['sx-totals', 'sx-clearance', 'sx-categories', 'sx-nationality-victims',
    'sx-nationality-perpetrators', 'sx-peligrosidad', 'sx-convictions'],
  migration: ['mi-inflow', 'mi-origin', 'mi-sex', 'mi-ageband', 'mi-ageprofile', 'mi-stock',
    'mi-stock-region', 'mi-age-pyramid', 'mi-age-pyramid-es', 'co-rateratio', 'co-share'],
  'hate-crimes': ['hc-totals', 'hc-categories'],
};

/** Switch to a main tab by clicking its button */
export async function switchTab(page, tabId) {
  const tabBar = page.locator('#main-tabs');
  const btn = tabBar.locator(`button[data-id="${tabId}"]`);
  await btn.click();
  await page.waitForTimeout(500); // allow panels to mount
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

/**
 * Check whether the chart seems to be in drilled-down state (has
 * country-level datasets). `regions` must be the panel's own real region
 * list (DRILL_PANELS[i].regions) — a label that isn't one of those, isn't
 * 'España', and isn't a '↩ ' back-handle can only be a drilled-in country.
 */
export async function isDrilled(page, panelId, regions) {
  return page.evaluate(({ id, regions }) => {
    const c = document.getElementById(id)._chart;
    const labels = c.data.datasets.map(d => d.label);
    return labels.some(l => !regions.includes(l) && l !== 'España' && !l.startsWith('↩'));
  }, { id: panelId, regions });
}

/**
 * Wait for the chart panels in the *currently active* tab to mount.
 * app.js's mountVisible() only builds panels whose `offsetParent` is non-null
 * (i.e. inside the visible .tab-panel), so panels belonging to other, still
 * hidden tabs never get a `_chart` — querying every <svs-chart-panel> on the
 * whole page (regardless of tab) would wait for a state the app never
 * reaches within a single tab view.
 */
export async function waitForCharts(page, timeout = 8000) {
  await page.waitForFunction(() => {
    const active = document.querySelector('.tab-panel.active');
    if (!active) return false;
    const panels = active.querySelectorAll('svs-chart-panel');
    return panels.length > 0 && Array.from(panels).every(p => p._chart && p._chart instanceof Chart);
  }, { timeout });
}

/**
 * True if at least one dataset on the chart has at least one real
 * (non-null/undefined/NaN) data point. Catches a panel that mounts a Chart.js
 * instance but was fed an empty/all-null series (e.g. a data-key rename that
 * silently broke a `d.<field>` lookup in app.js, or an upstream JSON that
 * regenerated with a gap for every year).
 */
export async function chartHasData(page, panelId) {
  return page.evaluate((id) => {
    const c = document.getElementById(id)._chart;
    return c.data.datasets.some((ds) => Array.isArray(ds.data) && ds.data.some((v) => {
      if (v === null || v === undefined) return false;
      if (typeof v === 'number') return !Number.isNaN(v);
      return true; // pyramid/object-form points etc.
    }));
  }, panelId);
}

/** Get the chart's annotation-plugin `annotations` map (vline markers etc.), or null if none configured. */
export async function getAnnotations(page, panelId) {
  return page.evaluate((id) => {
    const c = document.getElementById(id)._chart;
    return c.options?.plugins?.annotation?.annotations ?? null;
  }, panelId);
}
