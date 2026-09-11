import json

from spaday import Button, Checkbox, Dialog, Select, TextInput
from spaday.ui import conformance, resolve
from spaday.ui.design import _plain

from spaday_webawesome import DESIGN, package


def _props(node: dict) -> dict:
    return {k: _plain(v) for k, v in node.get("props", {}).items()}


def test_the_package_publishes_its_design():
    assert package.design is DESIGN
    assert set(DESIGN.controls) == {"button", "input", "checkbox", "switch", "select", "dialog"}


def test_generic_controls_render_as_webawesome_elements():
    button = resolve(Button(label="Save", intent="primary", appearance="outline", size="lg").for_design("webawesome", pill=True).to_node(), DESIGN)
    assert button["tag"] == "wa-button"
    assert _props(button) == {"textContent": "Save", "variant": "brand", "appearance": "outlined", "size": "large", "pill": True}
    text = resolve(TextInput(label="Name", help="Hint", error="Bad").bind("value", "name", mode="two-way").to_node(), DESIGN)
    assert text["tag"] == "wa-input" and _props(text) == {"label": "Name", "hint": "Hint", "data-invalid": True}
    assert _props(text["slots"]["hint"][0])["textContent"] == "Bad"
    assert text["bindings"] == {"value": {"field": "name", "mode": "two-way"}}
    box = resolve(Checkbox(label="Agree").bind("value", "agree", mode="two-way").to_node(), DESIGN)
    assert box["tag"] == "wa-checkbox" and _props(box) == {"textContent": "Agree"}
    assert box["bindings"] == {"checked": {"field": "agree", "mode": "two-way"}}
    select = resolve(Select(label="Plan", options=["a", {"value": "b", "label": "B"}], placeholder="Pick").to_node(), DESIGN)
    assert select["tag"] == "wa-select" and _props(select)["placeholder"] == "Pick"
    assert [(o["tag"], _props(o)) for o in select["slots"]["default"]] == [
        ("wa-option", {"value": "a", "textContent": "a"}),
        ("wa-option", {"value": "b", "textContent": "B"}),
    ]
    dialog = resolve(Dialog(label="Confirm").bind("open", "open", mode="two-way").to_node(), DESIGN)
    assert dialog["tag"] == "wa-dialog" and _props(dialog) == {"label": "Confirm"}
    assert dialog["bindings"] == {"open": {"field": "open", "mode": "two-way", "event": "wa-after-hide"}}


def test_the_conformance_page_needs_no_fallback():
    rendered = json.dumps(resolve(conformance.page().to_node(), DESIGN))
    assert "ui-" not in rendered and "data-ui-fallback" not in rendered
