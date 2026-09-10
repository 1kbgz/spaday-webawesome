"""A downstream component library sharing the page with spaday-webawesome's own catalog.

The integration this exercises end to end:

* the downstream library builds a component out of WebAwesome's elements and imports WebAwesome by
  its bare specifiers, which the page's import map resolves to spaday-webawesome's copy, so the page
  holds one copy of a catalog that registers global custom element names;
* it has no Python of its own, binding through spaday's package surface instead: a
  :class:`~spaday.Component` carrying a schema plus a :class:`~spaday.ComponentPackage` serving its
  bundle, selected with ``packages=[...]`` alongside the first-party one;
* both are authored in one Python tree and wired together with spaday's own bindings and actions --
  a ``WaButton`` from the generated catalog drives a store field that a downstream element's prop is
  bound to, so the two libraries are not merely coexisting but talking to each other.

Served for the browser tests; ``/conformance.js`` hands back the check that asserts the downstream
bundle really implements the components its Python side declares, and ``/conformance-webawesome.js``
the same check for spaday-webawesome's own bundle against its generated catalog.
"""

from pathlib import Path

import uvicorn
from spaday import Component, ComponentPackage, ComponentSchema, PropertySchema, SetField, check_script, element
from spaday.backends.starlette import serve
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from spaday_webawesome import WaButton, WaCallout, WaCard, package as webawesome_package


class DemoMetricCard(Component):
    """The downstream library's element, bound from Python with no Python of its own."""

    tag = "demo-metric-card"
    schema = ComponentSchema(
        tag="demo-metric-card",
        class_name="DemoMetricCard",
        summary="A metric card composed from WebAwesome elements.",
        props=(
            PropertySchema(name="label", kind="string", description="Metric name."),
            PropertySchema(name="value", kind="string", description="Formatted value."),
            PropertySchema(name="tone", kind="enum", choices=("neutral", "brand", "success", "warning", "danger"), description="Badge tone."),
        ),
        events=("demo-metric-details",),
    )


downstream_package = ComponentPackage(
    name="demo-downstream",
    assets_dir=Path(__file__).parent / "downstream",
    assets=(("js", "downstream.js"),),
    components=(DemoMetricCard,),
)

PACKAGES = [webawesome_package, downstream_package]

page = element("div", id="app").child(
    element("h1").text("A downstream library on spaday's WebAwesome"),
    # first-party catalog and downstream element in one tree
    WaCard(id="first-party").child(
        element("h2").text("From the generated catalog"),
        # the tone the downstream card wears is store state, driven from here
        WaButton(id="to-success", variant="brand").text("Mark healthy").on("click", SetField("tone", "success")),
        WaButton(id="to-danger", variant="danger").text("Mark failing").on("click", SetField("tone", "danger")),
    ),
    element("section", id="downstream").child(
        DemoMetricCard(id="metric", label="Fill rate", value="98.6%").bind("tone", "tone"),
    ),
    # a first-party component reading the same field proves both libraries share spaday's state
    WaCallout(id="echo").child(element("span").bind("textContent", "tone")),
)


async def conformance(request) -> PlainTextResponse:
    """The browser-side check for the downstream bundle, built from the schemas its package carries."""
    return PlainTextResponse(check_script([downstream_package]), media_type="text/plain")


async def own_conformance(request) -> PlainTextResponse:
    """The same check for this package's own bundle, which a substitute bundle is measured against."""
    return PlainTextResponse(check_script([webawesome_package]), media_type="text/plain")


app = serve(
    page,
    packages=PACKAGES,
    routes=[Route("/conformance.js", conformance), Route("/conformance-webawesome.js", own_conformance)],
    store={"tone": "neutral"},
    title="spaday-webawesome downstream integration",
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8017)
