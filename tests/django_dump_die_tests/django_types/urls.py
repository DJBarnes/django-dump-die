"""DjangoDumpDie Django type testing URL Configuration."""

# Third-Party Imports.
from django.urls import path

# Internal Imports.
from django_dump_die_tests.django_types import views

app_name = "django_dump_die__tests__django"
urlpatterns = [
    path("django/model-instance/", views.django_type_model_instance, name="django__model_instance"),
    path("django/model-class/", views.django_type_model_class, name="django__model_class"),
    path("django/form/", views.django_type_form, name="django__form"),
    path("django/bound-field/", views.django_type_bound_field, name="django__bound_field"),
    path("django/safe-string/", views.django_type_safe_string, name="django__safe_string"),
    path("django/lazy-string/", views.django_type_lazy_string, name="django__lazy_string"),
    path("django/request/", views.django_type_request, name="django__request"),
    path("django/http-response/", views.django_type_http_response, name="django__http_response"),
    path("django/template-response/", views.django_type_template_response, name="django__template_response"),
]
