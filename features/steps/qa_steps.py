from behave import given, then, when
from django.contrib.auth.models import User
from django.urls import reverse
from django_octo_qa.models import TestExecutionRecord


@given("an authenticated QA superuser exists")
def step_create_qa_superuser(context):
    user = User.objects.create_superuser(
        username="bdd_qa_admin",
        email="bddqa@octo.dev",
        password="bddpassword123",
    )
    context.test.client.force_login(user)
    context.qa_url = reverse("admin:django_octo_qa_testexecutionrecord_changelist")


@given("an archived QA execution record exists")
def step_create_archived_record(context):
    context.record = TestExecutionRecord.objects.create(
        engine="pytest",
        target_scope="project_root",
        status="PASSED",
        duration_seconds=1.05,
        console_output="All tests passed.",
    )


@when("the superuser opens the Quality Assurance dashboard")
def step_open_qa_dashboard(context):
    context.response = context.test.client.get(context.qa_url)


@when("the superuser deletes the archived QA execution record")
def step_delete_archived_record(context):
    context.response = context.test.client.post(
        context.qa_url,
        data={"delete_record": str(context.record.id)},
        follow=True,
    )


@then("the response status code should be {status_code:d}")
def step_check_status(context, status_code):
    assert context.response.status_code == status_code


@then("the inventory table should list discovered test cases")
def step_check_inventory_listed(context):
    body = context.response.content.decode("utf-8")
    assert "Discovered Test Inventory" in body
    assert "test_discover_qa_inventory_finds_all_engines" in body


@then("the execution record should be removed from the database")
def step_check_record_deleted(context):
    assert not TestExecutionRecord.objects.filter(pk=context.record.id).exists()
