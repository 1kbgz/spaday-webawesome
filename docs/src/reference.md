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
the full component catalog. `package.components` contains every generated component class;
`package.catalog` returns their property, event, and slot schemas.

`package.imports` publishes WebAwesome's own ES modules under its bare specifiers, which spaday emits
as the page's import map:

| Specifier                      | Served from                                        |
| ------------------------------ | -------------------------------------------------- |
| `@awesome.me/webawesome`       | `vendor/@awesome.me/webawesome/dist/webawesome.js` |
| `@awesome.me/webawesome/dist/` | `vendor/@awesome.me/webawesome/dist/`              |

The bundle imports the catalog through those specifiers too, so any other module on the page that
imports them gets the same copy.
