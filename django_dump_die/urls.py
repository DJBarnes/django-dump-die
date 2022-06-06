"""
django_dump_die URL Configuration.
Used exclusively to show example output.
"""

from django.urls import path

from .views import (
    simple_type_example,
    intermediate_type_example,
    complex_type_example,
    function_type_example,
    class_type_example,
    django_model_type_example,
    full_example,
)


urlpatterns = [
    # Various example views, in order of increasing complexity.
    path('simple-type-example', simple_type_example, name='simple-type-example'),
    path('intermediate-type-example', intermediate_type_example, name='intermediate-type-example'),
    path('complex-type-example', complex_type_example, name='complex-type-example'),
    path('function-example', function_type_example, name='function-example'),
    path('class-example', class_type_example, name='class-example'),
    path('django-model-example', django_model_type_example, name='django-model-example'),
    path('full-example', full_example, name='full-example'),
]
