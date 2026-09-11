<a href="https://github.com/1kbgz/spaday-webawesome">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/1kbgz/spaday-webawesome/raw/main/docs/img/logo-dark.webp?raw=true">
    <img alt="spaday-webawesome logo, round rocks aligned vertically" src="https://github.com/1kbgz/spaday-webawesome/raw/main/docs/img/logo-light.webp?raw=true" width="1200">
  </picture>
</a>

Typed [WebAwesome components](https://webawesome.com/docs/components) and self-contained browser assets for [spaday](https://1kbgz.github.io/spaday/)

[![Build Status](https://github.com/1kbgz/spaday-webawesome/actions/workflows/build.yaml/badge.svg?branch=main&event=push)](https://github.com/1kbgz/spaday-webawesome/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/1kbgz/spaday-webawesome/branch/main/graph/badge.svg)](https://codecov.io/gh/1kbgz/spaday-webawesome)
[![License](https://img.shields.io/github/license/1kbgz/spaday-webawesome)](https://github.com/1kbgz/spaday-webawesome)
[![PyPI](https://img.shields.io/pypi/v/spaday-webawesome.svg)](https://pypi.python.org/pypi/spaday-webawesome)

[![Preview of the spaday-webawesome example](https://raw.githubusercontent.com/1kbgz/spaday-webawesome/main/docs/img/preview.webp)](https://1kbgz.github.io/spaday-webawesome/lite/)

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

## Browser examples

- [Open the standard app](https://1kbgz.github.io/spaday-webawesome/lite/) ([source](spaday_webawesome/example.py)).
- [Open the complete component gallery](https://1kbgz.github.io/spaday-webawesome/lite/?example=gallery) ([source](spaday_webawesome/gallery.py)).

Both run Python locally through Pyodide; no install or server is required.

## Run examples locally

```bash
python -m pip install -e ".[examples]"
python -m spaday_webawesome.example
python -m spaday_webawesome.gallery
```

Open `http://127.0.0.1:8012` for the standard operations-console app or `http://127.0.0.1:8013` for the component gallery. The standard app includes server-updated metrics and an order preview that round-trips to Python. The gallery includes every generated Web Awesome component and a highlighted Python snippet for each component family.

Both pass the local package descriptor directly, so they do not install or resolve the integration from GitHub.

> [!NOTE]
> This library was generated using [copier](https://copier.readthedocs.io/en/stable/) from the [Base Python Project Template repository](https://github.com/python-project-templates/base).
