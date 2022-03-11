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
    class SpamClass:
        """Spam sample class."""
        def __init__(self):
            self._spam = 'eggs'

    class SomeClass:
        """Sample class."""
        def __init__(self, value):
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
            self.my_string = 'A super cool string'
            self.works = True
            self.nothing = None
            self.bytes = bytes('My Bytes', 'utf-8')
            self.list_o_stuff = ['A', 'B', 'C']
            self.spam = SpamClass()

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
        'something': SomeClass('some instance'),
        'other_thing': SomeOtherClass(),
    }

    dd(x, 'hello')

    return HttpResponse("Example")
