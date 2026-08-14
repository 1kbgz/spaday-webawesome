import ast
from pathlib import Path

from spaday import element, generate
from spaday.bootstrap import bootstrap

from spaday_webawesome import Tabs, WaButton, WaCard, package


def test_generated_components_serialize():
    node = WaCard(WaButton(variant="brand").text("Run")).to_node()
    assert node["tag"] == "wa-card"
    assert node["slots"]["default"][0]["tag"] == "wa-button"


def test_tabs_build_linked_headers_and_panels():
    node = Tabs().tab("Overview", element("p")).to_node()
    assert node["slots"]["nav"][0]["props"]["panel"] == {"Str": "overview"}
    assert node["slots"]["default"][0]["props"]["name"] == {"Str": "overview"}


def test_package_drives_bootstrap_asset_urls():
    html = bootstrap(packages=[package])
    assert 'href="/components/webawesome/css/webawesome.css"' in html
    assert 'src="/components/webawesome/cdn/index.js"' in html


def test_generated_catalog_is_current():
    root = Path(__file__).parent.parent
    fresh = generate(str(root / "custom-elements.json"))
    assert ast.dump(ast.parse(fresh)) == ast.dump(ast.parse((root / "components.py").read_text(encoding="utf-8")))
