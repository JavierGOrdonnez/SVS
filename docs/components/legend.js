// <svs-legend items='[{"label":"High","color":"#22c55e"}]'>
// A compact swatch legend for charts whose series map to confidence tiers or
// categories. Items via JSON attribute or the `items` property.

class Legend extends HTMLElement {
  static observedAttributes = ['items'];

  set items(v) { this._items = v; this.render(); }

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  _parse() {
    if (this._items) return this._items;
    try { return JSON.parse(this.getAttribute('items') || '[]'); }
    catch { return []; }
  }

  render() {
    const items = this._parse();
    if (!this.shadowRoot) this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .row { display: flex; gap: 16px; flex-wrap: wrap; }
        .item { display: flex; align-items: center; gap: 6px;
                font: 400 0.74rem var(--font-body, system-ui); color: var(--text2, #9ba3bf); }
        .swatch { width: 10px; height: 10px; border-radius: 2px; }
      </style>
      <div class="row">${items.map(it => `
        <span class="item"><span class="swatch" style="background:${it.color}"></span>${it.label}</span>`).join('')}
      </div>`;
  }
}
customElements.define('svs-legend', Legend);
