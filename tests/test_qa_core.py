import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django_octo_qa.discovery import discover_qa_inventory
from django_octo_qa.models import TestExecutionRecord


@pytest.mark.django_db
def test_discover_qa_inventory_finds_all_engines():
    inventory = discover_qa_inventory()
    engines = {item["engine"] for item in inventory}
    assert "pytest" in engines
    assert "behave" in engines
    assert "locust" in engines


@pytest.mark.django_db
def test_admin_qa_dashboard_renders_inventory_for_superuser(client):
    admin_user = User.objects.create_superuser(
        username="qaadmin",
        email="qa@octo.dev",
        password="strongpassword123",
    )
    client.force_login(admin_user)

    url = reverse("admin:django_octo_qa_testexecutionrecord_changelist")
    response = client.get(url)

    assert response.status_code == 200
    assert b"Discovered Test Inventory" in response.content
    assert b"test_discover_qa_inventory_finds_all_engines" in response.content


@pytest.mark.django_db
def test_admin_qa_deletes_execution_record(client):
    admin_user = User.objects.create_superuser(
        username="qaadmin",
        email="qa@octo.dev",
        password="strongpassword123",
    )
    client.force_login(admin_user)
    record = TestExecutionRecord.objects.create(
        engine="pytest",
        target_scope="project_root",
        status="PASSED",
        duration_seconds=0.42,
        console_output="1 passed",
    )

    url = reverse("admin:django_octo_qa_testexecutionrecord_changelist")
    response = client.post(url, data={"delete_record": str(record.id)}, follow=True)

    assert response.status_code == 200
    assert TestExecutionRecord.objects.count() == 0
