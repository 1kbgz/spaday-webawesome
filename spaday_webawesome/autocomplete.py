"""WebAwesome input with server-backed suggestions."""

from typing import Any, cast

from spaday.catalog import ComponentSchema, PropertySchema
from spaday.component import Child

from .components import WaInput

_input_schema = cast(ComponentSchema, WaInput.schema)


class Autocomplete(WaInput):
    """An editable combobox using WebAwesome's input styling and form behavior.

    POST ``{"query": "text"}`` to ``suggestions_url``; return a JSON array of
    ``{"value": "MSFT", "label": "MSFT · Microsoft"}`` objects. Bind ``value``
    two-way for typed and selected values. ``allow_custom=False`` requires a
    matching suggestion. Normal ``WaInput`` text-input props and slots apply.
    """

    tag = "spaday-wa-autocomplete"
    schema = ComponentSchema(
        tag=tag,
        class_name="Autocomplete",
        summary="Editable combobox with asynchronous suggestions and optional free text.",
        props=(
            *_input_schema.props,
            PropertySchema(name="suggestions-url", kind="string", description="POST endpoint returning {value, label} suggestions."),
            PropertySchema(name="allow-custom", kind="boolean", default="true", description="Allow values outside the suggestion list."),
        ),
        events=(*_input_schema.events, "suggestions-error"),
        slots=_input_schema.slots,
    )

    def __init__(
        self,
        *children: Child,
        suggestions_url: str,
        allow_custom: bool = True,
        **props: Any,
    ) -> None:
        super().__init__(*children, **props)
        self.prop("suggestions-url", suggestions_url)
        self.prop("allow-custom", allow_custom)


__all__ = ["Autocomplete"]
