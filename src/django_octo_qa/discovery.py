import ast
import os
from pathlib import Path
from django.apps import apps
from django.conf import settings

IGNORED_DIRS = {".venv", "venv", ".git", "__pycache__", "node_modules", ".pytest_cache", "migrations"}


def get_scan_roots() -> list[tuple[str, Path]]:
    """Resolve both installed app paths and external repo/project test roots."""
    roots: list[tuple[str, Path]] = []
    seen_paths: set[Path] = set()

    # 1. Project root (BASE_DIR)
    base_dir = getattr(settings, "BASE_DIR", None)
    if base_dir:
        base_path = Path(base_dir).resolve()
        roots.append(("project_root", base_path))
        seen_paths.add(base_path)

    # 2. All active Django apps (including Satellites & User Apps)
    for app_config in apps.get_app_configs():
        if app_config.name.startswith("django.contrib."):
            continue

        app_path = Path(app_config.path).resolve()
        if app_path not in seen_paths:
            roots.append((app_config.label, app_path))
            seen_paths.add(app_path)

        # Check external sibling 'tests/' folder (editable installs / local dev repos)
        if app_path.parent.name == "src":
            repo_root = app_path.parent.parent
            for ext_dir_name in ("tests", "features"):
                ext_path = repo_root / ext_dir_name
                if ext_path.is_dir() and ext_path not in seen_paths:
                    roots.append((app_config.label, ext_path))
                    seen_paths.add(ext_path)

    return roots


def discover_all_tests() -> list[dict]:
    """Scan all resolved roots across the 3 pillars: Pytest, BDD (Behave), and Locust."""
    inventory: list[dict] = []
    scanned_files: set[Path] = set()

    for app_label, root_path in get_scan_roots():
        if not root_path.exists():
            continue

        for dirpath, dirnames, filenames in os.walk(root_path):
            # Prune ignored directories in-place
            dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
            current_dir = Path(dirpath)

            for filename in filenames:
                file_path = (current_dir / filename).resolve()
                if file_path in scanned_files:
                    continue
                scanned_files.add(file_path)

                # PILLAR 1: BDD (Behave .feature files)
                if filename.endswith(".feature"):
                    for line in file_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                        stripped = line.strip()
                        if stripped.startswith(("Scenario:", "Scenario Outline:")):
                            scenario_name = stripped.split(":", 1)[1].strip()
                            inventory.append({
                                "app": app_label,
                                "engine": "behave",
                                "name": scenario_name,
                                "target": str(file_path),
                            })

                # PILLAR 2 & 3: Python files (Pytest & Locust)
                elif filename.endswith(".py"):
                    try:
                        tree = ast.parse(file_path.read_text(encoding="utf-8", errors="ignore"))
                    except SyntaxError:
                        continue

                    # Check Locust files
                    is_locust = filename.startswith("locustfile") or _has_locust_user(tree)
                    if is_locust:
                        inventory.append({
                            "app": app_label,
                            "engine": "locust",
                            "name": filename,
                            "target": str(file_path),
                        })

                    # Check Pytest functions/methods
                    if filename.startswith("test_") or filename.endswith("_test.py"):
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                                inventory.append({
                                    "app": app_label,
                                    "engine": "pytest",
                                    "name": f"{filename}::{node.name}",
                                    "target": f"{file_path}::{node.name}",
                                })

    return inventory


def _has_locust_user(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id in {"HttpUser", "User", "FastHttpUser"}:
                    return True
    return False

def discover_qa_inventory() -> list[dict]:
    return discover_all_tests()
