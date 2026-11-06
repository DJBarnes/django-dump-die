"""DjangoDumpDie function type testing URL Configuration."""

# Third-Party Imports.
from django.urls import path

# Internal Imports.
from django_dump_die_tests.function_types import views

app_name = "django_dump_die__tests__function"
urlpatterns = [
    path("function/basic/", views.function_type_basic, name="function__basic"),
    path("function/with-params/", views.function_type_with_params, name="function__with_params"),
    path("function/no-docstring/", views.function_type_no_docstring, name="function__no_docstring"),
    path("function/lambda/", views.function_type_lambda, name="function__lambda"),
    path("function/bound-method/", views.function_type_bound_method, name="function__bound_method"),
    path("function/builtin/", views.function_type_builtin, name="function__builtin"),
    path("function/call/", views.function_type_call, name="function__call"),
    path("function/call-with-one-arg/", views.function_type_call_with_one_arg, name="function__call_with_one_arg"),
    path("function/call-with-kwarg/", views.function_type_call_with_kwarg, name="function__call_with_kwarg"),
    path("function/call-with-args/", views.function_type_call_with_args, name="function__call_with_args"),
]
