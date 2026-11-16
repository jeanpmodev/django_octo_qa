from pathlib import Path
from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from .discovery import discover_qa_inventory
from .importer import clear_octo_ecosystem_suites, import_octo_ecosystem_suites
from .models import TestExecutionRecord
from .runner import is_runner_allowed, run_behave_target, run_locust_target, run_pytest_target


@admin.register(TestExecutionRecord)
class TestExecutionRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "executed_at", "engine", "target_scope", "status", "duration_seconds")
    readonly_fields = (
        "executed_at",
        "engine",
        "target_scope",
        "status",
        "duration_seconds",
        "console_output",
    )

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        if request.method == "POST":
            if "delete_record" in request.POST and request.user.is_superuser:
                target_id = request.POST.get("delete_record")
                TestExecutionRecord.objects.filter(pk=target_id).delete()
                self.message_user(request, f"QA record #{target_id} deleted.", level=messages.WARNING)
                return redirect(request.path)

            if not request.user.is_superuser or not is_runner_allowed():
                self.message_user(
                    request,
                    "QA runner is disabled or requires superuser privileges.",
                    level=messages.ERROR,
                )
                return redirect(request.path)

            action = request.POST.get("qa_action")
            target = request.POST.get("target") or None
            scope_label = request.POST.get("scope_label") or "all"

            if action == "import_suites":
                summary = import_octo_ecosystem_suites()
                total_files = sum(summary.values())
                details = ", ".join(f"{mod}: {cnt}" for mod, cnt in summary.items())
                self.message_user(
                    request,
                    f"Imported {total_files} test files ({details}).",
                    level=messages.SUCCESS,
                )
                return redirect(request.path)

            if action == "clear_suites":
                removed = clear_octo_ecosystem_suites()
                msg = "Imported Octo test suites removed." if removed else "No imported suites found."
                self.message_user(request, msg, level=messages.WARNING)
                return redirect(request.path)

            if action == "run_pytest":
                rec = run_pytest_target(target=target, scope_label=scope_label)
                self.message_user(request, f"Pytest ({scope_label}): {rec.status}", level=messages.INFO)
                return redirect(f"{request.path}?record={rec.id}")

            if action == "run_behave":
                rec = run_behave_target(target=target, scope_label=scope_label)
                self.message_user(request, f"Behave ({scope_label}): {rec.status}", level=messages.INFO)
                return redirect(f"{request.path}?record={rec.id}")

            if action == "run_locust":
                host = request.POST.get("locust_host") or request.build_absolute_uri("/").rstrip("/")
                rec = run_locust_target(target=target, scope_label=scope_label, host=host)
                self.message_user(request, f"Locust ({scope_label}): {rec.status}", level=messages.INFO)
                return redirect(f"{request.path}?record={rec.id}")

        record_id = request.GET.get("record")
        active_record = (
            TestExecutionRecord.objects.filter(pk=record_id).first()
            if record_id
            else TestExecutionRecord.objects.first()
        )

        if active_record and request.GET.get("download") == "html" and active_record.html_report:
            response = HttpResponse(active_record.html_report, content_type="text/html; charset=utf-8")
            response["Content-Disposition"] = (
                f'attachment; filename="octo_qa_{active_record.engine}_{active_record.id}.html"'
            )
            return response

        base_dir = Path(getattr(settings, "BASE_DIR", Path.cwd())).resolve()
        has_imported_suites = (base_dir / "octo_suites").is_dir()

        inventory = discover_qa_inventory()
        context = {
            **self.admin_site.each_context(request),
            "title": "Quality Assurance Orchestrator",
            "inventory": inventory,
            "counts": {
                "pytest": len([i for i in inventory if i["engine"] == "pytest"]),
                "behave": len([i for i in inventory if i["engine"] == "behave"]),
                "locust": len([i for i in inventory if i["engine"] == "locust"]),
            },
            "active_record": active_record,
            "history": TestExecutionRecord.objects.only(
                "id", "executed_at", "engine", "target_scope", "status", "duration_seconds"
            )[:50],
            "runner_allowed": request.user.is_superuser and is_runner_allowed(),
            "has_imported_suites": has_imported_suites,
            **(extra_context or {}),
        }
        return TemplateResponse(
            request,
            "admin/django_octo_qa/qa_dashboard.html",
            context,
        )
