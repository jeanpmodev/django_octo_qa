import ast
import re
from pathlib import Path
from django.apps import apps
from django.conf import settings


def _get_search_roots() -> list[tuple[str, Path]]:
    roots: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    base_dir = getattr(settings, "BASE_DIR", None) or Path.cwd()
    if base_dir:
        base_path = Path(base_dir).resolve()
        roots.append(("project_root", base_path))
        seen.add(base_path)
    for app_config in apps.get_app_configs():
        app_path = Path(app_config.path).resolve()
        if app_path not in seen:
            roots.append((app_config.label, app_path))
            seen.add(app_path)
    return roots


def _extract_pytest_items(app_label: str, test_file: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    try:
        tree = ast.parse(test_file.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                items.append({"app": app_label, "engine": "pytest", "name": node.name, "target": f"{test_file}::{node.name}"})
    except Exception:
        pass
    return items


def _extract_behave_scenarios(app_label: str, feature_file: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    try:
        lines = feature_file.read_text(encoding="utf-8").splitlines()
        feature_name = feature_file.stem
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("Feature:"):
                feature_name = stripped.split(":", 1)[1].strip()
            elif re.match(r"^Scenario(?: Outline)?:", stripped):
                scen_name = stripped.split(":", 1)[1].strip()
                items.append({"app": app_label, "engine": "behave", "name": f"{feature_name} -> {scen_name}", "target": f"{feature_file}:{idx}"})
    except Exception:
        pass
    return items


def _extract_locust_tasks(app_label: str, py_file: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                bases = {getattr(b, "id", None) or getattr(b, "attr", None) for b in node.bases}
                if bases & {"HttpUser", "FastHttpUser", "User"}:
                    items.append({"app": app_label, "engine": "locust", "name": node.name, "target": str(py_file)})
    except Exception:
        pass
    return items


def discover_qa_inventory() -> list[dict[str, str]]:
    inventory: list[dict[str, str]] = []
    seen_targets: set[str] = set()
    for label, root in _get_search_roots():
        for test_file in sorted((root / "tests").rglob("test_*.py")) if (root / "tests").is_dir() else []:
            for item in _extract_pytest_items(label, test_file):
                if item["target"] not in seen_targets:
                    inventory.append(item)
                    seen_targets.add(item["target"])
        for feature_file in sorted((root / "features").rglob("*.feature")) if (root / "features").is_dir() else []:
            for item in _extract_behave_scenarios(label, feature_file):
                if item["target"] not in seen_targets:
                    inventory.append(item)
                    seen_targets.add(item["target"])
        candidates = [root / "locustfile.py", *root.glob("locust_*.py")]
        for sub in ("performance", "load_tests"):
            if (root / sub).is_dir():
                candidates.extend(sorted((root / sub).glob("*.py")))
        for candidate in candidates:
            if candidate.is_file():
                for item in _extract_locust_tasks(label, candidate):
                    if item["target"] not in seen_targets:
                        inventory.append(item)
                        seen_targets.add(item["target"])
    return inventory
