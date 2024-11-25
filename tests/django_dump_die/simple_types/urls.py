"""DjangoDumpDie simple testing URL Configuration."""

# Third-Party Imports.
from django.urls import path

# Internal Imports.
from tests.django_dump_die.simple_types.views import (
    simple_type_bool,
    simple_type_bytes,
    simple_type_const,
    simple_type_decimal,
    simple_type_float,
    simple_type_int,
    simple_type_module,
    simple_type_none,
    simple_type_string,
)

app_name = "django_dump_die__tests__simple"
urlpatterns = [
    # Simple examples
    path("simple/bool/", simple_type_bool, name="simple__bool"),
    path("simple/bytes/", simple_type_bytes, name="simple__bytes"),
    path("simple/const/", simple_type_const, name="simple__const"),
    path("simple/decimal/", simple_type_decimal, name="simple__decimal"),
    path("simple/float/", simple_type_float, name="simple__float"),
    path("simple/int/", simple_type_int, name="simple__int"),
    path("simple/module/", simple_type_module, name="simple__module"),
    path("simple/none/", simple_type_none, name="simple__none"),
    path("simple/string/", simple_type_string, name="simple__string"),
]
