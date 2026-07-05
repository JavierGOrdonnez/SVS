// <svs-tab-bar level="main|sub" tabs='[{"id":"violence","label":"Violence"}]' [active="violence"]>
// A reusable underline tab bar. Emits a bubbling `tab-change` CustomEvent with
// { detail: { id } } instead of calling globals — so both the main tabs and the
// per-section sub-tabs use the same element. `tabs` via JSON attribute or the
// `tabs` property.

class TabBar extends HTMLElement {
  static observedAttributes = ['tabs', 'active', 'level'];

  set tabs(v) { this._tabs = v; this.render(); }
  get active() { return this._active; }
  set active(id) { this._active = id; this._sync(); }

  connectedCallback() { this.render(); }
  attributeChangedCallback(name) { if (name === 'active') { this._active = this.getAttribute('active'); this._sync(); } else this.render(); }

  _parse() {
    if (this._tabs) return this._tabs;
    try { return JSON.parse(this.getAttribute('tabs') || '[]'); }
    catch { return []; }
  }

  render() {
    const tabs = this._parse();
    this._active = this._active || this.getAttribute('active') || (tabs[0] && tabs[0].id);
    const level = this.getAttribute('level') || 'main';
    if (!this.shadowRoot) this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .bar {
          display: flex; gap: 0; padding: 0 40px; overflow-x: auto;
          background: var(--bg2, #1a1d27); border-bottom: 1px solid var(--border, #2e3347);
        }
        :host([level="sub"]) .bar { padding-left: 40px; background: transparent; }
        button {
          background: transparent; border: none; cursor: pointer; white-space: nowrap;
          color: var(--text2, #9ba3bf); font: 600 0.88rem var(--font-body, system-ui);
          padding: 14px 20px; border-bottom: 2px solid transparent; letter-spacing: 0.02em;
          transition: color 0.15s, border-color 0.15s;
        }
        button:hover { color: var(--text, #e8eaf6); }
        button[aria-selected="true"] { color: var(--accent, #7c83ff); border-bottom-color: var(--accent, #7c83ff); }
        @media (max-width: 900px) { .bar { padding: 0 16px; } button { padding: 12px 14px; font-size: 0.82rem; } }
      </style>
      <div class="bar" role="tablist">
        ${tabs.map(t => `<button role="tab" data-id="${t.id}"
            aria-selected="${t.id === this._active}">${t.label}</button>`).join('')}
      </div>`;
    this.shadowRoot.querySelectorAll('button').forEach(b =>
      b.addEventListener('click', () => this._select(b.dataset.id)));
  }

  _select(id) {
    if (id === this._active) return;
    this._active = id;
    this._sync();
    this.dispatchEvent(new CustomEvent('tab-change', { detail: { id }, bubbles: true, composed: true }));
  }

  _sync() {
    this.shadowRoot?.querySelectorAll('button').forEach(b =>
      b.setAttribute('aria-selected', String(b.dataset.id === this._active)));
  }
}
customElements.define('svs-tab-bar', TabBar);
