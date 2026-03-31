"""Guards for AI model-registry provider consistency (DeepSeek only)."""
import ast
from pathlib import Path


ROUTER_FILE = Path(__file__).resolve().parents[1] / "routers" / "ai_screening.py"


def _find_model_registry_function(tree: ast.AST) -> ast.AsyncFunctionDef:
    for node in tree.body:
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "get_ai_model_registry":
            return node
    raise AssertionError("get_ai_model_registry endpoint not found")


def test_ai_model_registry_is_hard_pinned_to_deepseek_and_no_nscale_refs():
    source = ROUTER_FILE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    endpoint = _find_model_registry_function(tree)

    # Guard 1: return payload must hardcode provider=deepseek
    return_dicts = [n.value for n in ast.walk(endpoint) if isinstance(n, ast.Return) and isinstance(n.value, ast.Dict)]
    assert return_dicts, "Endpoint must return a dict payload"

    provider_values = []
    for d in return_dicts:
        for key, value in zip(d.keys, d.values):
            if isinstance(key, ast.Constant) and key.value == "provider":
                provider_values.append(value.value if isinstance(value, ast.Constant) else None)
    assert "deepseek" in provider_values, f"Expected provider deepseek, got {provider_values}"

    # Guard 2: endpoint must import/use deepseek provider symbols only
    imported_modules = [
        n.module for n in ast.walk(endpoint)
        if isinstance(n, ast.ImportFrom) and isinstance(n.module, str)
    ]
    assert "services.deepseek_provider" in imported_modules

    endpoint_source = ast.get_source_segment(source, endpoint) or ""
    assert "nscale" not in endpoint_source.lower(), "No NSCALE references allowed in model-registry endpoint"
    assert "nscall" not in endpoint_source.lower(), "No NSCall references allowed in model-registry endpoint"
