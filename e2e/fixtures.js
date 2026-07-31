// Custom `test`/`expect` wrapper: every spec imports from here instead of
// '@playwright/test' directly.
//
// docs/index.html loads Chart.js + the annotation plugin from cdn.jsdelivr.net
// (correct for the deployed site) and Google Fonts. Real browsers have real
// internet; a sandboxed/offline test runner may not — and even where it does,
// pinning e2e reliability to a third-party CDN being up is a flaky-test smell
// on its own. So every page load in this suite serves those specific requests
// from a local vendored copy (kept in sync with the versions pinned in
// docs/index.html — see e2e/vendor/README.md) and drops the Google Fonts
// requests, which are cosmetic and irrelevant to chart behavior.
import { test as base, expect } from '@playwright/test';
import path from 'node:path';

const VENDOR_DIR = path.join(__dirname, 'vendor');

export const test = base.extend({
  page: async ({ page }, use) => {
    await page.route('https://cdn.jsdelivr.net/npm/chart.js@*/dist/chart.umd.min.js', (route) =>
      route.fulfill({ path: path.join(VENDOR_DIR, 'chart.umd.min.js'), contentType: 'application/javascript' }));
    await page.route('https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@*/dist/chartjs-plugin-annotation.min.js', (route) =>
      route.fulfill({ path: path.join(VENDOR_DIR, 'chartjs-plugin-annotation.min.js'), contentType: 'application/javascript' }));
    // fulfill (not abort) — an aborted request logs a "Failed to load
    // resource" console error that would trip smoke.spec.js's zero-console-
    // errors check, for a request that's cosmetic (webfonts) and irrelevant
    // to chart behavior.
    await page.route('https://fonts.googleapis.com/**', (route) =>
      route.fulfill({ status: 200, contentType: 'text/css', body: '' }));
    await page.route('https://fonts.gstatic.com/**', (route) =>
      route.fulfill({ status: 200, contentType: 'font/woff2', body: '' }));
    await use(page);
  },
});

export { expect };
