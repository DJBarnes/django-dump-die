Configuration
=============

There are various configuration options that can be set via Django Settings to
control the overall look, feel, and functionality of the tool.


DJANGO_DD_MAX_RECURSION_DEPTH
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As the tool inspects an object it recurses into other objects that are part of
the original object. This recursion could become quite deep depending on the
size of the object being dumped. This setting will limit the depth of recursion
as to prevent long processing times.
**NOTE:** Setting the value to ```None``` will mean no limit.

:Type: ``int``
:Default: ``20``

Example::

    DJANGO_DD_MAX_RECURSION_DEPTH = 30



DJANGO_DD_MAX_ITERABLE_LENGTH
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As the tool inspects an iterable object it will recurse into each object in the
iterable. This may mean a lot of recursion for a very long iterable. This
setting will limit the length or processed elements in an iterable to prevent
long processing times.
**NOTE:** Setting the value to ```None``` will mean no limit.

:Type: ``int``
:Default: ``20``

Example::

    DJANGO_DD_MAX_ITERABLE_LENGTH = 30


DJANGO_DD_ADDITIONAL_SIMPLE_TYPES
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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


DJANGO_DD_ADDITIONAL_PSUEDO_SIMPLE_TYPES
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When the tool encounters a defined pseudo-simple type it will no longer recurse
further and instead simply output a string representation of that pseudo-simple type.
Predefined pseudo-simple types include:

* datetime
* date
* time
* timezone

If you would like to add additional simple types that are specific to your
project, you can do that here. Be sure to list each type in the list as a
string of the type to treat as a simple type.

:Type: ``list``
:Default: ``[]``

Example::

    DJANGO_DD_ADDITIONAL_PSEUDO_SIMPLE_TYPES = [
        'Cell' #  From openpyxl package
    ]


DJANGO_DD_INCLUDE_PRIVATE_MEMBERS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, Private members (those that start with an underscore) are not
included in the output. If you would like to include private members in the
output set this setting to: ``True``

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_INCLUDE_PRIVATE_MEMBERS = True


DJANGO_DD_INCLUDE_MAGIC_METHODS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, Magic methods (those enclosed by dunders) are not included in the
output. If you would like to include magic methods in the output, set this
setting to ``True``.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_INCLUDE_MAGIC_METHODS = True


DJANGO_DD_INCLUDE_ATTRIBUTES
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, all attributes for an object are included in the output. If you
would like to disable this, set this setting to ``False``.

:Type: ``bool``
:Default: ``True``

Example::

    DJANGO_DD_INCLUDE_ATTRIBUTES = False


DJANGO_DD_INCLUDE_FUNCTIONS
^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, all methods for an object are not included in the output. If you
would like to include them, set this setting to ``True``.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_INCLUDE_FUNCTIONS = True


DJANGO_DD_MULTILINE_FUNCTION_DOCS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
By default, all function documentation output is collapsed into one line (aka
line breaks are ignored). To expand function doc output to multiple lines, set
this setting to ``True``.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_MULTILINE_FUNCTION_DOCS = True


DJANGO_DD_ATTRIBUTE_TYPES_START_EXPANDED
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, everything is collapsed when dumped to the screen. If you would
like the first level of expansion that shows the attribute types (Attributes
and Functions heading) already expanded, set this setting to ``True``. This
will not show you the attributes or functions for a method, but rather the
headings for those sections.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_ATTRIBUTE_TYPES_START_EXPANDED = True


DJANGO_DD_ATTRIBUTES_START_EXPANDED
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, all attributes are already expanded so that when you expand a
specific object to show the attribute types you can immediately see the
attributes without having to also expand the attributes section. If you would
rather have this closed by default, set this setting to ``False``.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_ATTRIBUTES_START_EXPANDED = True


DJANGO_DD_FUNCTIONS_START_EXPANDED
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, all functions are collapsed so that when you expand a specific
object to show the attribute types you still have to manually expand the
functions section. If you would rather have this section already expanded, set
this setting to ``True``.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_FUNCTIONS_START_EXPANDED = True


DJANGO_DD_FORCE_LIGHT_THEME
^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, the included color theme will change depending on the setting of
your browser to either light or dark. If you normally have your browser set to
dark but would like to force this tool to display the light theme, change this
setting to ``True``.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_FORCE_LIGHT_THEME = True


DJANGO_DD_FORCE_DARK_THEME
^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, the included color theme will change depending on the setting of
your browser to either light or dark. If you normally have your browser set to
light but would like to force this tool to display the dark theme, change this
setting to ``True``.

:Type: ``bool``
:Default: ``False``

Example::

    DJANGO_DD_FORCE_DARK_THEME = True


DJANGO_DD_COLOR_SCHEME
^^^^^^^^^^^^^^^^^^^^^^

By default, the tool uses the Solarized color scheme. If you want full control
over the color theme and would like to define your own, here is where you do
that. The format is in dictionary format and needs to follow the same format.
In the sample below, ``<value>`` should be a string hexcode for a color with
the hash symbol included.
EX: ``#FF88CC``.

:Type: ``dict``
:Default: ``None``

Example::

    DJANGO_DD_COLOR_SCHEME = {
        'light': {
            'color': <value>,
            'background': <value>,
        },
        'dark': {
            'color': <value>,
            'background': <value>
        },
        'types': {
            'arrow': <value>,           #  Expand/Collapse arrow
            'unique': <value>,          #  Unique hash for class
            'access_modifier': <value>, #  Access Modifier Char
            'type': <value>,            #  Complex Types (non-int, float, string, bool, None)
            'attribute': <value>,       #  Class attribute
            'function': <value>,        #  Class functions
            'module': <value>,          #  Module via ModuleType
            'bound': <value>,           #  Django Bound Form Field
            'docs': <value>,            #  Class function documentation
            'constant': <value>,        #  Class constants
            'index': <value>,           #  Index values for indexable types
            'key': <value>,             #  Key values for dict
            'string': <value>,          #  Strings
            'bool': <value>,            #  Bools
            'number': <value>,          #  Ints and Floats
            'datetime': <value>,        #  DateTimes and similar types
            'none': <value>,            #  None
            'empty': <value>,           #  No Attributes or methods available
            'default': <value>,         #  Default color if does not fit into any of the above
        }
    }
