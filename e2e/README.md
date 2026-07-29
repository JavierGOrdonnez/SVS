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
already fixed here). None of these are things a test suite should silently
decide, so they're flagged rather than papered over:

1. **Confidence filter is a no-op.** The pills (`svs-confidence-filter`,
   "Show confidence") wire up a `conf-change` event and every mounted panel
   does receive `refresh()`, but no chart builder in `docs/app.js` actually
   reads the `activeConf` argument it's given, and `<svs-chart-panel>` never
   hides itself based on its own `confidence` attribute either. Toggling a
   tier currently just tears down and rebuilds every chart with identical
   data — the control has no visible effect. `smoke.spec.js`'s
   confidence-filter test only checks the pill's own pressed-state/event
   wiring, not that anything downstream changes, since that behavior doesn't
   exist yet to test.
2. **No data-point click-to-drill.** `drilldown.spec.js` had a whole
   `test.skip`'d describe block ("drill-down via data-element click")
   asserting that clicking a bar/line point drills in, same as clicking its
   legend entry. `regionDrilldownChart()` only wires `plugins.legend.onClick`
   — there's no `options.onClick` at all, so nothing in the app currently
   supports that interaction. Left as `test.skip` (not deleted) pending a
   call on whether to build it or drop the tests.
3. **`mi-stock-region` has no España reference line.** Unlike the two
   sexual-crimes drill panels, `docs/data/migration.json`'s
   `stock_by_region` has no `spain` key at all, so there's no "clicking
   España does nothing" case to test there — that one test is skipped for
   this panel only (see `hasSpain` in `helpers.js`'s `DRILL_PANELS`). Worth
   a look at whether that's intentional or just an omission from T68.

One real bug (not just a test-writing bug) *was* fixed as part of getting
green: `docs/app.js`'s `↩`-back-handle click handler reset `drilled` and
rebuilt the datasets, but never reset `scales.x/y.stacked` (or `y.max`) back
off — so drilling into a region's bar-mode chart and clicking back out left
the chart's axes still configured as if drilled in.
