import ast
from pathlib import Path

from spaday import element, generate
from spaday.bootstrap import bootstrap

from spaday_webawesome import Tabs, WaButton, WaCard, package


def _generated_ast(source: str) -> str:
    class Normalize(ast.NodeTransformer):
        def visit_ImportFrom(self, node):
            if node.module == "typing":
                node.names = [name for name in node.names if name.name != "Optional"]
            return node

        def visit_Subscript(self, node):
            node = self.generic_visit(node)
            if isinstance(node.value, ast.Name) and node.value.id == "Optional":
                return ast.BinOp(left=node.slice, op=ast.BitOr(), right=ast.Constant(value=None))
            return node

        def visit_Assign(self, node):
            node = self.generic_visit(node)
            if any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
                node.value.elts.sort(key=ast.unparse)
            return node

    return ast.dump(Normalize().visit(ast.parse(source)))


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
    tags = {schema.tag for schema in package.catalog}
    assert {"wa-button", "wa-card", "wa-input"} <= tags
    assert len(tags) == len(package.catalog)
    assert 'href="/components/webawesome/css/webawesome.css"' in html
    assert 'src="/components/webawesome/cdn/index.js"' in html


def test_generated_catalog_is_current():
    root = Path(__file__).parent.parent
    fresh = generate(str(root / "custom-elements.json"))
    assert _generated_ast(fresh) == _generated_ast((root / "components.py").read_text(encoding="utf-8"))
