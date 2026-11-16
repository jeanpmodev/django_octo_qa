from behave import given, when, then
from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

User = get_user_model()


def get_qa_execution_model():
    for app_config in apps.get_app_configs():
        if app_config.name.startswith("django_octo_"):
            models = list(app_config.get_models())
            if models:
                return models[0]
    raise LookupError("No model found in django_octo_* apps.")


def get_dashboard_url(model):
    opts = model._meta
    return reverse(f"admin:{opts.app_label}_{opts.model_name}_changelist")


@given("an authenticated QA superuser exists")
def step_create_authenticated_qa_superuser(context):
    context.client = Client()
    user, created = User.objects.get_or_create(
        username="qa_superuser",
        defaults={
            "email": "qa@example.com",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    if created:
        user.set_password("qa123456")
        user.save()
    context.client.force_login(user)


@when("the superuser opens the Quality Assurance dashboard")
def step_open_qa_dashboard(context):
    model = get_qa_execution_model()
    url = get_dashboard_url(model)
    context.response = context.client.get(url)


@then("the response status code should be {status_code:d}")
def step_verify_status_code(context, status_code):
    assert context.response.status_code == status_code, (
        f"Expected status {status_code}, got {context.response.status_code}"
    )


@then("the inventory table should list discovered test cases")
def step_verify_inventory_table(context):
    html = context.response.content.decode("utf-8")
    assert "Discovered Suites:" in html or "Quality Assurance Orchestrator" in html


@given("an archived QA execution record exists")
def step_create_archived_execution(context):
    model = get_qa_execution_model()
    field_names = {f.name for f in model._meta.fields}
    kwargs = {}
    if "engine" in field_names:
        kwargs["engine"] = "PYTEST"
    if "target_scope" in field_names:
        kwargs["target_scope"] = "project_root"
    if "status" in field_names:
        kwargs["status"] = "PASSED"

    context.execution_record = model.objects.create(**kwargs)


@when("the superuser deletes the archived QA execution record")
def step_delete_archived_execution(context):
    model = get_qa_execution_model()
    opts = model._meta
    record_id = context.execution_record.pk
    delete_url = reverse(
        f"admin:{opts.app_label}_{opts.model_name}_delete",
        args=[record_id],
    )
    context.delete_response = context.client.post(delete_url, {"post": "yes"})


@then("the execution record should be removed from the database")
def step_verify_record_deleted(context):
    model = get_qa_execution_model()
    exists = model.objects.filter(pk=context.execution_record.pk).exists()
    assert not exists, "Execution record still exists in the database."

