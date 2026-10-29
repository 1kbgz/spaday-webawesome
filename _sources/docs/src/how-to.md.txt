# How to generate a bound form

This guide shows how to turn a pydantic model into WebAwesome controls bound to spaday store fields.

Define the model and pass its class to `form`:

```python
from pydantic import BaseModel, Field
from spaday_webawesome import form

class Settings(BaseModel):
    name: str = "lamp"
    enabled: bool = True
    brightness: int = Field(default=50, ge=0, le=100)

settings_form = form(Settings)
```

Seed matching browser state and select the package assets when serving:

```python
from spaday.backends.starlette import serve

app = serve(
    settings_form,
    packages=["webawesome"],
    store=Settings().model_dump(),
)
```

The generated controls use two-way bindings. `name`, `enabled`, and `brightness` update their matching
store fields.

## Relabel or replace a control

Use `FormField` as `Annotated` metadata:

```python
from typing import Annotated

from spaday_webawesome import FormField, WaSlider

class Settings(BaseModel):
    brightness: Annotated[
        int,
        FormField(label="Lamp brightness", control=WaSlider()),
    ] = 50
```

Use `exclude={"field_name"}` to omit fields and `overrides={...}` for call-site-specific changes.
Refer to the [API reference](reference.md) for exported helpers.

## Share WebAwesome with your own library

WebAwesome registers global custom element names, so a second copy on the page throws from
`customElements.define`. If your library uses WebAwesome, import it by its bare specifiers and leave
those imports out of your bundle:

```js
// esbuild
await esbuild.build({
  entryPoints: ["src/index.js"],
  bundle: true,
  format: "esm",
  external: ["@awesome.me/webawesome"], // and every path under it
});
```

Serve your bundle as a module next to `packages=["webawesome"]`. The page's import map resolves
`@awesome.me/webawesome/dist/components/button/button.js` and friends to the copy this package
already loaded, so your `import WaButton from "..."` is the registered class and nothing registers twice.

## How to size a Perspective grid inside tabs

Give the grid a definite height. A height on `WaTabGroup` alone does not size its tab-panel
contents; `height: 100%` on the grid can resolve to zero through that chain.

Given an existing Perspective connection and layout in `perspective_config`:

```python
from spaday import element
from spaday.backends.starlette import serve
from spaday_perspective import PerspectivePanel
from spaday_webawesome import WaTab, WaTabGroup, WaTabPanel

tabs = WaTabGroup(
    WaTab(panel="summary").text("Summary"),
    WaTab(panel="trades").text("Trades"),
    WaTabPanel(element("p").text("Select Trades to show the grid."), name="summary"),
    WaTabPanel(
        PerspectivePanel(config=perspective_config).style(
            height="24rem", width="100%", min_width="0",
        ),
        name="trades",
    ),
)
app = serve(tabs, packages=["webawesome", "perspective"])
```

Keep the default Perspective auto-sizing and auto-pause settings. A sized grid redraws when its
tab becomes visible; no `wa-tab-show` handler or synthetic window resize is needed. For a
viewport-relative grid, use a definite height such as `clamp(16rem, 60vh, 40rem)`. For a filling
flex/grid layout, give every intervening container a resolved height and allow flex/grid items
to shrink with `min-width: 0; min-height: 0`.
