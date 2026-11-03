import WaInput from "@awesome.me/webawesome/dist/components/input/input.js";
import { css, html, type PropertyValues } from "lit";

type Suggestion = { value: string; label: string };

/** A WebAwesome input with asynchronous suggestions in the input's own ARIA tree. */
export class Autocomplete extends WaInput {
  static properties = {
    suggestionsUrl: { attribute: "suggestions-url" },
    allowCustom: { type: Boolean, attribute: "allow-custom" },
  };
  static css = [
    ...WaInput.css,
    css`
      wa-popup::part(popup) {
        z-index: 1000;
      }
      #suggestions {
        margin: 0;
        padding: 0.25rem;
        list-style: none;
        max-height: 16rem;
        overflow: auto;
        box-sizing: border-box;
        background: var(--wa-color-surface-raised, white);
        color: var(--wa-color-text-normal, black);
        border: 1px solid var(--wa-color-surface-border, #ccc);
        border-radius: var(--wa-border-radius-m, 0.375rem);
        box-shadow: var(--wa-shadow-m);
      }
      [role="option"] {
        padding: 0.5rem 0.75rem;
        cursor: pointer;
        border-radius: 0.25rem;
      }
      [aria-selected="true"] {
        background: var(--wa-color-brand-fill-quiet, #def);
      }
      #status {
        position: absolute;
        width: 1px;
        height: 1px;
        overflow: hidden;
        clip-path: inset(50%);
        white-space: nowrap;
      }
      #status[data-error] {
        position: static;
        width: auto;
        height: auto;
        clip-path: none;
        white-space: normal;
        font-size: var(--wa-font-size-s);
        color: var(--wa-color-text-quiet);
      }
      #status:empty {
        display: none;
      }
    `,
  ];
  static get validators(): typeof WaInput.validators {
    return [
      ...super.validators,
      {
        checkValidity: (element) => {
          const control = element as Autocomplete;
          const isValid =
            !control.hasUpdated ||
            control.allowCustom ||
            !control.value ||
            control.#selected === control.value ||
            control.#options.some((option) => option.value === control.value);
          return {
            isValid,
            message: "Choose a suggestion.",
            invalidKeys: ["customError" as const],
          };
        },
      },
    ];
  }

  declare suggestionsUrl: string;
  declare allowCustom: boolean;
  #options: Suggestion[] = [];
  #selected: string | null = null;
  #active = -1;
  #open = false;
  #loading = false;
  #composing = false;
  #message = "";
  #controller?: AbortController;
  #timer?: ReturnType<typeof setTimeout>;

  constructor() {
    super();
    this.suggestionsUrl = "";
    this.allowCustom = true;
    this.autocomplete = "off";
    this.addEventListener("input", () => {
      if (this.value !== this.#selected) this.#selected = null;
      this.#options = [];
      this.#active = -1;
      this.#cancel();
      this.updateValidity();
      if (
        this.#selected === null &&
        this.value &&
        !this.disabled &&
        !this.readonly
      )
        this.#search();
    });
    this.addEventListener("compositionstart", () => {
      this.#composing = true;
      this.#close();
    });
    this.addEventListener("compositionend", () => {
      this.#composing = false;
      if (!this.disabled && !this.readonly) this.#search();
    });
    // Capture Enter before wa-input's implicit form-submit handler.
    this.addEventListener("keydown", (event) => this.#key(event), true);
    this.addEventListener("focus", () => {
      if (!this.disabled && !this.readonly && this.value) this.#search();
    });
    this.addEventListener("blur", () => this.#close());
  }

  disconnectedCallback() {
    this.#close();
    super.disconnectedCallback();
  }

  updated(changed: PropertyValues<this>) {
    super.updated(changed);
    if (changed.has("suggestionsUrl")) this.#selected = null;
    if (
      changed.has("value") ||
      changed.has("suggestionsUrl") ||
      changed.has("disabled") ||
      changed.has("readonly")
    ) {
      if (this.value !== this.#selected) this.#selected = null;
      this.#options = [];
      this.#active = -1;
      this.#close();
      if (
        this.#selected === null &&
        this.value &&
        !this.disabled &&
        !this.readonly
      )
        this.#search();
    }
    this.input.setAttribute("role", "combobox");
    this.input.setAttribute("aria-autocomplete", "list");
    this.input.setAttribute("aria-controls", "suggestions");
    this.input.setAttribute("aria-expanded", String(this.#open));
    this.input.setAttribute("aria-busy", String(this.#loading));
    if (this.#open && this.#active >= 0)
      this.input.setAttribute(
        "aria-activedescendant",
        `suggestion-${this.#active}`,
      );
    else this.input.removeAttribute("aria-activedescendant");
    if (changed.has("allowCustom") || changed.has("suggestionsUrl"))
      this.updateValidity();
  }

  #cancel() {
    clearTimeout(this.#timer);
    this.#controller?.abort();
    this.#controller = undefined;
    this.#loading = false;
  }

  #close() {
    this.#cancel();
    this.#open = false;
    this.#active = -1;
    this.#message = "";
    this.requestUpdate();
  }

  #search() {
    this.#cancel();
    this.#options = [];
    this.#active = -1;
    this.#open = false;
    if (
      !this.suggestionsUrl ||
      !this.value ||
      !this.isConnected ||
      this.#composing
    )
      return;
    const query = this.value;
    const controller = new AbortController();
    this.#controller = controller;
    this.#loading = true;
    this.#message = "Loading suggestions…";
    this.requestUpdate();
    this.#timer = setTimeout(async () => {
      try {
        const response = await fetch(this.suggestionsUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query }),
          signal: controller.signal,
        });
        if (!response.ok)
          throw new Error(`Suggestions request failed (${response.status})`);
        const options: unknown = await response.json();
        if (
          !Array.isArray(options) ||
          !options.every(
            (option) =>
              option &&
              typeof option.value === "string" &&
              typeof option.label === "string",
          )
        )
          throw new TypeError(
            "Suggestions must be an array of {value, label} objects",
          );
        if (
          controller.signal.aborted ||
          this.value !== query ||
          !this.isConnected
        )
          return;
        this.#options = options;
        this.#open =
          this.shadowRoot?.activeElement === this.input && options.length > 0;
        this.#message = options.length
          ? `${options.length} suggestions available.`
          : "No matching suggestions.";
      } catch (error) {
        if (controller.signal.aborted) return;
        this.#message = "Suggestions unavailable.";
        this.dispatchEvent(
          new CustomEvent("suggestions-error", {
            detail: { message: String(error) },
            bubbles: true,
            composed: true,
          }),
        );
      } finally {
        if (this.#controller === controller) {
          this.#loading = false;
          this.updateValidity();
          this.requestUpdate();
        }
      }
    }, 150);
  }

  async #choose(index: number) {
    const option = this.#options[index];
    if (!option || this.disabled || this.readonly) return;
    this.#selected = option.value;
    this.value = option.value;
    this.#close();
    await this.updateComplete;
    this.dispatchEvent(
      new InputEvent("input", { bubbles: true, composed: true }),
    );
    this.dispatchEvent(new Event("change", { bubbles: true, composed: true }));
    this.input.focus();
  }

  #key(event: KeyboardEvent) {
    if (event.isComposing || this.disabled || this.readonly) return;
    if (event.key === "Escape") {
      if (this.#open || this.#loading) {
        event.preventDefault();
        event.stopPropagation();
        this.#close();
      }
    } else if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      if (!this.#options.length) return;
      event.preventDefault();
      this.#open = true;
      const direction = event.key === "ArrowDown" ? 1 : -1;
      this.#active =
        this.#active < 0
          ? direction > 0
            ? 0
            : this.#options.length - 1
          : (this.#active + direction + this.#options.length) %
            this.#options.length;
      this.requestUpdate();
      void this.updateComplete.then(() =>
        this.shadowRoot
          ?.getElementById(`suggestion-${this.#active}`)
          ?.scrollIntoView({ block: "nearest" }),
      );
    } else if (event.key === "Enter" && this.#open && this.#active >= 0) {
      event.preventDefault();
      event.stopPropagation();
      void this.#choose(this.#active);
    } else if (event.key === "Tab") this.#close();
  }

  render() {
    return html`
      ${super.render()}
      <wa-popup
        .anchor=${this.input?.parentElement}
        .active=${this.#open}
        placement="bottom-start"
        strategy="fixed"
        sync="width"
        flip
        shift
      >
        <ul
          id="suggestions"
          part="suggestions"
          role="listbox"
          aria-label=${this.label || "Suggestions"}
        >
          ${this.#options.map(
            (option, index) => html`
              <li
                id=${`suggestion-${index}`}
                part="option"
                role="option"
                aria-selected=${String(this.#active === index)}
                @mousedown=${(event: MouseEvent) => event.preventDefault()}
                @click=${() => this.#choose(index)}
              >
                ${option.label}
              </li>
            `,
          )}
        </ul>
      </wa-popup>
      <div
        id="status"
        role="status"
        aria-live="polite"
        ?data-error=${this.#message === "Suggestions unavailable."}
      >
        ${this.#message}
      </div>
    `;
  }
}

if (!customElements.get("spaday-wa-autocomplete"))
  customElements.define("spaday-wa-autocomplete", Autocomplete);
