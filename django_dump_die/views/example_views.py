"""Various example views for DumpDie library. To showcase how various outputs look in practice."""

# Third-Party Imports.
from django.shortcuts import render


def index(request):
    """Index view, to easily navigate to example views."""
    return render(request, 'django_dump_die/index.html')


def simple_type_example(request):
    """Example view, rendering only "simple type" object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_simple_types

    # Output desired dump values.
    dump('Displaying example of "simple type" object output.')
    dump('')
    dump_simple_types()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def intermediate_type_example(request):
    """Example view, rendering only "intermediate type" object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_intermediate_types

    # Output desired dump values.
    dump('Displaying example of "intermediate type" object output.')
    dump('')
    dump_intermediate_types()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example(request):
    """Example view, rendering only "complex type" object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" object output.')
    dump('')
    dump_complex_types().dump_all_objects()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def function_type_example(request):
    """Example view, rendering only function object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_function_types

    # Output desired dump values.
    dump('Displaying example of function object output.')
    dump('')
    dump_function_types()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def class_type_example(request):
    """Example view, rendering only class object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_class_types

    # Output desired dump values.
    dump('Displaying example of class object output.')
    dump('')
    dump_class_types()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def full_category_example(request):
    """Example view, rendering all examples shown in all other views, all in one page."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import (
        dump_simple_types,
        dump_intermediate_types,
        dump_complex_types,
        dump_function_types,
        dump_class_types,
    )

    # Output desired dump values.
    dump('')
    dump_simple_types()
    dump('')
    dump('')
    dump_intermediate_types()
    dump('')
    dump('')
    dump_complex_types()
    dump('')
    dump('')
    dump_function_types()
    dump('')
    dump('')
    dump_class_types()
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def datetime_example(request):
    """Example view, rendering only "datetime" object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_datetime_types

    # Output desired dump values.
    dump('Displaying example of "datetime" object output.')
    dump('')
    dump_datetime_types()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def django_model_example(request):
    """Example view, rendering only Django model object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_model_types

    # Output desired dump values.
    dump('Displaying example of Django model object output.')
    dump('')
    dump_model_types()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def iterable_group_example(request):
    """Example view, rendering only "iterable group" object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_iterable_group_types

    # Output desired dump values.
    dump('Displaying example of "iterable group" (arrays) object output.')
    dump('')
    dump_iterable_group_types()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def numeric_example(request):
    """Example view, rendering only "numeric" object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_numeric_types

    # Output desired dump values.
    dump('Displaying example of "numeric type" object output.')
    dump('')
    dump_numeric_types()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def system_path_example(request):
    """Example view, rendering only "system path" object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_syspath_types

    # Output desired dump values.
    dump('Displaying example of "syspath" object output.')
    dump('')
    dump_syspath_types()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def full_purpose_example(request):
    """Example view, rendering all examples shown in all other views, all in one page."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import (
        dump_numeric_types,
        dump_datetime_types,
        dump_model_types,
        dump_iterable_group_types,
        dump_syspath_types,
    )

    # Output desired dump values.
    dump('')
    dump_numeric_types()
    dump('')
    dump('')
    dump_datetime_types()
    dump('')
    dump('')
    dump_model_types()
    dump('')
    dump('')
    dump_iterable_group_types()
    dump('')
    dump('')
    dump_syspath_types()
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def django_request_response_cycle_example(request):
    """"""
    from .example_helpers import dump_django_request_response_cycle_types

    # Output desired dump values.
    dump('Displaying Django request-response-cycle example output.')
    dump('')
    dump_django_request_response_cycle_types(request)
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def edge_case_example(request):
    """Example view, rendering various edge-case output.

    These are output types that don't necessarily belong in the other example views, but have
    resulted in errors/bad output, in the past.

    This view allows easily checking them to make sure they are still handled correctly.
    """

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_edgecase_types

    # Output desired dump values.
    dump('')
    dump_edgecase_types()
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})
