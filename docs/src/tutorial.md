# Build an interactive WebAwesome page

In this tutorial, we will serve a WebAwesome card whose button shows and hides a callout entirely in
the browser.

## Install the packages

```bash
pip install "spaday[examples]" spaday-webawesome
```

## Create the page

Save this as `webawesome_app.py`:

```python
import uvicorn

from spaday import Toggle, by_id
from spaday.backends.starlette import serve
from spaday_webawesome import WaButton, WaCallout, WaCard

page = WaCard(
    WaButton(variant="brand")
    .text("Toggle details")
    .on("click", Toggle(by_id("details"), "hidden")),
    WaCallout(id="details", variant="success").text("WebAwesome is mounted."),
)

app = serve(page, packages=["webawesome"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

Run it:

```bash
python webawesome_app.py
```

Open `http://127.0.0.1:8000`. You should see a styled card, button, and callout. Click the button; the
callout disappears. Click it again; it returns without a Python round-trip.

You now have typed WebAwesome components using spaday's serializable action model. Continue with
[Generate a bound form](how-to.md) when your controls come from a schema.
