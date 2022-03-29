"""Views for testing DumpDie"""
from decimal import Decimal
from django.http import HttpResponse
from types import ModuleType


def simple_example(request):
    """Simple Type Example Test View"""
    test_type = request.GET['type']

    if test_type == 'bool':
        test_bool = True
        dd(test_bool)
    elif test_type == 'bound_field':
        test_bound_field = '?'
        dd(test_bound_field)
    elif test_type == 'bytes':
        test_bytes = b'test bytes'
        dd(test_bytes)
    elif test_type == 'decimal':
        test_decimal = Decimal(23.5)
        dd(test_decimal)
    elif test_type == 'float':
        test_float = 23.5
        dd(test_float)
    elif test_type == 'int':
        test_int = 23
        dd(test_int)
    elif test_type == 'module':
        test_module = ModuleType('django.http')
        dd(test_module)
    elif test_type == 'string':
        test_string = 'test string'
        dd(test_string)



    return HttpResponse('wrong response')
