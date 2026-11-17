import io
import shutil
import ssl
import urllib.request
import zipfile
from pathlib import Path
from django.apps import apps
from django.conf import settings

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

GITHUB_OWNER = "jeanpmodev"
OCTO_MODULES = [
    "django_octo",
    "django_octo_seo",
    "django_octo_security",
    "django_octo_uml",
    "django_octo_qa",
    "django_octo_aurora",
]

ALLOWED_ROOT_DIRS = ("tests", "features", "performance")


def _find_local_repo(module_name: str, base_dir: Path) -> Path | None:
    """Check sibling workspace directories for local cloned repositories."""
    alt_name = module_name.replace("_", "-")
    search_bases = [base_dir.parent, base_dir.parent.parent, Path.home() / "PROFISSIONAL"]
    for parent in search_bases:
        if not parent.exists():
            continue
        for candidate_name in (module_name, alt_name):
            candidate = parent / candidate_name
            if candidate.is_dir() and any((candidate / d).is_dir() for d in ALLOWED_ROOT_DIRS):
                return candidate
    return None


def _copy_local_suites(repo_dir: Path, module_dest: Path) -> int:
    extracted = 0
    for folder in ALLOWED_ROOT_DIRS:
        src_folder = repo_dir / folder
        if not src_folder.is_dir():
            continue
        for file_path in src_folder.rglob("*"):
            if file_path.is_dir() or file_path.name == "settings.py" or "__pycache__" in file_path.parts:
                continue
            rel = file_path.relative_to(repo_dir)
            dest_file = module_dest / rel
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_file)
            extracted += 1
    return extracted


def _download_github_suites(module_name: str, module_dest: Path) -> int:
    alt_name = module_name.replace("_", "-")
    for repo_slug in (module_name, alt_name):
        zip_url = f"https://github.com{GITHUB_OWNER}/{repo_slug}/archive/refs/heads/main.zip"
        try:
            req = urllib.request.Request(zip_url, headers={"User-Agent": "Django-Octo-QA"})
            with urllib.request.urlopen(req, timeout=15, context=SSL_CONTEXT) as response:
                zip_bytes = io.BytesIO(response.read())
        except Exception:
            continue

        extracted = 0
        with zipfile.ZipFile(zip_bytes) as zf:
            for member in zf.namelist():
                if member.endswith("/"):
                    continue
                parts = member.split("/", 1)
                if len(parts) < 2:
                    continue
                rel_path = parts[-1]
                if not rel_path.startswith(tuple(f"{d}/" for d in ALLOWED_ROOT_DIRS)):
                    continue
                if rel_path.endswith("settings.py"):
                    continue

                dest_file = module_dest / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_bytes(zf.read(member))
                extracted += 1
        return extracted
    return 0


def import_octo_ecosystem_suites() -> dict[str, int]:
    """Import test suites from local sibling repos or GitHub into BASE_DIR/octo_suites."""
    base_dir = Path(getattr(settings, "BASE_DIR", Path.cwd())).resolve()
    target_root = base_dir / "octo_suites"
    target_root.mkdir(parents=True, exist_ok=True)

    installed_labels = {app.name for app in apps.get_app_configs()}
    summary: dict[str, int] = {}

    for module_name in OCTO_MODULES:
        if module_name not in installed_labels:
            continue

        module_dest = target_root / module_name
        module_dest.mkdir(parents=True, exist_ok=True)

        local_repo = _find_local_repo(module_name, base_dir)
        if local_repo:
            summary[module_name] = _copy_local_suites(local_repo, module_dest)
        else:
            summary[module_name] = _download_github_suites(module_name, module_dest)

    return summary


def clear_octo_ecosystem_suites() -> bool:
    """Remove imported test suites directory from BASE_DIR."""
    base_dir = Path(getattr(settings, "BASE_DIR", Path.cwd())).resolve()
    target_root = base_dir / "octo_suites"
    if target_root.exists() and target_root.is_dir():
        shutil.rmtree(target_root)
        return True
    return False
