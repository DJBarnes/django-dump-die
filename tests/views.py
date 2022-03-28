"""Views for testing DumpDie"""
from django.http import HttpResponse


def string_example(request):
    """String Example Test View"""
    test_string = 'my test string'

    dd(test_string)

    return HttpResponse('wrong response')
