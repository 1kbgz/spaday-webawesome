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

## Offer server-backed suggestions while allowing free text

Use `Autocomplete` to query a Python endpoint as the user types. It renders WebAwesome's input
with an accessible suggestion list. Bind `value` two-way to use selected and typed values in
Spaday actions or a connected transports store.

```python
from spaday_webawesome import Autocomplete
from starlette.responses import JSONResponse
from starlette.routing import Route

async def symbols(request):
    query = str((await request.json()).get("query", "")).strip().upper()
    names = {"AAPL": "Apple", "MSFT": "Microsoft"}
    return JSONResponse([
        {"value": symbol, "label": f"{symbol} · {name}"}
        for symbol, name in names.items()
        if query and symbol.startswith(query)
    ])

symbol = Autocomplete(
    suggestions_url="/api/symbols",
    label="Symbol",
    hint="Choose a ticker or enter your own",
    allow_custom=True,
).bind("value", "symbol", mode="two-way")

# Add Route("/api/symbols", symbols, methods=["POST"]) to serve(..., routes=[...]).
# Initialize store={"symbol": ""}.
```

The component waits 150 ms after typing, cancels outdated requests, and ignores stale responses.
Arrow keys move through suggestions, Enter chooses one, Escape closes the list, and Tab leaves the
field without selecting. Selection emits ordinary `input` and `change` events.

Set `allow_custom=False` to require a matching suggestion. This participates in WebAwesome's form
validation; validate again on the server before accepting an order or other operation. Empty values
remain valid unless `required=True`. Network failures show a status message and emit
`suggestions-error`; free text remains usable when `allow_custom=True`.

The order example and gallery call Python endpoints both locally and through the Pyodide HTTP adapter.
