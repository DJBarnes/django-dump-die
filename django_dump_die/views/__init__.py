"""views init"""

from .dd_view import dd_view
from django_dump_die.views.example_views import (
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
    template_dump_example,
)
