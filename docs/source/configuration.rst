Configuration
*************

There are various configuration options that can be set via
`Django Settings <https://docs.djangoproject.com/en/dev/topics/settings/>`_ to
control the overall look, feel, and functionality of the tool.


DJANGO_DD_MAX_RECURSION_DEPTH
=============================

As the tool inspects an object it recurses into other objects that are part of
the original object. This recursion could become quite deep depending on the
size of the object being dumped. This setting will limit the depth of recursion
as to prevent long processing times.

.. note::
    Setting the value to ```None``` will mean no limit.

:Type: ``int``
:Default: ``20``

Example::

    DJANGO_DD_MAX_RECURSION_DEPTH = 30



DJANGO_DD_MAX_ITERABLE_LENGTH
=============================

As the tool inspects an iterable object it will recurse into each object in the
iterable. This may mean a lot of recursion for a very long iterable. This
setting will limit the length or processed elements in an iterable to prevent
long processing times.

.. note::
    Setting the value to ```None``` will mean no limit.

:Type: ``int``
:Default: ``20``

Example::

    DJANGO_DD_MAX_ITERABLE_LENGTH = 30


DJANGO_DD_ADDITIONAL_SIMPLE_TYPES
=================================

A "simple type" is a variable type which is common in most languages,
and generally the user only want to see the literal assigned value.

When the tool encounters a defined simple type it will no longer recurse
further and instead simply output a string representation of that simple type.

Predefined simple types include:

* bool
* BoundField
* bytes
* Decimal
* float
* int
* module
* str

If you would like to add additional simple types that are specific to your
project, you can do that here. Be sure to list each type in the list as a
string of the type to treat as a simple type.

:Type: ``list``
:Default: ``[]``

Example::

    DJANGO_DD_ADDITIONAL_SIMPLE_TYPES = [
        'Cell' #  From openpyxl package
    ]


DJANGO_DD_ADDITIONAL_INTERMEDIATE_TYPES
=======================================

An "intermediate type" is a variable which may have useful properties
for expanded output, but generally most users will only want to see the
literal assigned value.

Furthermore, some of these "intermediate type" objects have child members which
recurse an unhelpful number of times, if each attribute is examined fully.

When the tool encounters a defined intermediate type it will no longer recurse
further, instead outputing a string representation as well as allowing
examination of only the direct-child attributes. For the sake of processing
times, these direct-child attributes are not further expandable.

Predefined intermediate types include:

* bytesarray
* complex number
* datetime
* date
* time
* timezone
* pathlib paths

If you would like to add additional intermediate types that are specific to
your project, you can do that here. Be sure to list each type in the list as a
string of the type to treat as an intermediate type.

:Type: ``list``
:Default: ``[]``

Example::

    DJANGO_DD_ADDITIONAL_INTERMEDIATE_TYPES = [
        'Cell' #  From openpyxl package
    ]


DJANGO_DD_INCLUDE_PRIVATE_MEMBERS
=================================

By default, Private members (those that start with an underscore) are not
included in the output. If you would like to include private members in the
output set this setting to: ``True``

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_INCLUDE_PRIVATE_MEMBERS = True


DJANGO_DD_INCLUDE_MAGIC_METHODS
===============================

By default, Magic methods (those enclosed by dunders, ie `__str__`) are not
included in the output. If you would like to include magic methods in the
output, set this setting to ``True``.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_INCLUDE_MAGIC_METHODS = True


DJANGO_DD_INCLUDE_FILENAME_LINENUMBER
=====================================

By default, output will not include the filename and line number that dump or
dd was called from. If you would like to enable this, set this setting to
``True``.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_INCLUDE_FILENAME_LINENUMBER = True


DJANGO_DD_INCLUDE_ATTRIBUTES
============================

By default, all attributes for an object are included in the output. If you
would like to disable this, set this setting to ``False``.

:Type: ``bool``
:Default: ``True``

Example::

    DJANGO_DD_INCLUDE_ATTRIBUTES = False


DJANGO_DD_INCLUDE_FUNCTIONS
===========================

By default, all methods for an object are not included in the output. If you
would like to include them, set this setting to ``True``.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_INCLUDE_FUNCTIONS = True


DJANGO_DD_MULTILINE_FUNCTION_DOCS
=================================
By default, all function documentation output is collapsed into one line (aka
line breaks are ignored). To expand function doc output to multiple lines, set
this setting to ``True``.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_MULTILINE_FUNCTION_DOCS = True


DJANGO_DD_CONTENT_STARTS_EXPANDED
=================================

By default, everything is collapsed when dumped to the screen. Optionally,
each content item can be expanded to show the **Attribute** and
**Function** sections.

See below related ``DJANGO_DD_ATTRIBUTES_START_EXPANDED`` and
``DJANGO_DD_FUNCTIONS_START_EXPANDED`` settings for details of how those
sections are handled.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_CONTENT_STARTS_EXPANDED = True


DJANGO_DD_ATTRIBUTES_START_EXPANDED
===================================

Controls if Attribute sections are expanded on page load or not.

.. note::

    Only applies when ``DJANGO_DD_INCLUDE_ATTRIBUTES`` and
    ``DJANGO_DD_INCLUDE_FUNCTIONS`` are both set to ``True``.
    If **Attributes** are not turned on, they can't be expanded.
    If **Functions** are not also turned on, **Attributes** will automatically
    be expanded as they will be the only content available for the dumped
    object.

If set to ``True``, then opening an item will instantly show the fully
expanded Attribute section.

If set to ``False``, then opening an item will only show the Attribute
section header, and will need an additional click to expand.

:Type: ``bool``
:Default: ``True``

Example::

    DJANGO_DD_ATTRIBUTES_START_EXPANDED = False


DJANGO_DD_FUNCTIONS_START_EXPANDED
==================================

Controls if Function sections are expanded on page load or not.

.. note::

    Only applies when ``DJANGO_DD_INCLUDE_ATTRIBUTES`` and
    ``DJANGO_DD_INCLUDE_FUNCTIONS`` are both set to ``True``.
    If **Functions** are not turned on, they can't be expanded.
    If **Attributes** are not also turned on, **Functions** will automatically
    be expanded as they will be the only content available for the dumped
    object.

If set to ``True``, then opening an item will instantly show the fully
expanded Function section.

If set to ``False``, then opening an item will only show the Function
section header, and will need an additional click to expand.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_FUNCTIONS_START_EXPANDED = True


DJANGO_DD_INCLUDE_UTILITY_TOOLBAR
=================================

By default, a **Utility Toolbar** will show at top of the page during DD output.
This toolbar provides buttons to easily expand and collapse multiple objects
at once.

To hide this toolbar, set this setting to ``False``.

:Type: ``bool``
:Default: ``True``

Example::

    DJANGO_DD_INCLUDE_UTILITY_TOOLBAR = False


DJANGO_DD_COLORIZE_DUMPED_OBJECT_NAME
=====================================
By default, all dumped object names are syntax highlighted.
If you would like to disable this so that the dumped name is all the same color
regardless of its contents, set this setting to ``False``.

:Type: ``bool``
:Default: ``True``

Example::

    DJANGO_DD_COLORIZE_DUMPED_OBJECT_NAME = False


DJANGO_DD_FORCE_LIGHT_THEME
===========================

By default, the included color theme will change depending on the setting of
your browser to either light or dark. If you normally have your browser set to
dark but would like to force this tool to display the light theme, change this
setting to ``True``.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_FORCE_LIGHT_THEME = True


DJANGO_DD_FORCE_DARK_THEME
==========================

By default, the included color theme will change depending on the setting of
your browser to either light or dark. If you normally have your browser set to
light but would like to force this tool to display the dark theme, change this
setting to ``True``.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_FORCE_DARK_THEME = True


DJANGO_DD_COLOR_SCHEME
======================

By default, the tool uses the Solarized color scheme. If you want full control
over the color theme and would like to define your own, here is where you do
that. The format is in dictionary format and needs to follow the same format.
In the sample below, ``<value>`` should be a string hexcode for a color with
the hash symbol included.
EX: ``#FF88CC``.

.. note::
    Not all values need to be included. Any excluded values will fall back
    to a default. Feel free to only include the values you wish to modify.

:Type: ``dict``
:Default: ``None``



Example::

    DJANGO_DD_COLOR_SCHEME = {
        'light': {
            'color': <value>,               # Light theme default text color
            'background': <value>,          # Light theme background color
            'border': <value>,              # Light theme border color
            'toolbar_color': <value>,       # Light theme toolbar text color
            'toolbar_background': <value>,  # Light theme toolbar background color
        },
        'dark': {
            'color': <value>,               # Dark theme default text color
            'background': <value>,          # Dark theme background color
            'border': <value>,              # Dark theme border color
            'toolbar_color': <value>,       # Dark theme toolbar text color
            'toolbar_background': <value>,  # Dark theme toolbar background color
        },
        'meta': {
            'arrow': <value>,               #  Expand/Collapse arrow
            'access_modifier': <value>,     #  Access Modifier Char
            'braces': <value>,              #  Braces, Brackets, and Parentheses
            'empty': <value>,               #  No Attributes or methods available
            'location': <value>,            #  File location and line number
            'type': <value>,                #  Type text of dumped variable
            'unique': <value>,              #  Unique hash for class
        },
        'identifiers': {
            'section_name': <value>,        #  The words "Attribute" or "Function", denoting each sections
            'attribute': <value>,           #  Class attribute
            'constant': <value>,            #  Class constants
            'dumped_name': <value>,         #  Dumped object name
            'function': <value>,            #  Class functions
            'index': <value>,               #  Index values for indexable types
            'key': <value>,                 #  Key values for dict
            'params': <value>,              #  Function parameters
        },
        'types': {
            'bool': <value>,                #  Booleans
            'bound': <value>,               #  Django Bound Form Field
            'default': <value>,             #  Default color if does not fit into any of the others
            'docs': <value>,                #  Class function documentation
            'intermediate': <value>,        #  The brief description output for "Intermediate" types
            'module': <value>,              #  Module via ModuleType
            'none': <value>,                #  None
            'number': <value>,              #  Integers, Floats, and Decimals
            'string': <value>,              #  Strings
        }
    }
