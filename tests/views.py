"""Views for testing DumpDie"""

# System Imports.
from decimal import Decimal
from types import ModuleType

# Third-Party Imports.
from django.http import HttpResponse


def function_example(request):
    """Function Type Example Test View."""

    def test_function(arg1):
        """Standard Test Function Documentation."""
        return 42

    class TestClass():
        """Test class to attach a function to."""
        def test_function(self):
            """Attached Test Function Documentation."""
            return 42

    test_type = request.GET['type']

    if test_type == 'standard':
        dd(test_function)
    elif test_type == 'attached':
        test_obj = TestClass()
        dd(test_obj.test_function)

    return HttpResponse('wrong response')


def simple_example(request):
    """Simple Type Example Test View."""
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


def data_structure_example(request):
    """Simple Type Example Test View."""
    test_type = request.GET['type']

    if test_type == 'list':
        test_list = ['A', 12, True]
        dd(test_list)
    elif test_type == 'dict':
        test_dict = {
            'char': 'A',
            'num': 12,
            'bool': True,
        }
        dd(test_dict)
    elif test_type == 'tuple':
        test_tuple = ('A', 12, True)
        dd(test_tuple)
    elif test_type == 'set':
        test_set = {'A', 12, True}
        dd(test_set)

    return HttpResponse('wrong response')
