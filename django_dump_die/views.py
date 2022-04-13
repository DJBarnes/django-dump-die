"""Views for DumpDie"""
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from types import ModuleType


def dd_view(request, objects):
    """
    Return dump die view.
    :param request: Request object.
    :param objects: Set of objects to dump.
    """
    # Get user theme choices.
    force_light_theme = getattr(settings, 'DJANGO_DD_FORCE_LIGHT_THEME', False)
    force_dark_theme = getattr(settings, 'DJANGO_DD_FORCE_DARK_THEME', False)
    custom_color_theme = getattr(settings, 'DJANGO_DD_COLOR_SCHEME', None)
    multiline_function_docs = getattr(settings, 'DJANGO_DD_MULTILINE_FUNCTION_DOCS', False)

    # Validate chosen themes.
    if force_light_theme and force_dark_theme:
        raise ValueError("You can't force both light and dark themes.")

    # Render template.
    return render(request, 'django_dump_die/dd.html', {
        'objects': objects,
        'force_light_theme': force_light_theme,
        'force_dark_theme': force_dark_theme,
        'custom_color_theme': custom_color_theme,
        'multiline_function_docs': multiline_function_docs,
    })


def example(request):
    """Example Test"""

    def test_func():
        """Test doc string"""
        return 42

    def test_func_param(param1, *args, **kwargs):
        """Test param doc string"""
        return param1

    class EmptyClass:
        """Empty sample class"""
        pass


    class SpamClass:
        """Spam sample class."""
        def __init__(self):
            self._spam = 'eggs'


    class SomeClass:
        """Sample class."""
        def __init__(self, value):
            self.viewable = 'viewable'
            self._value = value
            self._spam = SpamClass()

        def get(self):
            """Get class level value"""
            return self._value

        def add(self, x, y):
            """Add two numbers"""
            return x + y

        def _secret(self):
            """This is a private function"""
            return 'secret'


    class SomeOtherClass:
        """Some Other Class."""
        SAMPLE_CONST = 41

        def __init__(self, *args, **kwargs):
            self.my_number = 32
            self.my_float = 32.5
            self.my_decimal = Decimal(32.5)
            self.my_string = 'A super cool string'
            self.works = True
            self.nothing = None
            self.bytes = bytes('My Bytes', 'utf-8')
            self.datetime = datetime.now()
            self.list_o_stuff = ['A', 'B', 'C']
            self.sample_set = {'A', 'B', 'C'}
            self.sample_tuple = ('A', 12, True)
            self.some_class = SomeClass('sample')
            self.some_class_dup = self.some_class

        def do_work(self):
            """Do some work"""
            return True

    x = {
        'one': 1,
        'two': [
            1, 2, 3,
            [4, 5, 6],
        ],
        'three': 'three',
        'empty_class': EmptyClass(),
        'some_class': SomeClass('some instance'),
        'other_class': SomeOtherClass(),
    }

    module_type = ModuleType('django.html')


    dump(test_func)
    dump(test_func_param)
    dump(x.copy)
    dump(x, deepcopy=True)
    dump(x, deepcopy=True)
    x['foo'] = 'bar'
    x['new_class'] = SomeOtherClass()
    dump(x)
    dump(module_type)
    dd('hello')

    return HttpResponse("Example")
