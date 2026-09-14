"""How WebAwesome renders spaday's generic controls (:mod:`spaday.ui`).

A page that selects this package renders the complete generic control set as the ``wa-*`` elements
below. ``Control.for_design("webawesome", …)`` sets a WebAwesome prop the generic vocabulary leaves
out (``pill=True``, ``with_clear=True``).
"""

from spaday.ui import ControlSpec, Design, Open, Options, Part, Value

_SIZES = {"sm": "small", "md": "medium", "lg": "large"}
#: WebAwesome has no informational variant of its own; brand carries it, as the palette mapping does.
_VARIANTS = {"neutral": "neutral", "primary": "brand", "info": "brand", "success": "success", "warning": "warning", "danger": "danger"}
_HELP = Part(kind="attr", name="hint")
#: an error is a second hint, in the danger color, and the control marked invalid
_ERROR = Part(kind="slot", name="hint", tag="span", props={"style": "color: var(--wa-color-danger-fill-loud)"})
_FIELD = {"disabled": "disabled", "required": "required", "name": "name", "size": "size"}
_TEXT = {**_FIELD, "readonly": "readonly", "placeholder": "placeholder"}

DESIGN = Design(
    name="webawesome",
    controls={
        "button": ControlSpec(
            tag="wa-button",
            label=Part(kind="text"),
            props={"intent": "variant", "appearance": "appearance", "size": "size", "disabled": "disabled", "name": "name"},
            values={"intent": _VARIANTS, "appearance": {"filled": "filled", "outline": "outlined", "plain": "plain"}, "size": _SIZES},
        ),
        "input": ControlSpec(
            tag="wa-input",
            help=_HELP,
            error=_ERROR,
            invalid={"data-invalid": True},
            props={**_TEXT, "type": "type"},
            values={"size": _SIZES},
        ),
        "textarea": ControlSpec(
            tag="wa-textarea",
            help=_HELP,
            error=_ERROR,
            invalid={"data-invalid": True},
            props={**_TEXT, "rows": "rows", "minlength": "minlength", "maxlength": "maxlength"},
            values={"size": _SIZES},
        ),
        "number-input": ControlSpec(
            tag="wa-input",
            fixed={"type": "number"},
            help=_HELP,
            error=_ERROR,
            invalid={"data-invalid": True},
            props={**_TEXT, "min": "min", "max": "max", "step": "step"},
            values={"size": _SIZES},
            value=Value(codec="number"),
        ),
        "date-input": ControlSpec(
            tag="wa-input",
            fixed={"type": "date"},
            help=_HELP,
            error=_ERROR,
            invalid={"data-invalid": True},
            props={**_FIELD, "readonly": "readonly", "min": "min", "max": "max"},
            values={"size": _SIZES},
        ),
        "checkbox": ControlSpec(
            tag="wa-checkbox",
            label=Part(kind="text"),
            help=_HELP,
            error=_ERROR,
            invalid={"data-invalid": True},
            props=_FIELD,
            values={"size": _SIZES},
            value=Value(prop="checked"),
        ),
        "switch": ControlSpec(
            tag="wa-switch",
            label=Part(kind="text"),
            help=_HELP,
            error=_ERROR,
            invalid={"data-invalid": True},
            props=_FIELD,
            values={"size": _SIZES},
            value=Value(prop="checked"),
        ),
        "select": ControlSpec(
            tag="wa-select",
            help=_HELP,
            error=_ERROR,
            invalid={"data-invalid": True},
            props={**_FIELD, "placeholder": "placeholder"},
            values={"size": _SIZES},
            options=Options(kind="children", tag="wa-option", value="value", label="text"),
            value=Value(codec="json"),
        ),
        "radio-group": ControlSpec(
            tag="wa-radio-group",
            help=_HELP,
            error=_ERROR,
            invalid={"data-invalid": True},
            props=_FIELD,
            values={"size": _SIZES},
            options=Options(kind="children", tag="wa-radio", value="value", label="text", disabled="disabled", selected="checked"),
            value=Value(codec="json"),
        ),
        "slider": ControlSpec(
            tag="wa-slider",
            help=_HELP,
            error=_ERROR,
            invalid={"data-invalid": True},
            props={
                "disabled": "disabled",
                "required": None,
                "readonly": "readonly",
                "name": "name",
                "size": "size",
                "min": "min",
                "max": "max",
                "step": "step",
            },
            values={"size": _SIZES},
            value=Value(codec="number"),
        ),
        "alert": ControlSpec(
            tag="wa-callout",
            label=Part(kind="child", tag="strong"),
            props={"intent": "variant"},
            values={"intent": _VARIANTS},
        ),
        "progress": ControlSpec(
            tag="wa-progress-bar",
            # Web Awesome exposes a percentage rather than a value/max pair.
            props={"max": None},
        ),
        "dialog": ControlSpec(
            tag="wa-dialog",
            # opens by its `open` property; a close it does itself (Escape, light dismiss) ends in wa-after-hide
            open=Open(prop="open", event="wa-after-hide"),
        ),
    },
)
"""WebAwesome's design."""

__all__ = ["DESIGN"]
