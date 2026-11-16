from django.urls import path
from .views import qa_dashboard_redirect

app_name = "django_octo_qa"

urlpatterns = [
    path("octo/qa/", qa_dashboard_redirect, name="dashboard"),
]
