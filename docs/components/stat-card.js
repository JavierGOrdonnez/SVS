// <svs-stat-card value="47" label="Feminicides 2024" [delta="-18%"] [delta-dir="down"] [confidence="high"]>
// The headline KPI card. Big figure + caption, optional YoY delta and a
// provenance badge. Uses the mono font so stacked figures align.

import './confidence-badge.js';

class StatCard extends HTMLElement {
  static observedAttributes = ['value', 'label', 'delta', 'delta-dir', 'confidence'];

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  render() {
    const value = this.getAttribute('value') ?? '—';
    const label = this.getAttribute('label') ?? '';
    const delta = this.getAttribute('delta');
    const dir = this.getAttribute('delta-dir') || 'up';
    const conf = this.getAttribute('confidence');
    if (!this.shadowRoot) this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .card {
          background: var(--bg3, #22263a);
          border: 1px solid var(--border, #2e3347);
          border-radius: var(--card-radius, 12px);
          padding: 16px 18px; height: 100%;
          display: flex; flex-direction: column; gap: 4px;
        }
        .val {
          font: 700 2rem/1.05 var(--font-mono, monospace);
          color: var(--accent, #7c83ff); letter-spacing: -0.01em;
        }
        .label {
          font: 400 0.78rem/1.3 var(--font-body, system-ui);
          color: var(--text2, #9ba3bf);
        }
        .foot { display: flex; align-items: center; gap: 10px; margin-top: auto; padding-top: 6px; }
        .delta { font: 600 0.78rem var(--font-body, system-ui); color: var(--high, #22c55e); }
        .delta.down { color: #60a5fa; }
        .delta::before { content: '▲ '; font-size: 0.65em; }
        .delta.down::before { content: '▼ '; }
      </style>
      <div class="card">
        <div class="val">${value}</div>
        <div class="label">${label}</div>
        <div class="foot">
          ${delta ? `<span class="delta ${dir === 'down' ? 'down' : ''}">${delta}</span>` : ''}
          ${conf ? `<svs-confidence-badge level="${conf}"></svs-confidence-badge>` : ''}
        </div>
      </div>`;
  }
}
customElements.define('svs-stat-card', StatCard);
