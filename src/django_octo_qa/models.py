from django.db import models


class TestExecutionRecord(models.Model):
    __test__ = False
    ENGINE_CHOICES = [
        ("pytest", "Pytest (Unit & Integration)"),
        ("behave", "Behave (BDD Specifications)"),
        ("locust", "Locust (Load & Performance)"),
        ("full", "Full QA Suite"),
    ]

    STATUS_CHOICES = [
        ("PASSED", "Passed"),
        ("FAILED", "Failed"),
        ("ERROR", "Execution Error"),
    ]

    executed_at = models.DateTimeField(auto_now_add=True, verbose_name="Executed At")
    engine = models.CharField(max_length=20, choices=ENGINE_CHOICES, verbose_name="Engine")
    target_scope = models.CharField(max_length=255, default="all", verbose_name="Target Scope")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Status")
    duration_seconds = models.FloatField(default=0.0, verbose_name="Duration (s)")
    console_output = models.TextField(blank=True, default="", verbose_name="Console Output")
    html_report = models.TextField(blank=True, default="", verbose_name="HTML Report")

    class Meta:
        app_label = "django_octo_qa"
        verbose_name = "Test Execution"
        verbose_name_plural = "Quality Assurance"
        ordering = ["-executed_at"]

    def __str__(self):
        return f"QA #{self.id} [{self.engine.upper()}] — {self.status} ({self.duration_seconds:.2f}s)"
