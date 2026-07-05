// <svs-confidence-badge level="high|medium|low|unverified" [label="…"]>
// A pill that encodes a data row's provenance tier. The 4-tier scale is the
// project's core trust signal; this badge is reused pervasively next to any
// figure. Self-contained (shadow DOM); themed via tokens.css custom properties.

const LABELS = {
  high: 'High',
  medium: 'Medium',
  low: 'Low',
  unverified: 'Unverified',
};

class ConfidenceBadge extends HTMLElement {
  static observedAttributes = ['level', 'label'];

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  render() {
    const level = (this.getAttribute('level') || 'medium').toLowerCase();
    const label = this.getAttribute('label') || LABELS[level] || level;
    if (!this.shadowRoot) this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: inline-flex; }
        .badge {
          display: inline-flex; align-items: center; gap: 6px;
          padding: 3px 10px; border-radius: var(--pill-radius, 20px);
          border: 1.5px solid var(--c); color: var(--c);
          font: 600 0.72rem/1 var(--font-body, system-ui);
          letter-spacing: 0.02em; text-transform: uppercase;
          background: color-mix(in srgb, var(--c) 12%, transparent);
        }
        .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--c); }
      </style>
      <span class="badge" style="--c: var(--${level}, #9ba3bf)">
        <span class="dot"></span>${label}
      </span>`;
  }
}
customElements.define('svs-confidence-badge', ConfidenceBadge);
