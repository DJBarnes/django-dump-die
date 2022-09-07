"""
DjangoDumpDie testing URL Configuration.

"""

# Third-Party Imports.
from django.urls import path

# Internal Imports.
from .views.test_views import (
    complex_type_example__set,
    complex_type_example__frozen_set,
    complex_type_example__tuple,
    complex_type_example__list,
    complex_type_example__dict,
    complex_type_example__querydict,
    complex_type_example__memory_view,
    complex_type_example__enum,

    complex_type_example__multilevel_set,
    complex_type_example__multilevel_tuple,
    complex_type_example__multilevel_list,
    complex_type_example__multilevel_dict,

    complex_type_example__list_subitem,
    complex_type_example__tuple_subitem,
    complex_type_example__tuple_subitem_func,
    complex_type_example__dict_subitem,
    complex_type_example__enum_subitem,
)


app_name = 'django_dump_die_tests'
urlpatterns = [
    # Various "complex type" example views.
    path('complex/set/', complex_type_example__set, name='complex__set'),
    path('complex/frozen_set/', complex_type_example__frozen_set, name='complex__frozen_set'),
    path('complex/tuple/', complex_type_example__tuple, name='complex__tuple'),
    path('complex/list/', complex_type_example__list, name='complex__list'),
    path('complex/dict/', complex_type_example__dict, name='complex__dict'),
    path('complex/querydict/', complex_type_example__querydict, name='complex__querydict'),
    path('complex/memory_view/', complex_type_example__memory_view, name='complex__memory_view'),
    path('complex/enum/', complex_type_example__enum, name='complex__enum'),

    path('complex/multi_level/set/', complex_type_example__multilevel_set, name='complex__multi_level__set'),
    path('complex/multi_level/tuple/', complex_type_example__multilevel_tuple, name='complex__multi_level__tuple'),
    path('complex/multi_level/list/', complex_type_example__multilevel_list, name='complex__multi_level__list'),
    path('complex/multi_level/dict/', complex_type_example__multilevel_dict, name='complex__multi_level__dict'),

    path('complex/sub_item/list/', complex_type_example__list_subitem, name='complex__sub_item__list'),
    path('complex/sub_item/tuple/', complex_type_example__tuple_subitem, name='complex__sub_item__tuple'),
    path(
        'complex/sub_item/tuple_func/',
        complex_type_example__tuple_subitem_func,
        name='complex__sub_item__tuple_func',
    ),
    path('complex/sub_item/dict/', complex_type_example__dict_subitem, name='complex__sub_item__dict'),
    path('complex/sub_item/enum/', complex_type_example__enum_subitem, name='complex__sub_item__enum'),
]
