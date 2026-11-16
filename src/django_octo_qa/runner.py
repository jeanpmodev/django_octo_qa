import subprocess
import sys
import tempfile
import time
from pathlib import Path
from django.conf import settings
from .discovery import discover_qa_inventory
from .models import TestExecutionRecord


def is_runner_allowed() -> bool:
    """Checks explicit opt-in flag to prevent unintended execution in production."""
    return bool(getattr(settings, "OCTO_QA_ALLOW_RUNNER", settings.DEBUG))


def _exec_cmd(cmd: list[str], timeout: int = 180) -> tuple[int, str]:
    """Runs a subprocess safely with shell=False and captures combined output."""
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=False,
            timeout=timeout,
        )
        output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        return proc.returncode, output.strip()
    except subprocess.TimeoutExpired:
        return 124, f"Execution timed out after {timeout}s."
    except Exception as exc:
        return 1, f"Subprocess execution error: {exc}"


def run_pytest_target(target: str | None = None, scope_label: str = "all") -> TestExecutionRecord:
    """Executes a specific pytest node ID or all discovered pytest targets."""
    inventory = [i for i in discover_qa_inventory() if i["engine"] == "pytest"]
    start = time.monotonic()

    targets = [target] if target else list({i["target"].split("::")[0] for i in inventory})
    if not targets:
        return TestExecutionRecord.objects.create(
            engine="pytest",
            target_scope="none",
            status="ERROR",
            duration_seconds=0.0,
            console_output="No pytest tests discovered.",
        )

    code, output = _exec_cmd([sys.executable, "-m", "pytest", "-v", *targets])
    duration = time.monotonic() - start
    return TestExecutionRecord.objects.create(
        engine="pytest",
        target_scope=scope_label,
        status="PASSED" if code == 0 else "FAILED",
        duration_seconds=round(duration, 2),
        console_output=output,
    )


def run_behave_target(target: str | None = None, scope_label: str = "all") -> TestExecutionRecord:
    """Executes a specific Behave feature:line scenario or all discovered features."""
    inventory = [i for i in discover_qa_inventory() if i["engine"] == "behave"]
    start = time.monotonic()

    if not inventory and not target:
        return TestExecutionRecord.objects.create(
            engine="behave",
            target_scope="none",
            status="ERROR",
            duration_seconds=0.0,
            console_output="No Behave scenarios discovered.",
        )

    manage_py = Path(getattr(settings, "BASE_DIR", Path.cwd())) / "manage.py"
    if manage_py.is_file():
        cmd = [sys.executable, str(manage_py), "behave", "--no-capture"]
        if target:
            cmd.append(target)
    else:
        targets = [target] if target else list({i["target"].split(":")[0] for i in inventory})
        cmd = [sys.executable, "-m", "behave", *targets]

    code, output = _exec_cmd(cmd)
    duration = time.monotonic() - start
    return TestExecutionRecord.objects.create(
        engine="behave",
        target_scope=scope_label,
        status="PASSED" if code == 0 else "FAILED",
        duration_seconds=round(duration, 2),
        console_output=output,
    )


def run_locust_target(
    target: str | None = None,
    scope_label: str = "all",
    host: str = "http://127.0.0.1:8000",
    users: int = 5,
    spawn_rate: int = 1,
    run_time: str = "5s",
) -> TestExecutionRecord:
    """Executes a specific Locust file or the first discovered Locust suite in headless mode."""
    inventory = [i for i in discover_qa_inventory() if i["engine"] == "locust"]
    start = time.monotonic()

    locustfile = target or (inventory["target"] if inventory else None)
    if not locustfile:
        return TestExecutionRecord.objects.create(
            engine="locust",
            target_scope="none",
            status="ERROR",
            duration_seconds=0.0,
            console_output="No Locust files discovered.",
        )

    safe_users = min(max(1, int(users)), int(getattr(settings, "OCTO_QA_MAX_LOCUST_USERS", 50)))
    safe_spawn = min(max(1, int(spawn_rate)), safe_users)

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        report_file = Path(tmp.name)

    cmd = [
        sys.executable,
        "-m",
        "locust",
        "-f",
        locustfile,
        "--headless",
        "--host",
        host,
        "--users",
        str(safe_users),
        "--spawn-rate",
        str(safe_spawn),
        "--run-time",
        run_time,
        "--html",
        str(report_file),
        "--exit-code-on-error",
        "1",
    ]
    code, output = _exec_cmd(cmd, timeout=120)
    html_content = report_file.read_text(encoding="utf-8") if report_file.is_file() else ""
    report_file.unlink(missing_ok=True)

    duration = time.monotonic() - start
    return TestExecutionRecord.objects.create(
        engine="locust",
        target_scope=f"{scope_label} ({safe_users}u, {run_time})",
        status="PASSED" if code == 0 else "FAILED",
        duration_seconds=round(duration, 2),
        console_output=output,
        html_report=html_content,
    )
