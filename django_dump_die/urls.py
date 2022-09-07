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
    function_type_example,
    class_type_example,
    full_category_example,

    numeric_example,
    datetime_example,
    django_model_example,
    iterable_group_example,
    system_path_example,
    full_purpose_example,

    django_request_response_cycle_example,
    edge_case_example,
)


app_name = 'django_dump_die'
urlpatterns = [
    # Various example views.
    path('simple-type-example/', simple_type_example, name='simple-type-example'),
    path('intermediate-type-example/', intermediate_type_example, name='intermediate-type-example'),
    path('complex-type-example/', complex_type_example, name='complex-type-example'),

    path('function-example/', function_type_example, name='function-example'),
    path('class-example/', class_type_example, name='class-example'),

    path('full-category-example/', full_category_example, name='full-category-example'),

    path('datetime-example/', datetime_example, name='datetime-example'),
    path('django-model-example/', django_model_example, name='django-model-example'),
    path('iterable-group-example/', iterable_group_example, name='iterable-group-example'),
    path('numeric-example/', numeric_example, name='numeric-example'),
    path('system-path-example/', system_path_example, name='system-path-example'),

    path('full-purpose-example/', full_purpose_example, name='full-purpose-example'),

    path(
        'django-request-response-cycle-example/',
        django_request_response_cycle_example,
        name='django-request-response-cycle-example',
    ),
    path('edge-case-example/', edge_case_example, name='edge-case-example'),

    path('', index, name='index'),
]
