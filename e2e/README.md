# SVS dashboard — Playwright e2e suite

Drives the built dashboard (`docs/`) in a real headless Chromium against the
static `docs/data/*.json` snapshot already checked in — no backend, no
mocking. `playwright.config.js` boots `src/serve.py` (no-auth) itself, so
`npm test` is the only command needed.

```
cd e2e
npm install
npm test              # everything
npm run test:smoke       # per-panel mount + data + caveat/headline checks
npm run test:drilldown   # region-drilldown interaction (legend/point clicks)
npm run test:annotation  # vline break/milestone markers
```

## Scope

Depth coverage currently targets the three tabs that have had a dedicated
data-quality pass: **feminicides**, **sexual crime**, **migration & cohorts**.
Hate crime has only the pre-existing `hc-totals` annotation check (it was
already in `ANNOTATION_PANELS` from earlier work) — no smoke/panel-list
coverage yet. Extend `TAB_PANELS` / the `TABS` array in `smoke.spec.js` when
that tab gets the same pass.

## Known gaps found while writing this suite

Three product-level questions surfaced while making the suite actually pass
in a real browser (the previous version, added in "Add playwright drilldown
tests", had never been run against one — every one of its tests failed
outright once executed, for reasons below plus a couple of test-only bugs
already fixed here). None of these were things a test suite should silently
decide, so they were flagged for the user rather than papered over. Two are
now resolved:

1. **Confidence filter is a no-op — still open.** The pills
   (`svs-confidence-filter`, "Show confidence") wire up a `conf-change` event
   and every mounted panel does receive `refresh()`, but no chart builder in
   `docs/app.js` actually reads the `activeConf` argument it's given, and
   `<svs-chart-panel>` never hides itself based on its own `confidence`
   attribute either. Toggling a tier currently just tears down and rebuilds
   every chart with identical data — the control has no visible effect.
   `smoke.spec.js`'s confidence-filter test only checks the pill's own
   pressed-state/event wiring, not that anything downstream changes, since
   that behavior doesn't exist yet to test.
2. **~~No data-point click-to-drill.~~ Resolved.** `regionDrilldownChart()`
   only wired `plugins.legend.onClick`; clicking a bar/line point directly
   did nothing. Built via TDD (un-skipped the existing test, confirmed it
   failed, then implemented): a shared `handleRegionClick()` now backs both
   the legend's `onClick` and a new top-level `onClick` that does its own
   `getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true)`
   hit-test — deliberately *not* reusing the `elements` Chart.js's default
   click handling passes in, since that follows `baseOpts`' hover
   `interaction: { mode: 'index', intersect: false }` (tuned for tooltips)
   and would return one element per dataset at the nearest x-index
   regardless of which one was actually clicked, which would have made
   every click drill into whichever region happens to be first in the
   dataset array. `drilldown.spec.js` has a regression test for exactly that
   failure mode (clicking a *non-first* region's point).
3. **~~`mi-stock-region` has no España reference line.~~ Resolved** — was an
   omission, not intentional. Added a `spain` series to `stock_by_region`
   (`src/migration/build_dashboard_data.py`, `_spain_stock_series()`): INE
   Padrón total population minus the 50-nationality foreign stock, same
   subtraction approach the T70 Spanish age pyramid already uses. First cut
   put it on the shared axis and made every region line unreadable (Spain's
   ~40M dwarfs any region's ~1-2.5M) — screenshotted and confirmed with the
   user before proceeding. Now on its own secondary axis
   (`regionDrilldownChart`'s new `opts.spainSecondaryAxis`, opt-in per panel
   since the sexual-crimes drill panels' own `spain` series is already the
   same order of magnitude as their region series and doesn't need this).
   The user also asked for a %-of-total-population share line; added as a
   dashed secondary-axis series on `mi-stock` instead (`foreign_pct_of_total`
   in `stock_trend`), which already had a single raw-count line and room for
   a normalized companion, rather than on `mi-stock-region`.

One real bug (not just a test-writing bug) *was* fixed as part of getting
green: `docs/app.js`'s `↩`-back-handle click handler reset `drilled` and
rebuilt the datasets, but never reset `scales.x/y.stacked` (or `y.max`) back
off — so drilling into a region's bar-mode chart and clicking back out left
the chart's axes still configured as if drilled in.
