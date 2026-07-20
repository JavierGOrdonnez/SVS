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
const CONF_A = {
  high: 'rgba(34,197,94,0.7)', medium: 'rgba(234,179,8,0.7)',
  low: 'rgba(249,115,22,0.7)', unverified: 'rgba(239,68,68,0.7)',
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
const line = (label, data, color, extra = {}) => ({
  label, data, borderColor: color, backgroundColor: color + '22',
  borderWidth: 2, tension: 0.25, pointRadius: 2, pointHoverRadius: 4, ...extra,
});

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
function buildFeminicides() {
  const d = DATA.feminicides;

  register('fem-timeline', (cv) => {
    const t = d.timeline;
    const colors = t.confidence.map(c => activeConf[c] ? CONF_A[c] : 'rgba(120,120,140,0.12)');
    const borders = t.confidence.map(c => activeConf[c] ? CONF[c] : 'rgba(120,120,140,0.3)');
    return new Chart(cv, {
      type: 'bar',
      data: { labels: t.years.map(String), datasets: [{ label: 'Victims', data: t.values, backgroundColor: colors, borderColor: borders, borderWidth: 1.5 }] },
      options: baseOpts({ plugins: { annotation: { annotations: {
        covid: vline(String(2020), 'COVID', '#60a5fa') } } } }),
    });
  });

  register('fem-regional', (cv) => {
    const r = d.regional.rows.slice().sort((a, b) => b.count - a.count);
    return new Chart(cv, {
      type: 'bar',
      data: { labels: r.map(x => x.label), datasets: [{ data: r.map(x => x.count), backgroundColor: ACCENT + 'cc', borderColor: ACCENT, borderWidth: 1 }] },
      options: baseOpts({ scales: { x: { beginAtZero: true, grid: { color: GRID }, ticks: { color: TICK } }, y: { grid: { display: false }, ticks: { color: TICK, font: { size: 10 } } } }, y: undefined }),
    });
  });

  register('fem-rates', (cv) => {
    const r = d.rates_2024.rows;
    return new Chart(cv, {
      type: 'bar',
      data: { labels: r.map(x => x.origin), datasets: [{ label: 'per 100k', data: r.map(x => x.rate_per_100k),
        backgroundColor: r.map((_, i) => PALETTE[i] + 'cc'), borderColor: r.map((_, i) => PALETTE[i]), borderWidth: 1 }] },
      options: baseOpts({ plugins: { tooltip: { callbacks: { afterLabel: (c) => {
        const row = r[c.dataIndex]; return `${row.victims} victims / ${(row.population/1e6).toFixed(1)}M · 95% CI ${row.ci_lower}–${row.ci_upper}`; } } } } }),
    });
  });

  register('fem-age-origin', (cv) => {
    const a = d.age_origin.age.filter(x => (x.victims || 0) > 0);
    return new Chart(cv, {
      type: 'bar',
      data: { labels: a.map(x => x.label), datasets: [{ label: 'Victims', data: a.map(x => x.victims), backgroundColor: ACCENT + 'aa', borderColor: ACCENT, borderWidth: 1 }] },
      options: baseOpts({ x: { grid: { display: false }, ticks: { color: TICK, font: { size: 9 }, maxRotation: 45 } } }),
    });
  });
}

function buildSexual() {
  const d = DATA.sexual_crimes;

  register('sx-totals', (cv) => new Chart(cv, {
    type: 'line',
    data: { labels: d.totals.years.map(String), datasets: [line('Reported sexual crimes', d.totals.total, ACCENT, { fill: true })] },
    options: baseOpts({ plugins: { annotation: { annotations: { lo: vline(String(2022), 'LO 10/2022', CONF.low) } } } }),
  }));

  register('sx-categories', (cv) => {
    const s = d.categories.series, keys = Object.keys(s).slice(0, 6);
    return new Chart(cv, {
      type: 'line',
      data: { labels: d.categories.years, datasets: keys.map((k, i) => line(k.replace(/_/g, ' '), s[k], PALETTE[i % PALETTE.length])) },
      options: baseOpts(),
    });
  });

  register('sx-nationality', (cv) => {
    const s = d.nationality.series;
    const pick = ['spanish_perpetrator', 'foreign_perpetrator', 'spanish', 'foreign'].filter(k => s[k]);
    return new Chart(cv, {
      type: 'line',
      data: { labels: d.nationality.years, datasets: pick.map((k, i) => line(k.replace(/_/g, ' '), s[k], PALETTE[i % PALETTE.length])) },
      options: baseOpts(),
    });
  });

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
    data: { labels: s.years, datasets: s.bands.map((b, i) => line(b, s.series[b], PALETTE[i % PALETTE.length], { fill: true, stack: 's', tension: 0.2 })) },
    options: baseOpts({ y: { stacked: true, beginAtZero: true, grid: { color: GRID }, ticks: { color: TICK } } }) }); });
  register('mi-ageprofile', (cv) => { const s = d.age_profile_latest; return new Chart(cv, { type: 'bar',
    data: { labels: s.ages, datasets: [{ data: s.values, backgroundColor: ACCENT + 'cc' }] },
    options: baseOpts({ x: { grid: { display: false }, ticks: { color: TICK, font: { size: 9 } } } }) }); });
  register('mi-stock', (cv) => { const s = d.stock_trend; return new Chart(cv, { type: 'line',
    data: { labels: s.years, datasets: [line('Foreign nationals (stock)', s.foreign_nationality, ACCENT, { fill: true })] },
    options: baseOpts() }); });
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
  const foreignRate = (fem.rates_2024.rows.find(r => r.origin !== 'españa') || {}).rate_per_100k;
  const spainRate = (fem.rates_2024.rows.find(r => r.origin === 'españa') || {}).rate_per_100k;
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
