// <svs-chart-panel title="…" subtitle="…" size="full|half|third" [confidence="high"]>
// The workhorse card that hosts one Chart.js chart. Light DOM (so Chart.js
// canvas sizing is reliable and the element participates in the page's 12-col
// grid). Styling lives in assets/components.css.
//
// Usage from app.js:
//   panel.builder = (canvas, activeConf) => new Chart(canvas, {...});
//   panel.mount(activeConf);              // build when the tab first shows
//   panel.refresh(activeConf);            // rebuild on a confidence-filter change
//
// Optional slots: pass a <svs-legend slot="legend"> or
// <svs-source-cite slot="source"> as light-DOM children and they render in the
// header / footer respectively.

import './confidence-badge.js';

class ChartPanel extends HTMLElement {
  static observedAttributes = ['title', 'subtitle', 'size', 'confidence', 'height'];

  connectedCallback() { if (!this._built) this.render(); }
  attributeChangedCallback() { if (this._built) this.render(); }

  get canvas() { return this.querySelector('canvas'); }
  set builder(fn) { this._builder = fn; }

  render() {
    const title = this.getAttribute('title') || '';
    const subtitle = this.getAttribute('subtitle') || '';
    const size = this.getAttribute('size') || 'full';
    const conf = this.getAttribute('confidence');
    const height = this.getAttribute('height'); // optional fixed cp-wrap height, in px

    // Detach any slotted children before we overwrite innerHTML, then re-place.
    const legend = this.querySelector('[slot="legend"]');
    const source = this.querySelector('[slot="source"]');

    this.classList.add('chart-panel');
    this.dataset.size = size;
    this.innerHTML = `
      <div class="cp-head">
        <div class="cp-titles">
          <div class="cp-title">${title}</div>
          ${subtitle ? `<div class="cp-sub">${subtitle}</div>` : ''}
        </div>
        ${conf ? `<svs-confidence-badge level="${conf}"></svs-confidence-badge>` : ''}
      </div>
      <div class="cp-legend"></div>
      <div class="cp-wrap"${height ? ` style="flex:0 0 ${Number(height)}px;min-height:0"` : ''}><canvas></canvas></div>
      <div class="cp-source"></div>`;

    if (legend) this.querySelector('.cp-legend').append(legend);
    if (source) this.querySelector('.cp-source').append(source);
    this._built = true;
  }

  mount(activeConf) {
    if (!this._built) this.render();
    if (this._chart) { this._chart.destroy(); this._chart = null; }
    if (this._builder) this._chart = this._builder(this.canvas, activeConf || {});
  }

  refresh(activeConf) {
    if (this._builder && this._built) this.mount(activeConf);
  }

  disconnectedCallback() {
    if (this._chart) { this._chart.destroy(); this._chart = null; }
  }
}
customElements.define('svs-chart-panel', ChartPanel);
