# spaday-webawesome

Typed WebAwesome components and self-contained browser assets for spaday.

[![Build Status](https://github.com/1kbgz/spaday-webawesome/actions/workflows/build.yaml/badge.svg?branch=main&event=push)](https://github.com/1kbgz/spaday-webawesome/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/1kbgz/spaday-webawesome/branch/main/graph/badge.svg)](https://codecov.io/gh/1kbgz/spaday-webawesome)
[![License](https://img.shields.io/github/license/1kbgz/spaday-webawesome)](https://github.com/1kbgz/spaday-webawesome)
[![PyPI](https://img.shields.io/pypi/v/spaday-webawesome.svg)](https://pypi.python.org/pypi/spaday-webawesome)

## Documentation

- [Build an interactive WebAwesome page](docs/src/tutorial.md) — guided first page.
- [Generate a bound form](docs/src/how-to.md) — task-focused model form guide.
- [API reference](docs/src/reference.md) — catalog, helpers, and assets.
- [Why WebAwesome is a peer package](docs/src/explanation.md) — ownership and loading model.

## Quick example

```python
from spaday import serve
from spaday_webawesome import WaButton, WaCard

page = WaCard(WaButton().text("Run"))
serve(page, packages=["webawesome"])
```

The package also exports `Tabs`, plus `form()` and `FormField` for generating bound WebAwesome controls from pydantic models or JSON Schema.

Installing the package does not inject assets. Select it explicitly with `packages=["webawesome"]` or pass the exported `package` descriptor.

## Run the local example

```bash
python -m pip install -e ".[examples]"
python -m spaday_webawesome.example
```

Open `http://127.0.0.1:8012` to inspect the [complete operations-console example](spaday_webawesome/example.py): cards,
server-updated metrics, tabs, inputs, selects, switches, progress, badges, responsive layout, and an order
preview that round-trips to Python. It passes the local package descriptor directly, so it does not install
or resolve the integration from GitHub.
