import io
import shutil
import urllib.request
import zipfile
from pathlib import Path
from django.apps import apps
from django.conf import settings

GITHUB_OWNER = "jeanpmodev"
OCTO_MODULES = [
    "django_octo",
    "django_octo_seo",
    "django_octo_security",
    "django_octo_uml",
    "django_octo_qa",
    "django_octo_aurora",
]

OCTO_REPOS = {
    mod: f"https://github.com{GITHUB_OWNER}/{mod}/archive/refs/heads/main.zip"
    for mod in OCTO_MODULES
}

ALLOWED_ROOT_DIRS = ("tests/", "features/", "performance/")


def import_octo_ecosystem_suites() -> dict[str, int]:
    """Download and extract test suites from installed Django-Octo GitHub repos into BASE_DIR/octo_suites."""
    base_dir = Path(getattr(settings, "BASE_DIR", Path.cwd())).resolve()
    target_root = base_dir / "octo_suites"
    target_root.mkdir(parents=True, exist_ok=True)

    installed_labels = {app.name for app in apps.get_app_configs()}
    summary: dict[str, int] = {}

    for module_name, zip_url in OCTO_REPOS.items():
        if module_name not in installed_labels:
            continue

        try:
            with urllib.request.urlopen(zip_url, timeout=15) as response:
                zip_bytes = io.BytesIO(response.read())
        except Exception:
            summary[module_name] = 0
            continue

        extracted_count = 0
        module_dest = target_root / module_name
        module_dest.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_bytes) as zf:
            for member in zf.namelist():
                if member.endswith("/"):
                    continue
                parts = member.split("/", 1)
                if len(parts) < 2:
                    continue
                rel_path = parts[1]

                if not rel_path.startswith(ALLOWED_ROOT_DIRS):
                    continue
                if rel_path.endswith("settings.py"):
                    continue

                dest_file = module_dest / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_bytes(zf.read(member))
                extracted_count += 1

        summary[module_name] = extracted_count

    return summary


def clear_octo_ecosystem_suites() -> bool:
    """Remove imported test suites directory from BASE_DIR."""
    base_dir = Path(getattr(settings, "BASE_DIR", Path.cwd())).resolve()
    target_root = base_dir / "octo_suites"
    if target_root.exists() and target_root.is_dir():
        shutil.rmtree(target_root)
        return True
    return False
