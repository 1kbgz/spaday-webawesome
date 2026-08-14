"""WebAwesome tab-group convenience component."""

from typing import Any

from spaday.component import Child, Component

from .components import WaTab, WaTabPanel


def _tab_name(label: str) -> str:
    return "-".join("".join(c if c.isalnum() else " " for c in label.lower()).split()) or "tab"


class Tabs(Component):
    """A ``wa-tab-group`` built from labelled content panels.

    Bind ``active`` two-way to keep application state synchronized with user tab selection.
    """

    tag = "wa-tab-group"

    def __init__(self, *, active: str | None = None, placement: str | None = None, key: str | None = None, **props: Any) -> None:
        super().__init__(key=key, props={"active": active, "placement": placement}, **props)

    def tab(self, label: str, *content: Child, name: str | None = None) -> "Tabs":
        """Add linked ``wa-tab`` and ``wa-tab-panel`` children."""
        name = name or _tab_name(label)
        self.child_in("nav", WaTab(panel=name).text(label))
        self.child(WaTabPanel(name=name).child(*content))
        return self


__all__ = ["Tabs"]
