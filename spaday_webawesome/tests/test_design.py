import json

from spaday import Alert, Button, Checkbox, DateInput, Dialog, NumberInput, Progress, RadioGroup, Select, Slider, TextArea, TextInput
from spaday.ui import conformance, resolve
from spaday.ui.controls import CONTROLS
from spaday.ui.design import _plain

from spaday_webawesome import DESIGN, package


def _props(node: dict) -> dict:
    return {k: _plain(v) for k, v in node.get("props", {}).items()}


def test_the_package_publishes_its_design():
    assert package.design is DESIGN
    assert set(DESIGN.controls) == set(CONTROLS)


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
        ("wa-option", {"value": '"a"', "textContent": "a"}),
        ("wa-option", {"value": '"b"', "textContent": "B"}),
    ]
    dialog = resolve(Dialog(label="Confirm").bind("open", "open", mode="two-way").to_node(), DESIGN)
    assert dialog["tag"] == "wa-dialog" and _props(dialog) == {"label": "Confirm"}
    assert dialog["bindings"] == {"open": {"field": "open", "mode": "two-way", "event": "wa-after-hide"}}


def test_wider_generic_controls_render_as_webawesome_elements():
    textarea = resolve(TextArea(label="Notes", rows=3, minlength=2, maxlength=20).bind("value", "notes", mode="two-way").to_node(), DESIGN)
    assert textarea["tag"] == "wa-textarea" and _props(textarea) == {"label": "Notes", "rows": 3, "minlength": 2, "maxlength": 20}

    number = resolve(NumberInput(label="Count", min=0, max=10, step=1).bind("value", "count", mode="two-way").to_node(), DESIGN)
    assert number["tag"] == "wa-input" and _props(number) == {"type": "number", "label": "Count", "min": 0, "max": 10, "step": 1}
    assert number["bindings"]["value"]["codec"] == "number"

    date = resolve(DateInput(label="Date", min="2026-01-01", max="2026-12-31").to_node(), DESIGN)
    assert date["tag"] == "wa-input" and _props(date) == {"type": "date", "label": "Date", "min": "2026-01-01", "max": "2026-12-31"}

    radios = resolve(
        RadioGroup(label="Priority", options=[1, {"value": 2, "label": "High", "disabled": True}], value=1)
        .bind("value", "priority", mode="two-way")
        .to_node(),
        DESIGN,
    )
    assert radios["tag"] == "wa-radio-group" and _props(radios)["value"] == "1"
    assert radios["bindings"]["value"]["codec"] == "json"
    assert [(option["tag"], _props(option)) for option in radios["slots"]["default"]] == [
        ("wa-radio", {"value": "1", "textContent": "1", "checked": True}),
        ("wa-radio", {"value": "2", "disabled": True, "textContent": "High"}),
    ]

    slider = resolve(Slider(label="Volume", min=0, max=10, step=1).bind("value", "volume", mode="two-way").to_node(), DESIGN)
    assert slider["tag"] == "wa-slider" and _props(slider) == {"label": "Volume", "min": 0, "max": 10, "step": 1}
    assert slider["bindings"]["value"]["codec"] == "number"

    alert = resolve(Alert("Body", label="Portable", intent="info").to_node(), DESIGN)
    assert alert["tag"] == "wa-callout" and _props(alert) == {"variant": "brand"}
    assert _props(alert["slots"]["default"][0])["textContent"] == "Portable"

    progress = resolve(Progress(label="Upload", value=25, max=50).to_node(), DESIGN)
    assert progress["tag"] == "wa-progress-bar" and _props(progress) == {"label": "Upload", "value": 25}


def test_the_conformance_page_needs_no_fallback():
    rendered = json.dumps(resolve(conformance.page().to_node(), DESIGN))
    assert "ui-" not in rendered and "data-ui-fallback" not in rendered
