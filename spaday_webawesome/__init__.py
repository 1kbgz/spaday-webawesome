from pathlib import Path

from spaday import ComponentPackage

from .components import *
from .components import __all__ as _component_names
from .form import FormField, form
from .tabs import Tabs

__version__ = "0.1.0"

package = ComponentPackage(
    name="webawesome",
    assets_dir=Path(__file__).parent / "extension",
    assets=(("css", "css/webawesome.css"), ("js", "cdn/index.js")),
)

__all__ = [*_component_names, "FormField", "Tabs", "form", "package"]  # noqa: PLE0604
