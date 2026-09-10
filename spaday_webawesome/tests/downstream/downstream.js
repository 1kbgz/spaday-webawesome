/* A stand-in for a downstream component library built on WebAwesome.
 *
 * It imports WebAwesome the way a library built on it does, by WebAwesome's own bare specifiers,
 * left as imports in its bundle rather than inlined. spaday-webawesome publishes its copy under
 * those specifiers in the page's import map, so they resolve to the modules that already registered
 * the catalog: the page keeps one copy, and there is no second registration of the same tag names
 * to collide with.
 *
 * It has no Python of its own. Its Python binding is a spaday Component carrying a schema plus a
 * ComponentPackage that serves this file, so an application authors it exactly like a first-party
 * component and spaday's props, bindings and actions reach it unchanged.
 */

import "@awesome.me/webawesome/dist/components/badge/badge.js";
import WaButton from "@awesome.me/webawesome/dist/components/button/button.js";
import "@awesome.me/webawesome/dist/components/card/card.js";

const TONES = new Set(["neutral", "brand", "success", "warning", "danger"]);

class DemoMetricCard extends HTMLElement {
  #label = "";
  #value = "";
  #tone = "neutral";
  #built = false;
  #nodes = {};

  get label() {
    return this.#label;
  }
  set label(value) {
    this.#label = value == null ? "" : String(value);
    this.#paint();
  }

  get value() {
    return this.#value;
  }
  set value(value) {
    this.#value = value == null ? "" : String(value);
    this.#paint();
  }

  get tone() {
    return this.#tone;
  }
  set tone(value) {
    this.#tone = TONES.has(value) ? value : "neutral";
    this.#paint();
  }

  connectedCallback() {
    this.style.display ||= "block";
    this.#build();
    this.#paint();
  }

  // built from WebAwesome's own elements: the library is a consumer of the catalog, not a copy of it
  #build() {
    if (this.#built) return;
    this.#built = true;
    const card = document.createElement("wa-card");
    card.setAttribute("with-header", "");

    const header = document.createElement("div");
    header.slot = "header";
    header.className = "demo-metric-header";

    const label = document.createElement("span");
    label.className = "demo-metric-label";
    const badge = document.createElement("wa-badge");
    badge.className = "demo-metric-badge";
    header.append(label, badge);

    const value = document.createElement("strong");
    value.className = "demo-metric-value";

    // constructed from the imported class, which throws unless it is the registered one
    const action = new WaButton();
    action.setAttribute("size", "small");
    action.textContent = "Details";
    action.addEventListener("click", () => {
      this.dispatchEvent(
        new CustomEvent("demo-metric-details", {
          bubbles: true,
          composed: true,
          detail: { label: this.#label, value: this.#value },
        }),
      );
    });

    card.append(header, value, action);
    this.appendChild(card);
    this.#nodes = { label, badge, value };
  }

  #paint() {
    if (!this.#built) return;
    this.#nodes.label.textContent = this.#label;
    this.#nodes.value.textContent = this.#value;
    this.#nodes.badge.textContent = this.#tone;
    this.#nodes.badge.setAttribute("variant", this.#tone);
    this.dataset.tone = this.#tone;
  }
}

if (!customElements.get("demo-metric-card")) {
  customElements.define("demo-metric-card", DemoMetricCard);
}

export { DemoMetricCard };
