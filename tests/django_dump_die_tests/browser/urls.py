"""DjangoDumpDie browser testing URL Configuration."""

# Third-Party Imports.
from django.urls import path

# Internal Imports.
from django_dump_die_tests.browser.views import above_page_example, nested_example, template_dump_example

app_name = "django_dump_die__tests__browser"
urlpatterns = [
    path("browser/nested/", nested_example, name="nested"),
    path("browser/template-dump/", template_dump_example, name="template_dump"),
    path("browser/above-page/", above_page_example, name="above_page"),
]
