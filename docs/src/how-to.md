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
