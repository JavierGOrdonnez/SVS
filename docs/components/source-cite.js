// <svs-source-cite href="…" label="MIR Informe 2024" [note="definition break in 2022"]>
// Inline provenance line beneath a chart. Every figure must trace to a primary
// source (project invariant); this renders that link plus an optional warning.

class SourceCite extends HTMLElement {
  static observedAttributes = ['href', 'label', 'note'];

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  render() {
    const href = this.getAttribute('href');
    const label = this.getAttribute('label') || 'source';
    const note = this.getAttribute('note');
    if (!this.shadowRoot) this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .cite { font: 400 0.74rem/1.4 var(--font-body, system-ui); color: var(--text2, #9ba3bf); }
        .lead { text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.66rem; opacity: 0.7; }
        a {
          color: var(--accent, #7c83ff); text-decoration: none;
          border-bottom: 1px solid var(--accent, #7c83ff); transition: all 0.2s;
        }
        a:hover { color: #fff; border-bottom-color: #fff; background: var(--accent-a, rgba(124,131,255,0.1)); }
        .note { color: var(--low, #f97316); font-weight: 600; }
      </style>
      <div class="cite">
        <span class="lead">Source</span>
        ${href ? `<a href="${href}" target="_blank" rel="noopener">${label}</a>` : `<span>${label}</span>`}
        ${note ? ` · <span class="note">${note}</span>` : ''}
      </div>`;
  }
}
customElements.define('svs-source-cite', SourceCite);
