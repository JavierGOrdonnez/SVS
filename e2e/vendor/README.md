Vendored copies of the two CDN scripts `docs/index.html` loads, used by
`e2e/fixtures.js` to serve chart JS locally during tests instead of hitting
cdn.jsdelivr.net. Keep versions in lockstep with `docs/index.html`'s `<script>`
tags:

```
curl -sS -o chart.umd.min.js https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js
curl -sS -o chartjs-plugin-annotation.min.js https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js
```
