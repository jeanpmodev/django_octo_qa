import os
from locust import HttpUser, between, task


class QaDashboardUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        username = os.getenv("OCTO_LOAD_USER", "admin")
        password = os.getenv("OCTO_LOAD_PASS", "admin")

        login_url = "/admin/login/"
        response = self.client.get(login_url)
        csrf_token = response.cookies.get("csrftoken", "")

        self.client.post(
            login_url,
            data={
                "username": username,
                "password": password,
                "csrfmiddlewaretoken": csrf_token,
                "next": "/admin/django_octo_qa/testexecutionrecord/",
            },
            headers={"Referer": f"{self.host}{login_url}"},
        )

    @task(3)
    def view_qa_dashboard(self):
        self.client.get(
            "/admin/django_octo_qa/testexecutionrecord/",
            name="/admin/django_octo_qa/testexecutionrecord/",
        )
