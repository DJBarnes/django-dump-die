"""
DjangoDumpDie example URL Configuration.
Used exclusively to show example output.
"""

# Third-Party Imports.
from django.urls import path

# Internal Imports.
from .views import (
    index,
    simple_type_example,
    intermediate_type_example,
    complex_type_example,
    iterable_type_example,
    class_type_example,
    django_types_example,
    django_model_example,
    django_request_response_cycle_example,
    function_type_example,
    full_category_example,
    numeric_example,
    datetime_example,
    system_path_example,
    full_specialized_example,
    edge_case_example,
)


app_name = "django_dump_die"
urlpatterns = [
    # Various example views.
    path("simple-type-example/", simple_type_example, name="simple-type-example"),
    path("intermediate-type-example/", intermediate_type_example, name="intermediate-type-example"),
    path("complex-type-example/", complex_type_example, name="complex-type-example"),
    path("django-types-example/", django_types_example, name="django-types-example"),
    path("function-example/", function_type_example, name="function-example"),
    path("full-category-example/", full_category_example, name="full-category-example"),
    # Specialized example views.
    path("numeric-example/", numeric_example, name="numeric-example"),
    path("datetime-example/", datetime_example, name="datetime-example"),
    path("system-path-example/", system_path_example, name="system-path-example"),
    path("iterable-type-example/", iterable_type_example, name="iterable-type-example"),
    path("class-example/", class_type_example, name="class-example"),
    path("django-model-example/", django_model_example, name="django-model-example"),
    path(
        "django-request-response-cycle-example/",
        django_request_response_cycle_example,
        name="django-request-response-cycle-example",
    ),
    path("full-specialized-example/", full_specialized_example, name="full-purpose-example"),
    # Edge Case example views.
    path("edge-case-example/", edge_case_example, name="edge-case-example"),
    # Index page.
    path("", index, name="index"),
]
