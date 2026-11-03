# API reference

## Generated components

`spaday_webawesome.components` contains typed classes generated from WebAwesome's committed Custom
Elements Manifest. Class names follow the upstream tags: `WaButton` maps to `<wa-button>`, `WaInput`
maps to `<wa-input>`, and so on. Constructor keyword arguments mirror manifest attributes.

All generated names are re-exported from `spaday_webawesome`.

```python
from spaday_webawesome import WaButton

WaButton(variant="brand", size="small").text("Save")
```

## Helpers

```{eval-rst}
.. autoclass:: spaday_webawesome.Tabs
   :members: tab

.. autoclass:: spaday_webawesome.FormField

.. autofunction:: spaday_webawesome.form
```

`Tabs.tab(label, *content, name=None)` adds a linked `<wa-tab>` and `<wa-tab-panel>`. The default name
is a slug of the label.

`form(source, ...)` accepts a pydantic model class, model instance, `TypeAdapter`, or JSON Schema mapping.

## `package`

`spaday_webawesome.package` is a `spaday.ComponentPackage` named `webawesome`. Assets load in this order:

1. `css/webawesome.css`
1. `cdn/index.js`

The CSS maps WebAwesome theme colors onto core `--spa-*` shell tokens. The JavaScript bundle registers
the full component catalog. `package.components` contains every generated component class plus `Autocomplete`;
`package.catalog` returns their property, event, and slot schemas.

`package.imports` publishes WebAwesome's own ES modules under its bare specifiers, which spaday emits
as the page's import map:

| Specifier                      | Served from                                        |
| ------------------------------ | -------------------------------------------------- |
| `@awesome.me/webawesome`       | `vendor/@awesome.me/webawesome/dist/webawesome.js` |
| `@awesome.me/webawesome/dist/` | `vendor/@awesome.me/webawesome/dist/`              |

The bundle imports the catalog through those specifiers too, so any other module on the page that
imports them gets the same copy.

## Radio orientation

`WaRadioGroup(orientation="horizontal")` displays its radios side by side.
`orientation="vertical"` is the upstream default. Both values are present in the
committed manifest, generated constructor, and property schema. The gallery
shows horizontal placement.

```python
from spaday_webawesome import WaRadio, WaRadioGroup

WaRadioGroup(
    WaRadio(value="buy").text("Buy"),
    WaRadio(value="sell").text("Sell"),
    label="Side", orientation="horizontal", value="buy",
)
```

## Autocomplete

`Autocomplete(suggestions_url=..., allow_custom=True, **input_props)` renders
`<spaday-wa-autocomplete>`, a subclass of WebAwesome's input. Use it as a text input;
normal `WaInput` text-input properties, label/hint slots, validation, and form submission apply.
`value` supports two-way binding. Styling uses WebAwesome's existing theme tokens.

| Python argument   | Browser property | Meaning                                      |
| ----------------- | ---------------- | -------------------------------------------- |
| `suggestions_url` | `suggestionsUrl` | POST endpoint accepting `{"query": "text"}`. |
| `allow_custom`    | `allowCustom`    | Accept free text; defaults to `True`.        |

The endpoint must return a JSON array of `{"value": "...", "label": "..."}` objects.
Labels render as text. Return only a bounded set of relevant suggestions. Requests use the browser's
same-origin credentials; authenticate and authorize the endpoint as usual.

The component emits the input's standard events plus `suggestions-error` with a `detail.message`
string for HTTP, network, or response-format failures. Programmatic value changes cancel previous
lookups. Empty input, disabling the field, blur, Escape, and disconnect cancel pending work.
A successful response cannot reopen an unfocused or dismissed list.

The native input has `role="combobox"`, `aria-autocomplete="list"`, `aria-expanded`,
`aria-controls`, and an active-descendant reference during keyboard navigation. The listbox and
options share its shadow root. Focus stays on the input while navigating or selecting options.
The inherited input parts remain available; additional parts are `suggestions` and `option`.
