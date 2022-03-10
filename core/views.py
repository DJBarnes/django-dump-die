"""Views for DumpDie"""
from django.http import HttpResponse
from django.shortcuts import render


def dd_view(request, objects):
    """Return dump die view"""
    return render(request, 'dump_die/dd.html', {
        'objects': objects,
    })


def example(request):
    """Example Test"""
    class AnotherClass:
        """Another sample class."""
        def __init__(self):
            self._spam = 'eggs'

    class SomeClass:
        """Sample class."""
        def __init__(self, value):
            self._value = value
            self._spam = AnotherClass()

        def get(self):
            """Get class level value"""
            return self._value

        def add(self, x, y):
            """Add two numbers"""
            return x + y

        def _secret(self):
            """This is a private function"""
            return 'secret'

    x = {
        'one': 1,
        'two': [
            1, 2, 3,
            [4, 5, 6],
        ],
        'three': 'three',
        'something': SomeClass('some instance'),
    }

    dd(x, 'hello')

    return HttpResponse("Example")
