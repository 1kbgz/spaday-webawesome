from pathlib import Path

from spaday import ComponentPackage

from . import components as _components
from .components import *
from .components import __all__ as _component_names
from .form import FormField, form
from .tabs import Tabs

__version__ = "0.2.0"

package = ComponentPackage(
    name="webawesome",
    assets_dir=Path(__file__).parent / "extension",
    assets=(("css", "css/webawesome.css"), ("js", "cdn/index.js")),
    components=tuple(getattr(_components, name) for name in _component_names),
)

__all__ = [*_component_names, "FormField", "Tabs", "form", "package"]  # noqa: PLE0604
