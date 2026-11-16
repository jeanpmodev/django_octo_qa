from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect


@staff_member_required
def qa_dashboard_redirect(request):
    """Redirects standalone /octo/qa/ entry point to the unified QA Admin dashboard."""
    return redirect("admin:django_octo_qa_testexecutionrecord_changelist")
