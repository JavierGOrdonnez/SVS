// <svs-confidence-filter active="high,medium,low">
// The pill filter that toggles which confidence tiers are shown. Emits a
// bubbling `conf-change` CustomEvent with { detail: { active } } where active
// is { high, medium, low, unverified } booleans. Charts listen and re-render.

const TIERS = ['high', 'medium', 'low', 'unverified'];

class ConfidenceFilter extends HTMLElement {
  static observedAttributes = ['active'];

  connectedCallback() {
    const attr = (this.getAttribute('active') || 'high,medium,low').split(',').map(s => s.trim());
    this._state = Object.fromEntries(TIERS.map(t => [t, attr.includes(t)]));
    this.render();
  }

  get value() { return { ...this._state }; }

  render() {
    if (!this.shadowRoot) this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .bar {
          display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
          padding: 14px 40px; background: var(--bg2, #1a1d27);
          border-bottom: 1px solid var(--border, #2e3347);
        }
        .lead { font: 600 0.78rem var(--font-body, system-ui); color: var(--text2, #9ba3bf);
                text-transform: uppercase; letter-spacing: 0.05em; }
        button {
          display: flex; align-items: center; gap: 6px; cursor: pointer;
          padding: 5px 12px; border-radius: var(--pill-radius, 20px);
          border: 1.5px solid var(--c); color: var(--c); background: transparent;
          font: 600 0.8rem var(--font-body, system-ui); transition: all 0.15s;
        }
        button[aria-pressed="true"] { background: var(--c); color: #08101c; }
        button[aria-pressed="true"].unverified { color: #fff; }
        .dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; }
        @media (max-width: 900px) { .bar { padding: 12px 16px; } }
      </style>
      <div class="bar">
        <span class="lead">Show confidence</span>
        ${TIERS.map(t => `
          <button class="${t}" data-tier="${t}" style="--c: var(--${t})"
                  aria-pressed="${this._state[t]}">
            <span class="dot"></span>${t[0].toUpperCase() + t.slice(1)}
          </button>`).join('')}
      </div>`;
    this.shadowRoot.querySelectorAll('button').forEach(b =>
      b.addEventListener('click', () => this._toggle(b.dataset.tier)));
  }

  _toggle(tier) {
    this._state[tier] = !this._state[tier];
    const b = this.shadowRoot.querySelector(`button[data-tier="${tier}"]`);
    b.setAttribute('aria-pressed', String(this._state[tier]));
    this.dispatchEvent(new CustomEvent('conf-change', {
      detail: { active: this.value }, bubbles: true, composed: true,
    }));
  }
}
customElements.define('svs-confidence-filter', ConfidenceFilter);
