/** Tolerate another bundle having already registered elements this bundle also registers.
 *
 * This bundle registers every WebAwesome element at import. An application that also ships
 * WebAwesome — its own curated subset, or another copy at a different version — registers the
 * same tag names, and whichever bundle loads second would throw from `customElements.define`
 * and die entirely, taking the whole catalog with it. Importing this module FIRST makes
 * `define` idempotent (skip names that already exist); `restoreDefine()` puts the real one back
 * immediately after the upstream imports, so the guard never leaks to other scripts.
 *
 * First registration wins, so this keeps the page alive; it does not make two copies agree.
 * One copy on the page is still the goal — see the package README.
 */

const original = customElements.define.bind(customElements);

customElements.define = (
  name: string,
  ctor: CustomElementConstructor,
  options?: ElementDefinitionOptions,
) => {
  if (!customElements.get(name)) original(name, ctor, options);
};

export function restoreDefine(): void {
  customElements.define = original;
}
