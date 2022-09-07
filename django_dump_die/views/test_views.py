"""Various test views for the DumpDie library.

Needed because having too many mocked "unique" values on a single response will lead to either:
* StopIteration - Due to giving an insufficient mock range.
* RecursionError - Due to too many mock calls, so Python seems to think we're recursing infinitely.

The solution was to divide objects out, displaying only one object per view, which lowers the total amount of
"uniques" being rendered on a given page.
"""

# Third-Party Imports.
from django.shortcuts import render


def complex_type_example__set(request):
    """Example view, rendering only "complex type" Set object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" Set object output.')
    dump('')
    dump_complex_types().dump_set()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__frozen_set(request):
    """Example view, rendering only "complex type" FrozenSet object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" FrozenSet object output.')
    dump('')
    dump_complex_types().dump_frozen_set()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__tuple(request):
    """Example view, rendering only "complex type" Tuple object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" Tuple object output.')
    dump('')
    dump_complex_types().dump_tuple()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__list(request):
    """Example view, rendering only "complex type" List object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" List object output.')
    dump('')
    dump_complex_types().dump_list()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__dict(request):
    """Example view, rendering only "complex type" Dict object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" Dict object output.')
    dump('')
    dump_complex_types().dump_dict()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__querydict(request):
    """Example view, rendering only "complex type" QueryDict object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" QueryDict object output.')
    dump('')
    dump_complex_types().dump_querydict()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__memory_view(request):
    """Example view, rendering only "complex type" MemoryView object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" MemoryView object output.')
    dump('')
    dump_complex_types().dump_memory_view()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__enum(request):
    """Example view, rendering only "complex type" Enum object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" Enum object output.')
    dump('')
    dump_complex_types().dump_enum()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__multilevel_set(request):
    """Example view, rendering only "complex type" Multi-Level Set object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" Multi-Level Set object output.')
    dump('')
    dump_complex_types().dump_multilevel_set()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__multilevel_tuple(request):
    """Example view, rendering only "complex type" Multi-Level Tuple object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" Multi-Level Tuple object output.')
    dump('')
    dump_complex_types().dump_multilevel_tuple()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__multilevel_list(request):
    """Example view, rendering only "complex type" Multi-Level List object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" Multi-Level List object output.')
    dump('')
    dump_complex_types().dump_multilevel_list()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__multilevel_dict(request):
    """Example view, rendering only "complex type" Multi-Level Dict object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" Multi-Level Dict object output.')
    dump('')
    dump_complex_types().dump_multilevel_dict()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__list_subitem(request):
    """Example view, rendering only "complex type" List sub-item object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" List sub-item object output.')
    dump('')
    dump_complex_types().dump_list_subitem()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__tuple_subitem(request):
    """Example view, rendering only "complex type" Tuple sub-item object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" Tuple sub-item object output.')
    dump('')
    dump_complex_types().dump_tuple_subitem()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__tuple_subitem_func(request):
    """Example view, rendering only "complex type" Tuple sub-item function object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" Tuple sub-item function object output.')
    dump('')
    dump_complex_types().dump_tuple_subitem_function()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__dict_subitem(request):
    """Example view, rendering only "complex type" Dict sub-item object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" Dict sub-item object output.')
    dump('')
    dump_complex_types().dump_dict_subitem()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example__enum_subitem(request):
    """Example view, rendering only "complex type" Enum sub-item object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import dump_complex_types

    # Output desired dump values.
    dump('Displaying example of "complex type" Enum sub-item object output.')
    dump('')
    dump_complex_types().dump_enum_subitem()
    dump('')
    dump('')

    # Force dd to prevent further view parsing.
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})
