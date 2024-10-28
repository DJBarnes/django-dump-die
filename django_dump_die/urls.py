"""
DjangoDumpDie example URL Configuration.
Used exclusively to show example output.
"""

# Third-Party Imports.
from django.urls import path

# Internal Imports.
from .views import (
    index,
    simple_types_example,
    intermediate_types_example,
    complex_types_example,
    iterable_types_example,
    class_types_example,
    django_types_example,
    django_model_types_example,
    django_request_response_cycle_types_example,
    function_types_example,
    full_category_example,
    numeric_example,
    datetime_example,
    system_path_example,
    full_specialized_example,
    edge_case_example,
    obj_inspection_exception_case_example,
    unhandled_exception_case_example,
    template_dump_example,
)


app_name = "django_dump_die"
urlpatterns = [
    # Various example views.
    path("simple-type-example/", simple_types_example, name="simple-type-example"),
    path("intermediate-type-example/", intermediate_types_example, name="intermediate-type-example"),
    path("complex-type-example/", complex_types_example, name="complex-type-example"),
    path("django-types-example/", django_types_example, name="django-types-example"),
    path("function-example/", function_types_example, name="function-example"),
    path("full-category-example/", full_category_example, name="full-category-example"),
    # Specialized example views.
    path("numeric-example/", numeric_example, name="numeric-example"),
    path("datetime-example/", datetime_example, name="datetime-example"),
    path("system-path-example/", system_path_example, name="system-path-example"),
    path("iterable-type-example/", iterable_types_example, name="iterable-type-example"),
    path("class-example/", class_types_example, name="class-example"),
    path("django-model-example/", django_model_types_example, name="django-model-example"),
    path(
        "django-request-response-cycle-example/",
        django_request_response_cycle_types_example,
        name="django-request-response-cycle-example",
    ),
    path("full-specialized-example/", full_specialized_example, name="full-purpose-example"),
    # Edge Case example views.
    path("edge-case-example/", edge_case_example, name="edge-case-example"),
    path(
        "obj-inspection-exception-case-example/",
        obj_inspection_exception_case_example,
        name="obj-inspection-exception-case-example",
    ),
    path(
        "unhandled-exception-case-example/",
        unhandled_exception_case_example,
        name="unhandled-exception-case-example",
    ),
    # Template dump views.
    path("template-dump-example/", template_dump_example, name="template-dump-example"),
    # Index page.
    path("", index, name="index"),
]
