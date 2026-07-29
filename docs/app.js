// SVS dashboard bootstrap.
// Fetches the generated data layer (docs/data/*.json), wires the tab bars and
// confidence filter, and assigns a Chart.js builder to each <svs-chart-panel>.
// Charts mount lazily when their tab first becomes visible (Chart.js needs the
// canvas laid out) and refresh when the confidence filter changes.

import './components/stat-card.js';
import './components/confidence-badge.js';
import './components/source-cite.js';
import './components/caveat-list.js';
import './components/legend.js';
import './components/chart-panel.js';
import './components/tab-bar.js';
import './components/confidence-filter.js';

/* ── palette + Chart.js defaults ─────────────────────── */
const CSS = getComputedStyle(document.documentElement);
const tok = (n, fb) => (CSS.getPropertyValue(n).trim() || fb);
const CONF = {
  high: tok('--high', '#22c55e'), medium: tok('--medium', '#eab308'),
  low: tok('--low', '#f97316'), unverified: tok('--unverified', '#ef4444'),
};
const ACCENT = tok('--accent', '#7c83ff');
const PALETTE = ['#7c83ff', '#22c55e', '#eab308', '#f472b6', '#06b6d4', '#f97316', '#a855f7', '#60a5fa'];
const GRID = 'rgba(255,255,255,0.06)', TICK = '#6b7280';

Chart.defaults.font.family = tok('--font-body', 'system-ui');
Chart.defaults.color = TICK;

function baseOpts(extra = {}) {
  return {
    responsive: true, maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#22263a', borderColor: '#2e3347', borderWidth: 1,
        titleColor: '#fff', bodyColor: '#9ba3bf', padding: 10,
      },
      ...(extra.plugins || {}),
    },
    scales: {
      x: { grid: { color: GRID }, ticks: { color: TICK, font: { size: 11 } }, ...(extra.x || {}) },
      y: { grid: { color: GRID }, ticks: { color: TICK, font: { size: 11 } }, beginAtZero: true, ...(extra.y || {}) },
      ...(extra.scales || {}),
    },
  };
}

// a break-year vertical marker for the annotation plugin
function vline(x, label, color = ACCENT) {
  return { type: 'line', xMin: x, xMax: x, borderColor: color, borderWidth: 1, borderDash: [4, 4],
    label: { display: true, content: label, color, backgroundColor: 'rgba(15,17,23,0.85)', font: { size: 9 }, position: 'start' } };
}
// dim a '#rrggbb' color to a lower alpha, e.g. for provisional/not-yet-consolidated bars
function fadeAlpha(hex, factor = 0.35) {
  const r = parseInt(hex.slice(1, 3), 16), g = parseInt(hex.slice(3, 5), 16), b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${factor})`;
}
// midpoint age (years) of a band label, handling both the Spanish
// "N a M años" / "N años o más" and migration "N-M" / "N+" formats, plus
// open-ended-low bands ("<N años"). Open-ended-high bands ("o más"/"+")
// get a +7.5y nudge past their floor so they sit past the preceding
// closed band on the 0-100 colormap domain; open-ended-low bands ("<N")
// instead take the floor's lower half (N/2) so they sort/color youngest.
function ageMidpoint(label) {
  if (label.startsWith('<')) {
    const lt = label.match(/(\d+)/);
    return lt ? Number(lt[1]) / 2 : 0;
  }
  const range = label.match(/(\d+)\D+(\d+)/);
  if (range) return (Number(range[1]) + Number(range[2])) / 2;
  const open = label.match(/(\d+)/);
  return open ? Number(open[1]) + 7.5 : 50;
}
// continuous age colormap: red (young) -> blue (old) hue sweep, fixed to
// a 0-100y domain so the same age always maps to the same color across charts.
function hslToHex(h, s, l) {
  s /= 100; l /= 100;
  const k = (n) => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = (n) => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
  const toHex = (x) => Math.round(255 * x).toString(16).padStart(2, '0');
  return `#${toHex(f(0))}${toHex(f(8))}${toHex(f(4))}`;
}
function ageColor(age) {
  const t = Math.max(0, Math.min(1, age / 100));
  return hslToHex(t * 220, 65, 58);
}
// trailing 5-year moving average that skips nulls (band/actor not
// applicable that year) rather than treating them as 0; all-null windows
// stay null so genuinely inapplicable spans (e.g. a legacy-only band past
// 2005) render as a true gap, not a fabricated flat line.
function movingAvg5(values, window = 5) {
  return values.map((_, i) => {
    const span = values.slice(Math.max(0, i - window + 1), i + 1).filter(v => v !== null && v !== undefined);
    return span.length ? span.reduce((a, b) => a + b, 0) / span.length : null;
  });
}
const line = (label, data, color, extra = {}) => ({
  label, data, borderColor: color, backgroundColor: color + '22',
  borderWidth: 2, tension: 0.25, pointRadius: 2, pointHoverRadius: 4, ...extra,
});

// Shared region-drilldown chart (migration's T68/T72 mi-stock-region, reused
// for sexual-crimes' victim/perpetrator nationality panels). `s` is
// {years, regions, series: {region: [...]}, by_country: {region: {countries,
// series}}}. Click a region's legend entry to swap its line for a stacked
// bar chart of that region's top-N countries + "Other" (the by_country data
// is always derived from the same rows the region line itself sums, so the
// parts sum exactly to the whole); the other regions' lines stay visible,
// dimmed, and remain clickable to switch the drill target. Click the same
// region's entry again (a hidden zero-data "back" dataset standing in for
// its line) to return to the aggregate view. Base chart type is 'bar'
// (needed for the stacked group) with region series overriding
// `type: 'line'` per-dataset — Chart.js 4.x supports this mixed combo
// natively.
function regionDrilldownChart(cv, s, opts = {}) {
  const drillStyle = opts.drillStyle || 'bar';   // 'bar' (migration stock) | 'line' (peligrosidad)
  let drilled = null; // null = aggregate view, else a region name
  const hasSpain = 'spain' in s;
  // mi-stock-region's España line is Spain's total resident population
  // (~40M) against region lines in the hundreds-of-thousands to low
  // millions — sharing one axis flattens every region to a line hugging
  // zero. sexual-crimes' two nationality panels don't have this problem
  // (their `spain` series is the same unit/order-of-magnitude as the
  // region series), so the secondary axis is opt-in per panel, not
  // automatic just because `spain` exists.
  const spainOnSecondaryAxis = !!opts.spainSecondaryAxis;
  let chart;

  const regionColor = (region) => PALETTE[s.regions.indexOf(region) % PALETTE.length];

  function spainDataset() {
    if (!hasSpain) return null;
    return { type: 'line', label: 'España', data: s.spain,
      borderColor: '#fff', backgroundColor: '#fff22',
      borderWidth: 3, pointRadius: 3, pointHoverRadius: 5,
      tension: 0.2, _region: 'España', stack: 'spain',
      ...(spainOnSecondaryAxis ? { yAxisID: 'y1' } : {}) };
  }

  function barAxisMax(region) {   // only used in 'bar' mode
    const bc = s.by_country[region];
    const perYearTotal = s.years.map((_, yi) =>
      bc.countries.reduce((sum, name) => sum + bc.series[name][yi], 0));
    return Math.round(Math.max(...perYearTotal) * 1.1);
  }

  function regionLine(region, extra = {}) {
    const color = regionColor(region);
    return { type: 'line', label: region, data: s.series[region], borderColor: color,
      backgroundColor: color + '22', borderWidth: 2, tension: 0.25,
      pointRadius: 2, pointHoverRadius: 4, _region: region, stack: `line-${region}`, ...extra };
  }

  function buildDatasets() {
    const spain = spainDataset();
    if (!drilled) {
      const regions = s.regions.map((r) => regionLine(r));
      return spain ? [...regions, spain] : regions;
    }

    const dimmed = s.regions.filter((r) => r !== drilled).map((r) => regionLine(r, {
      borderColor: regionColor(r) + '55', backgroundColor: 'transparent',
      borderWidth: 1, borderDash: [3, 3], pointRadius: 0, order: 1,
    }));
    const bc = s.by_country[drilled];

    if (drillStyle === 'line') {
      // Line mode: dashed country lines + solid region reference line.
      // The drilled region's own line stays as a visual reference; clicking
      // it in the legend (same _region) toggles back to aggregate view.
      const reference = regionLine(drilled, { order: 0 });
      const countries = bc.countries.map((name, i) => ({
        type: 'line', label: name, data: bc.series[name],
        borderColor: PALETTE[i % PALETTE.length], backgroundColor: 'transparent',
        borderWidth: 1.5, borderDash: [4, 3], pointRadius: 1.5, pointHoverRadius: 4,
        tension: 0.2, order: 2,
      }));
      const result = [reference, ...dimmed, ...countries];
      if (spain) result.push(spain);
      return result;
    }

    // Bar mode (default): stacked country bars replace the region line.
    // A visible "↩" back-handle click target replaces the region's legend entry.
    const backHandle = { type: 'line', label: '↩ ' + drilled, data: s.years.map(() => null),
      borderColor: regionColor(drilled), pointRadius: 0, showLine: false,
      order: 0, _region: drilled, stack: `line-${drilled}-back` };
    const bars = bc.countries.map((name, i) => ({
      type: 'bar', label: name, data: bc.series[name],
      backgroundColor: PALETTE[i % PALETTE.length] + 'cc',
      borderColor: PALETTE[i % PALETTE.length], borderWidth: 1, stack: 'countries', order: 2,
    }));
    const result = [backHandle, ...dimmed, ...bars];
    if (spain) result.push(spain);
    return result;
  }

  const yMax = opts.yMax;

  // Shared by the legend-click and data-point-click handlers below: applies
  // the drill/undrill/back-handle transition for a clicked label. Returns
  // true if `txt` was one of those (so the caller stops there); false means
  // it wasn't a region/back-handle label, so the caller can fall through to
  // whatever it does for a plain dataset label (legend does a show/hide
  // toggle; a chart-area point click does nothing — a country line isn't
  // itself drillable).
  function handleRegionClick(ci, txt) {
    if (txt === 'España') return true;
    if (txt.startsWith('↩ ')) {
      drilled = null;
      ci.data.datasets = buildDatasets();
      ci.options.scales.x.stacked = false;
      ci.options.scales.y.stacked = false;
      ci.options.scales.y.max = yMax;
      ci.update();
      return true;
    }
    if (s.regions.includes(txt)) {
      drilled = (drilled === txt) ? null : txt;
      ci.data.datasets = buildDatasets();
      ci.options.scales.x.stacked = !!(drilled && drillStyle === 'bar');
      ci.options.scales.y.stacked = !!(drilled && drillStyle === 'bar');
      ci.options.scales.y.max = (drilled && drillStyle === 'bar') ? barAxisMax(drilled) : yMax;
      ci.update();
      return true;
    }
    return false;
  }

  return new Chart(cv, {
    type: 'bar',
    data: { labels: s.years.map(String), datasets: buildDatasets() },
    options: {
      ...baseOpts({
        x: { stacked: false },
        y: { stacked: false, beginAtZero: true, max: yMax },
        scales: spainOnSecondaryAxis ? {
          y1: {
            position: 'right', beginAtZero: false,
            grid: { drawOnChartArea: false },
            ticks: { color: TICK, font: { size: 11 }, callback: (v) => (v / 1e6).toFixed(0) + 'M' },
          },
        } : {},
        plugins: {
          legend: {
            display: true,
            labels: { color: TICK, boxWidth: 10, font: { size: 10 } },
            onClick: function(evt, item, _legend) {
              const ci = (_legend && _legend.chart) || (this && this.chart);
              if (!ci) return;
              if (handleRegionClick(ci, item.text)) return;
              const i = item.datasetIndex;
              if (ci.isDatasetVisible(i)) { ci.hide(i); item.hidden = true; }
              else { ci.show(i); item.hidden = false; }
            },
          },
        },
      }),
      // Clicking a region's line/bar directly (not just its legend entry)
      // drills in the same way. baseOpts' `interaction: { mode: 'index',
      // intersect: false }` is tuned for hover tooltips (one element per
      // dataset at the nearest x, regardless of which one the cursor is
      // actually over) and would misidentify which region was clicked if
      // reused here, so this does its own precise hit-test instead of
      // trusting the `elements` Chart.js passes in.
      onClick: (evt, _elements, chart) => {
        const hits = chart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
        if (!hits.length) return;
        const ds = chart.data.datasets[hits[0].datasetIndex];
        handleRegionClick(chart, ds.label);
      },
    },
  });
}

/* ── data + panel registry ───────────────────────────── */
const DATA = {};
const builders = {};          // id -> (canvas, activeConf) => Chart
let activeConf = { high: true, medium: true, low: true, unverified: false };
const panel = (id) => document.getElementById(id);

function register(id, fn) { builders[id] = fn; const p = panel(id); if (p) p.builder = fn; }

function mountVisible() {
  document.querySelectorAll('svs-chart-panel').forEach(p => {
    if (p.offsetParent !== null && !p._chart && p._builder) p.mount(activeConf);
  });
}

/* ── chart builders per domain ───────────────────────── */
const FEM_AXIS_START = 2003, FEM_AXIS_END = 2025;
const FEM_AXIS_YEARS = Array.from({ length: FEM_AXIS_END - FEM_AXIS_START + 1 }, (_, i) => FEM_AXIS_START + i);

function buildFeminicides() {
  const d = DATA.feminicides;

  register('fem-timeline', (cv) => {
    const raw = d.timeline;
    // clip to the shared 2003-2025 axis (all feminicide panels line up)
    const idxs = raw.years.map((_, i) => i).filter(i => raw.years[i] >= FEM_AXIS_START && raw.years[i] <= FEM_AXIS_END);
    const t = {
      age_breakdown: idxs.map(i => raw.age_breakdown[i]),
      has_age_breakdown: idxs.map(i => raw.has_age_breakdown[i]),
      provisional: idxs.map(i => raw.provisional[i]),
      values: idxs.map(i => raw.values[i]),
      values_ma5: idxs.map(i => raw.values_ma5[i]),
    };
    const years = idxs.map(i => raw.years[i]);
    const provFactor = 0.35;

    // union of age-band labels, in ascending-age order (2003-2005 have none)
    const bandLabels = [];
    t.age_breakdown.forEach(ab => { if (ab) ab.forEach(a => { if (!bandLabels.includes(a.label)) bandLabels.push(a.label); }); });
    bandLabels.sort((a, b) => ageMidpoint(a) - ageMidpoint(b));

    const bandDatasets = bandLabels.map((label) => {
      const color = ageColor(ageMidpoint(label));
      return {
        label,
        data: years.map((_, yi) => {
          const ab = t.age_breakdown[yi];
          if (!ab) return null;
          const entry = ab.find(a => a.label === label);
          return entry ? entry.victims : 0;
        }),
        backgroundColor: years.map((_, yi) => t.provisional[yi] ? fadeAlpha(color, provFactor) : color + 'cc'),
        borderColor: color, borderWidth: 1, stack: 's',
      };
    });

    // 2003-2005: no age breakdown in the source (legacy-format stub reports),
    // so render as a single solid bar instead of a stack for those years only.
    const legacyDataset = {
      label: 'Total (no age breakdown)',
      data: years.map((_, yi) => t.has_age_breakdown[yi] ? null : t.values[yi]),
      backgroundColor: years.map((_, yi) => t.provisional[yi] ? fadeAlpha(TICK, provFactor) : ACCENT + '99'),
      borderColor: ACCENT, borderWidth: 1, stack: 's',
    };

    const ma5Dataset = {
      type: 'line', label: '5-year moving average', data: t.values_ma5,
      borderColor: '#fff', backgroundColor: 'transparent', borderWidth: 2,
      borderDash: [6, 3], pointRadius: 0, tension: 0.2, order: -1, stack: 'ma5',
    };

    const annotations = { covid: vline(String(2020), 'COVID', '#60a5fa') };
    d.milestones.forEach((m, i) => { annotations['ms' + i] = vline(String(m.year), m.label, '#a855f7'); });

    return new Chart(cv, {
      type: 'bar',
      data: { labels: years.map(String), datasets: [legacyDataset, ...bandDatasets, ma5Dataset] },
      options: baseOpts({
        x: { stacked: true, grid: { color: GRID }, ticks: { color: TICK } },
        y: { stacked: true, beginAtZero: true, grid: { color: GRID }, ticks: { color: TICK } },
        plugins: {
          legend: { display: true, labels: { color: TICK, boxWidth: 10, font: { size: 10 } } },
          annotation: { annotations },
          tooltip: { callbacks: { footer: (items) => {
            const yi = items[0]?.dataIndex;
            return t.provisional[yi] ? 'Provisional — year not yet consolidated' : '';
          } } },
        },
      }),
    });
  });

  // each age band as its own (non-stacked) 5-year-moving-average line,
  // same colors as the fem-timeline stack, to show whether declines are
  // age-group-specific or general across bands. Smoothed (not raw
  // per-year values) to cut small-subgroup year-to-year noise. One
  // builder shared between the victims and perpetrators variants.
  function buildAgeBandChart(cv, actorKey) {
    const raw = d.timeline;
    const idxs = raw.years.map((_, i) => i).filter(i => raw.years[i] >= FEM_AXIS_START && raw.years[i] <= FEM_AXIS_END);
    const years = idxs.map(i => raw.years[i]);
    const ab = idxs.map(i => raw.age_breakdown[i]);

    const bandLabels = [];
    ab.forEach(a => { if (a) a.forEach(x => { if (x[actorKey] != null && !bandLabels.includes(x.label)) bandLabels.push(x.label); }); });
    bandLabels.sort((a, b) => ageMidpoint(a) - ageMidpoint(b));

    const datasets = bandLabels.map((label) => {
      const color = ageColor(ageMidpoint(label));
      const series = years.map((_, yi) => {
        const entry = ab[yi] && ab[yi].find(x => x.label === label);
        return entry ? entry[actorKey] : null;
      });
      return line(label, movingAvg5(series), color, { spanGaps: false });
    });

    return new Chart(cv, {
      type: 'line',
      data: { labels: years.map(String), datasets },
      options: baseOpts({
        plugins: {
          legend: { display: true, labels: { color: TICK, boxWidth: 10, font: { size: 10 } } },
          annotation: { annotations: { covid: vline(String(2020), 'COVID', '#60a5fa') } },
        },
      }),
    });
  }
  register('fem-ageband', (cv) => buildAgeBandChart(cv, 'victims'));
  register('fem-ageband-perp', (cv) => buildAgeBandChart(cv, 'perps'));

  // shared by fem-counts/fem-rates: one line per origin x role (color =
  // origin, dash = perpetrator), plotted over the shared 2003-2025 axis
  // with true gaps (no data before 2006 or after 2024).
  function buildOriginRoleChart(cv, valueKey, afterLabel) {
    const rows = d.rates.rows;
    const origins = ['españa', 'otro_pais'];
    const originLabel = { 'españa': 'Spanish', 'otro_pais': 'Foreign-born' };
    const originColor = { 'españa': PALETTE[0], 'otro_pais': PALETTE[4] };
    const roles = ['victim', 'perpetrator'];
    const roleLabel = { victim: 'victims', perpetrator: 'perpetrators' };
    const byKey = {};
    rows.forEach(r => { byKey[`${r.year}|${r.origin}|${r.role}`] = r; });

    const datasets = [];
    origins.forEach(o => roles.forEach(role => {
      const color = originColor[o];
      datasets.push({
        label: `${originLabel[o]} — ${roleLabel[role]}`,
        data: FEM_AXIS_YEARS.map(y => byKey[`${y}|${o}|${role}`]?.[valueKey] ?? null),
        borderColor: color, backgroundColor: color + '22', borderWidth: 2,
        borderDash: role === 'perpetrator' ? [5, 4] : [],
        pointRadius: 2, pointHoverRadius: 4, tension: 0.2, spanGaps: false,
      });
    }));

    return new Chart(cv, {
      type: 'line',
      data: { labels: FEM_AXIS_YEARS.map(String), datasets },
      options: baseOpts({
        plugins: {
          legend: { display: true, labels: { color: TICK, boxWidth: 10, font: { size: 10 } } },
          tooltip: { callbacks: { afterLabel: (c) => {
            const o = origins[Math.floor(c.datasetIndex / 2)], role = roles[c.datasetIndex % 2];
            const row = byKey[`${FEM_AXIS_YEARS[c.dataIndex]}|${o}|${role}`];
            return row ? afterLabel(row, roleLabel[role]) : '';
          } } },
        },
      }),
    });
  }

  register('fem-counts', (cv) => buildOriginRoleChart(cv, 'count',
    (row, roleLabel) => `${(row.population / 1e6).toFixed(1)}M ${row.origin === 'españa' ? 'Spanish-resident' : 'foreign-resident'} population`));

  register('fem-rates', (cv) => buildOriginRoleChart(cv, 'rate_per_100k',
    (row, roleLabel) => `${row.count} ${roleLabel} / ${(row.population / 1e6).toFixed(1)}M`));
}

function buildSexual() {
  const d = DATA.sexual_crimes;

  // T-sx-totals: 2016-2018 Anuario, 2019-2024 Informe, 2025 Balance
  // (provisional) — bars colored by source confidence; Balance's own
  // independent quarterly total overlaid as a dashed line wherever it
  // exists (diverges visibly from Anuario/Informe from 2022 on, B24).
  register('sx-totals', (cv) => {
    const t = d.totals;
    const sourceColor = { anuario: fadeAlpha(ACCENT, 0.55), informe: ACCENT + 'cc', balance: fadeAlpha(ACCENT, 0.35) };
    const sourceLabel = { anuario: 'Anuario Estadístico', informe: 'Informe', balance: 'Balance de Criminalidad (provisional)' };
    const bars = {
      type: 'bar', label: 'Reported total', data: t.total,
      backgroundColor: t.source.map((s) => sourceColor[s]), borderColor: ACCENT, borderWidth: 1, order: 2,
    };
    const balanceLine = {
      type: 'line', label: 'Balance total (independent, quarterly)', data: t.balance_total,
      borderColor: '#fff', backgroundColor: 'transparent', borderDash: [4, 3], borderWidth: 2,
      pointRadius: 2, tension: 0.15, spanGaps: false, order: 1,
    };
    return new Chart(cv, {
      type: 'bar',
      data: { labels: t.years.map(String), datasets: [bars, balanceLine] },
      options: baseOpts({
        plugins: {
          legend: { display: true, labels: { color: TICK, boxWidth: 10, font: { size: 10 } } },
          annotation: { annotations: { lo: vline(String(2022), 'LO 10/2022', CONF.low) } },
          tooltip: { callbacks: { footer: (items) => `Source: ${sourceLabel[t.source[items[0]?.dataIndex]]}` } },
        },
      }),
    });
  });

  register('sx-clearance', (cv) => {
    // clearance_rate is null for 2025 (Balance doesn't publish it) — drop
    // that trailing year entirely rather than showing an empty tick that'd
    // contradict the panel's own "2016-2024" subtitle.
    const idxs = d.totals.years.map((_, i) => i).filter((i) => d.totals.clearance_rate[i] != null);
    const years = idxs.map((i) => d.totals.years[i]);
    const rates = idxs.map((i) => d.totals.clearance_rate[i]);
    return new Chart(cv, {
      type: 'line',
      data: { labels: years.map(String), datasets: [line('Clearance rate', rates, PALETTE[1], { fill: true })] },
      options: baseOpts({
        y: { min: 0, max: 100, ticks: { color: TICK, callback: (v) => v + '%' } },
        plugins: { annotation: { annotations: { lo: vline(String(2022), 'LO 10/2022', CONF.low) } } },
      }),
    });
  });

  // T-sx-cat: all categories (not just the first 6), pre/post-LO10/2022
  // naming already unified in build_dashboard_data.py.
  register('sx-categories', (cv) => {
    const s = d.categories.series, keys = Object.keys(s);
    return new Chart(cv, {
      type: 'bar',
      data: { labels: d.categories.years.map(String), datasets: keys.map((k, i) => ({
        label: k.replace(/_unified$/, '').replace(/_/g, ' '), data: s[k],
        backgroundColor: PALETTE[i % PALETTE.length] + 'cc', borderColor: PALETTE[i % PALETTE.length],
        borderWidth: 1, stack: 's',
      })) },
      options: baseOpts({
        x: { stacked: true }, y: { stacked: true, beginAtZero: true },
        plugins: {
          legend: { display: true, labels: { color: TICK, boxWidth: 10, font: { size: 9 } } },
          annotation: { annotations: { lo: vline(String(2022), 'LO 10/2022', CONF.low) } },
        },
      }),
    });
  });

  register('sx-nationality-victims', (cv) => regionDrilldownChart(cv, d.nationality_victims, { drillStyle: 'bar' }));
  register('sx-nationality-perpetrators', (cv) => regionDrilldownChart(cv, d.nationality_perpetrators, { drillStyle: 'bar' }));

  // Peligrosidad: perpetrators % males 15-59 by nationality (region drill-down)
  register('sx-peligrosidad', (cv) => regionDrilldownChart(cv, d.peligrosidad, { drillStyle: 'line', yMax: 0.5 }));

  register('sx-convictions', (cv) => {
    const c = d.convictions;
    const drop = new Set(['total']);
    const groups = c.groups.filter(g => !drop.has(g) && c.series[g].some(v => v > 0));
    return new Chart(cv, {
      type: 'bar',
      data: { labels: c.years, datasets: groups.map((g, i) => ({
        label: g.replace(/_/g, ' '), data: c.series[g], backgroundColor: PALETTE[i % PALETTE.length] + 'cc', stack: 's' })) },
      options: baseOpts({ x: { stacked: true, grid: { color: GRID }, ticks: { color: TICK } }, y: { stacked: true, beginAtZero: true, grid: { color: GRID }, ticks: { color: TICK } } }),
    });
  });
}

function buildHate() {
  const d = DATA.hate_crimes;

  register('hc-totals', (cv) => new Chart(cv, {
    type: 'line',
    data: { labels: d.totals.years.map(String), datasets: [line('Hate crimes reported', d.totals.total, CONF.low, { fill: true, spanGaps: false })] },
    options: baseOpts({ plugins: { annotation: { annotations: { gap: vline(String(d.gap_year), 'no 2022 report', TICK) } } } }),
  }));

  register('hc-categories', (cv) => {
    const s = d.categories.series, keys = d.categories.categories.slice(0, 6);
    return new Chart(cv, {
      type: 'line',
      data: { labels: d.categories.years, datasets: keys.map((k, i) => line(k.replace(/_/g, ' '), s[k], PALETTE[i % PALETTE.length])) },
      options: baseOpts(),
    });
  });
}

function buildMortality() {
  const d = DATA.mortality;
  register('mo-allcause', (cv) => new Chart(cv, { type: 'line',
    data: { labels: d.all_cause_by_sex.years, datasets: [line('Male', d.all_cause_by_sex.male, PALETTE[4]), line('Female', d.all_cause_by_sex.female, PALETTE[3])] },
    options: baseOpts() }));
  register('mo-chapter', (cv) => { const s = d.female_chapter_over_time; return new Chart(cv, { type: 'line',
    data: { labels: s.years, datasets: s.chapters.map((c, i) => line(c, s.series[c], PALETTE[i % PALETTE.length], { fill: true, stack: 's', tension: 0.2 })) },
    options: baseOpts({ y: { stacked: true, beginAtZero: true, grid: { color: GRID }, ticks: { color: TICK } } }) }); });
  register('mo-ageprofile', (cv) => { const s = d.female_age_profile_latest; return new Chart(cv, { type: 'line',
    data: { labels: s.ages, datasets: Object.keys(s.series).map((k, i) => line(k, s.series[k], PALETTE[i % PALETTE.length])) },
    options: baseOpts({ x: { grid: { color: GRID }, ticks: { color: TICK, font: { size: 9 } } } }) }); });
  register('mo-external', (cv) => { const s = d.female_external_over_time; return new Chart(cv, { type: 'line',
    data: { labels: s.years, datasets: Object.keys(s.series).map((k, i) => line(k, s.series[k], PALETTE[i % PALETTE.length])) },
    options: baseOpts() }); });
  register('mo-repro', (cv) => { const s = d.female_repro_over_time; return new Chart(cv, { type: 'line',
    data: { labels: s.years, datasets: Object.keys(s.series).map((k, i) => line(k, s.series[k], PALETTE[i % PALETTE.length])) },
    options: baseOpts() }); });
  register('mo-young', (cv) => { const s = d.female_young_top_causes; return new Chart(cv, { type: 'bar',
    data: { labels: s.labels, datasets: [{ data: s.deaths, backgroundColor: PALETTE.map(c => c + 'cc') }] },
    options: baseOpts({ x: { grid: { display: false }, ticks: { color: TICK, font: { size: 9 }, maxRotation: 60 } } }) }); });
}

function buildMigration() {
  const d = DATA.migration;
  register('mi-inflow', (cv) => new Chart(cv, { type: 'line',
    data: { labels: d.annual_inflow.years.map(String), datasets: [line('Immigration inflow', d.annual_inflow.values, ACCENT, { fill: true })] },
    options: baseOpts({ plugins: { annotation: { annotations: { br: vline(String(2008), 'EVR→EMCR', TICK) } } } }) }));
  register('mi-origin', (cv) => { const s = d.origin_composition; return new Chart(cv, { type: 'line',
    data: { labels: s.years, datasets: s.origins.map((o, i) => line(o, s.series[o], PALETTE[i % PALETTE.length])) },
    options: baseOpts() }); });
  register('mi-sex', (cv) => new Chart(cv, { type: 'line',
    data: { labels: d.sex_split.years, datasets: [line('Male', d.sex_split.male, PALETTE[4]), line('Female', d.sex_split.female, PALETTE[3])] },
    options: baseOpts() }));
  register('mi-ageband', (cv) => { const s = d.age_band_over_time; return new Chart(cv, { type: 'line',
    data: { labels: s.years, datasets: s.bands.map((b) => line(b, s.series[b], ageColor(ageMidpoint(b)), { fill: true, stack: 's', tension: 0.2 })) },
    options: baseOpts({ y: { stacked: true, beginAtZero: true, grid: { color: GRID }, ticks: { color: TICK } } }) }); });
  register('mi-ageprofile', (cv) => { const s = d.age_profile_latest; return new Chart(cv, { type: 'bar',
    data: { labels: s.ages, datasets: [{ data: s.values, backgroundColor: ACCENT + 'cc' }] },
    options: baseOpts({ x: { grid: { display: false }, ticks: { color: TICK, font: { size: 9 } } } }) }); });
  register('mi-stock', (cv) => { const s = d.stock_trend; return new Chart(cv, { type: 'line',
    data: { labels: s.years, datasets: [
      line('Foreign nationals (stock)', s.foreign_nationality, ACCENT, { fill: true }),
      line('% of total population', s.foreign_pct_of_total, '#fff',
        { fill: false, borderDash: [5, 4], pointRadius: 1.5, yAxisID: 'y1', spanGaps: false }),
    ] },
    options: baseOpts({
      plugins: { legend: { display: true, labels: { color: TICK, boxWidth: 10, font: { size: 10 } } } },
      scales: { y1: {
        position: 'right', beginAtZero: true,
        grid: { drawOnChartArea: false },
        ticks: { color: TICK, font: { size: 11 }, callback: (v) => v + '%' },
      } },
    }) }); });
  // T72: region-drilldown chart (shared with buildSexual()'s two nationality
  // panels — see regionDrilldownChart() below for the interaction).
  register('mi-stock-region', (cv) => regionDrilldownChart(cv, d.stock_by_region, { spainSecondaryAxis: true }));

  // population pyramids (T69/T70): horizontal bars, males negative/left,
  // females positive/right, oldest band at the top (reverse of PYRAMID_AGES'
  // young-to-old storage order) to match conventional pyramid layout.
  function pyramidOpts(maxAbs) {
    return {
      indexAxis: 'y',
      ...baseOpts({
        x: {
          stacked: true, min: -maxAbs * 1.05, max: maxAbs * 1.05,
          ticks: { color: TICK, font: { size: 10 }, callback: (v) => Math.round(Math.abs(v)).toLocaleString() },
        },
        y: { stacked: true, grid: { display: false } },
        plugins: {
          legend: { display: true, labels: { color: TICK, boxWidth: 10, font: { size: 10 },
            // de-dupe: the region pyramid repeats each region's label across
            // its male/female stacked datasets, so only keep the first
            filter: (item, data) => data.datasets.findIndex(ds => ds.label === item.text) === item.datasetIndex } },
          tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${Math.abs(c.raw).toLocaleString()}` } },
        },
      }),
    };
  }

  register('mi-age-pyramid', (cv) => {
    const s = d.stock_age_pyramid;
    const ages = [...s.ages].reverse();
    const regions = Object.keys(s.regions);
    const datasets = regions.flatMap((region, i) => {
      const color = PALETTE[i % PALETTE.length];
      const male = [...s.regions[region].male].reverse().map(v => -v);
      const female = [...s.regions[region].female].reverse();
      return [
        { label: region, data: male, backgroundColor: color + 'cc', borderColor: color, borderWidth: 1, stack: 'male', grouped: false },
        { label: region, data: female, backgroundColor: color + 'cc', borderColor: color, borderWidth: 1, stack: 'female', grouped: false },
      ];
    });
    const maxAbs = Math.max(...s.ages.map((_, i) => Math.max(s.male[i], s.female[i])));
    return new Chart(cv, { type: 'bar', data: { labels: ages, datasets }, options: pyramidOpts(maxAbs) });
  });

  register('mi-age-pyramid-es', (cv) => {
    const s = d.stock_age_pyramid_es;
    const ages = [...s.ages].reverse();
    const male = [...s.male].reverse().map(v => -v);
    const female = [...s.female].reverse();
    const datasets = [
      { label: 'Male', data: male, backgroundColor: PALETTE[4] + 'cc', borderColor: PALETTE[4], borderWidth: 1, stack: 'male', grouped: false },
      { label: 'Female', data: female, backgroundColor: PALETTE[3] + 'cc', borderColor: PALETTE[3], borderWidth: 1, stack: 'female', grouped: false },
    ];
    const maxAbs = Math.max(...s.ages.map((_, i) => Math.max(s.male[i], s.female[i])));
    return new Chart(cv, { type: 'bar', data: { labels: ages, datasets }, options: pyramidOpts(maxAbs) });
  });
}

function buildCohort() {
  const d = DATA.cohort_tenure;
  const grp = (obj) => Object.keys(obj);

  register('co-rateratio', (cv) => {
    const g = d.test_a_rate_ratio;
    const names = grp(g);
    const periods = g[names[0]].periods;
    return new Chart(cv, {
      type: 'bar',
      data: { labels: periods, datasets: names.map((n, i) => ({
        label: n, data: g[n].rate_ratio, backgroundColor: PALETTE[i % PALETTE.length] + 'cc', borderColor: PALETTE[i % PALETTE.length], borderWidth: 1 })) },
      options: baseOpts({ plugins: { annotation: { annotations: { base: { type: 'line', yMin: 1, yMax: 1, borderColor: '#fff5', borderWidth: 1, borderDash: [3, 3],
        label: { display: true, content: 'baseline = 1.0', color: '#9ba3bf', font: { size: 9 }, position: 'end' } } } },
        tooltip: { callbacks: { afterLabel: (c) => { const n = names[c.datasetIndex]; const p = g[n].p_value[c.dataIndex]; return `p = ${p != null ? p.toFixed(4) : 'n/a'} · ${g[n].call[c.dataIndex]}`; } } } },
        y: { beginAtZero: false, grid: { color: GRID }, ticks: { color: TICK } } }),
    });
  });

  register('co-share', (cv) => {
    const g = d.test_c_share;
    const names = grp(g);
    const periods = g[names[0]].periods;
    return new Chart(cv, {
      type: 'bar',
      data: { labels: names, datasets: periods.map((p, pi) => ({
        label: p, data: names.map(n => g[n].share_test_pct[pi]), backgroundColor: PALETTE[pi % PALETTE.length] + 'cc' })) },
      options: baseOpts({ x: { grid: { display: false }, ticks: { color: TICK, font: { size: 9 }, maxRotation: 30 } } }),
    });
  });
}

/* ── headline KPI cards (kept in sync with the data) ─── */
function setHeadlines() {
  const el = document.getElementById('headlines');
  if (!el) return;
  const fem = DATA.feminicides, sx = DATA.sexual_crimes, hc = DATA.hate_crimes;
  const femIdx = fem.timeline.years.indexOf(2024);
  const fem2024 = femIdx >= 0 ? fem.timeline.values[femIdx] : fem.timeline.values.at(-1);
  const victimRates = fem.rates.rows.filter(r => r.role === 'victim' && r.year === fem.rates.latest_year);
  const foreignRate = (victimRates.find(r => r.origin !== 'españa') || {}).rate_per_100k;
  const spainRate = (victimRates.find(r => r.origin === 'españa') || {}).rate_per_100k;
  const sx2024 = sx.totals.total.at(-1);
  const hcLatest = hc.totals.total.at(-1);
  const hcYear = hc.totals.years.at(-1);

  const cards = [
    { value: fem2024, label: 'Partner feminicides · 2024', confidence: 'high' },
    { value: sx2024?.toLocaleString('en-US'), label: 'Reported sexual crimes · 2024', confidence: 'high' },
    { value: foreignRate != null ? `${(foreignRate / spainRate).toFixed(1)}×` : '—', label: 'Foreign-born vs Spanish-born feminicide rate · 2024', confidence: 'high' },
    { value: hcLatest?.toLocaleString('en-US'), label: `Hate crimes reported · ${hcYear}`, confidence: 'high' },
    { value: DATA.migration.stock_trend.foreign_nationality.at(-1) ? (DATA.migration.stock_trend.foreign_nationality.at(-1) / 1e6).toFixed(1) + 'M' : '—', label: 'Foreign nationals resident · latest', confidence: 'medium' },
  ];
  el.innerHTML = cards.map(c => `<svs-stat-card value="${c.value ?? '—'}" label="${c.label}" confidence="${c.confidence}"></svs-stat-card>`).join('');
}

/* ── tab wiring ──────────────────────────────────────── */
function showTab(id) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.toggle('active', p.id === 'tab-' + id));
  const main = document.getElementById('main-tabs'); if (main) main.active = id;
  mountVisible();
}
function wire() {
  document.getElementById('main-tabs')?.addEventListener('tab-change', e => showTab(e.detail.id));
  document.querySelector('svs-confidence-filter')?.addEventListener('conf-change', e => {
    activeConf = e.detail.active;
    document.querySelectorAll('svs-chart-panel').forEach(p => { if (p._chart) p.refresh(activeConf); });
  });
  window.addEventListener('resize', () => { /* Chart.js handles responsive resize itself */ });
}

/* ── boot ────────────────────────────────────────────── */
async function main() {
  const names = ['mortality', 'migration', 'feminicides', 'sexual_crimes', 'hate_crimes', 'cohort_tenure'];
  const loaded = await Promise.all(names.map(n => fetch(`data/${n}.json`).then(r => {
    if (!r.ok) throw new Error(`${n}.json ${r.status}`); return r.json();
  })));
  names.forEach((n, i) => DATA[n] = loaded[i]);

  buildFeminicides(); buildSexual(); buildHate(); buildMortality(); buildMigration(); buildCohort();
  setHeadlines();
  wire();
  showTab('feminicides');   // mounts the initially-visible panels
}

main().catch(err => {
  console.error(err);
  document.body.insertAdjacentHTML('afterbegin',
    `<div style="padding:16px;background:#7f1d1d;color:#fff;font:600 14px system-ui">Data failed to load: ${err.message}. Run <code>uv run python src/build_dashboard.py</code> and serve docs/ over HTTP.</div>`);
});
