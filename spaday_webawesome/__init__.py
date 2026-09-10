from pathlib import Path

from spaday import ComponentPackage

from . import components as _components
from .components import *
from .components import __all__ as _component_names
from .form import FormField, form
from .tabs import Tabs

__version__ = "0.2.1"

package = ComponentPackage(
    name="webawesome",
    assets_dir=Path(__file__).parent / "extension",
    assets=(("css", "css/webawesome.css"), ("js", "cdn/index.js")),
    components=tuple(getattr(_components, name) for name in _component_names),
)

#: ``css()`` kwarg → (CSS custom property, what it controls), in the shape of
#: :data:`spaday.theme.SHELL_TOKENS`.
#:
#: WebAwesome is a design system, so this package themes the *other* way round from a rendering
#: package: rather than exposing ``--spa-webawesome-*`` tokens of its own, its stylesheet maps
#: WebAwesome's tokens onto the ``--spa-*`` palette that spaday's shell and every other component
#: package reads. Set these and the whole page follows — shell, graphs, tables, trees::
#:
#:     App().css(wa_color_brand_fill_loud="#0C4253")
#:
#: Every other WebAwesome token works the same way (``css()`` takes arbitrary custom properties);
#: these are the ones wired to the shell palette.
TOKENS = {
    "wa_color_surface_default": ("--wa-color-surface-default", "drives --spa-surface"),
    "wa_color_surface_lowered": ("--wa-color-surface-lowered", "drives --spa-surface-2"),
    "wa_color_surface_border": ("--wa-color-surface-border", "drives --spa-border"),
    "wa_color_text_quiet": ("--wa-color-text-quiet", "drives --spa-muted"),
    "wa_color_brand_fill_loud": ("--wa-color-brand-fill-loud", "drives --spa-accent and --spa-info"),
    "wa_color_success_fill_loud": ("--wa-color-success-fill-loud", "drives --spa-success"),
    "wa_color_warning_fill_loud": ("--wa-color-warning-fill-loud", "drives --spa-warning"),
    "wa_color_danger_fill_loud": ("--wa-color-danger-fill-loud", "drives --spa-danger"),
}

__all__ = [*_component_names, "FormField", "TOKENS", "Tabs", "form", "package"]  # noqa: PLE0604
