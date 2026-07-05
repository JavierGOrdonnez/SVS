// <svs-caveat-list heading="Critical Data Caveats" items='[{"label":"…","text":"…"}]'>
// The accent-bordered callout that documents each tab's data-quality warnings.
// Items may be passed as a JSON attribute or via the `items` property (array of
// {label, text, href?}).

class CaveatList extends HTMLElement {
  static observedAttributes = ['heading', 'items'];

  set items(v) { this._items = v; this.render(); }
  get items() { return this._items || this._parseAttr(); }

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  _parseAttr() {
    try { return JSON.parse(this.getAttribute('items') || '[]'); }
    catch { return []; }
  }

  render() {
    const heading = this.getAttribute('heading') || 'Critical Data Caveats';
    const items = this._items || this._parseAttr();
    if (!this.shadowRoot) this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .box {
          background: var(--bg2, #1a1d27);
          border: 1px solid var(--border, #2e3347);
          border-left: 4px solid var(--accent, #7c83ff);
          border-radius: var(--card-radius, 12px);
          padding: 18px 22px;
        }
        h3 {
          margin: 0 0 10px; font: 700 0.85rem var(--font-body, system-ui);
          color: var(--accent, #7c83ff); text-transform: uppercase; letter-spacing: 0.06em;
        }
        ul { margin: 0; padding: 0; list-style: none;
             display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 8px 24px; }
        li { position: relative; padding-left: 18px;
             font: 400 0.8rem/1.45 var(--font-body, system-ui); color: var(--text2, #9ba3bf); }
        li::before { content: '⚠'; position: absolute; left: 0; top: 1px; color: var(--low, #f97316); font-size: 0.72rem; }
        strong { color: var(--text, #e8eaf6); font-weight: 600; }
        a { color: var(--accent, #7c83ff); text-decoration: none; border-bottom: 1px solid var(--accent, #7c83ff); }
        a:hover { color: #fff; border-bottom-color: #fff; }
      </style>
      <div class="box">
        <h3>${heading}</h3>
        <ul>${items.map(it => `
          <li>${it.label ? `<strong>${it.label}:</strong> ` : ''}${it.text || ''}${
            it.href ? ` <a href="${it.href}" target="_blank" rel="noopener">source</a>` : ''}</li>`).join('')}
        </ul>
      </div>`;
  }
}
customElements.define('svs-caveat-list', CaveatList);
