"""DjangoDumpDie complex testing URL Configuration."""

# Third-Party Imports.
from django.urls import path

# Internal Imports.
from tests.django_dump_die.complex_types.views import (
    index,
    # Complex examples
    complex_type__set,
    complex_type__frozen_set,
    complex_type__tuple,
    complex_type__list,
    complex_type__dict,
    complex_type__querydict,
    complex_type__memory_view,
    complex_type__enum,
    # Complex object multi-level examples
    complex_type__multilevel__set,
    complex_type__multilevel__tuple,
    complex_type__multilevel__list,
    complex_type__multilevel__dict,
    # Complex object element examples
    complex_type__multilevel__list__element,
    complex_type__multilevel__tuple__element,
    complex_type__multilevel__dict__element,
    complex_type__multilevel__enum__element,
    # Complex builtin object functions
    complex_type__multilevel__tuple__element__function,
)


app_name = "django_dump_die__tests__complex"
urlpatterns = [
    # Complex examples
    path("complex/set/", complex_type__set, name="complex__set"),
    path("complex/frozen_set/", complex_type__frozen_set, name="complex__frozen_set"),
    path("complex/tuple/", complex_type__tuple, name="complex__tuple"),
    path("complex/list/", complex_type__list, name="complex__list"),
    path("complex/dict/", complex_type__dict, name="complex__dict"),
    path("complex/querydict/", complex_type__querydict, name="complex__querydict"),
    path("complex/memory_view/", complex_type__memory_view, name="complex__memory_view"),
    path("complex/enum/", complex_type__enum, name="complex__enum"),
    # Complex object multi-level examples
    path("complex/multilevel/set/", complex_type__multilevel__set, name="complex__multilevel__set"),
    path("complex/multilevel/tuple/", complex_type__multilevel__tuple, name="complex__multilevel__tuple"),
    path("complex/multilevel/list/", complex_type__multilevel__list, name="complex__multilevel__list"),
    path("complex/multilevel/dict/", complex_type__multilevel__dict, name="complex__multilevel__dict"),
    # Complex object element examples
    path(
        "complex/multilevel/list/element/",
        complex_type__multilevel__list__element,
        name="complex__multilevel__list__element",
    ),
    path(
        "complex/multilevel/tuple/element/",
        complex_type__multilevel__tuple__element,
        name="complex__multilevel__tuple__element",
    ),
    path(
        "complex/multilevel/dict/element/",
        complex_type__multilevel__dict__element,
        name="complex__multilevel__dict__element",
    ),
    path(
        "complex/multilevel/enum/element/",
        complex_type__multilevel__enum__element,
        name="complex__multilevel__enum__element",
    ),
    # Complex builtin object function examples
    path(
        "complex/multilevel/tuple/element/function/",
        complex_type__multilevel__tuple__element__function,
        name="complex__multilevel__tuple__element__function",
    ),
    path("", index, name="index"),
]
