Django Dump & Die
============================

Django-Dump-Die is a [Django](https://www.djangoproject.com/) app that
provides a couple of debug tools, in the form of built-in methods
`dump` and `dd`. These allow sending details about a variable to the
browser for inspection.

Dumped variables are presented in an easy to read and
fully expandable / collapsible tree. You can easily understand complex objects
and the results of django queries with a simple call to either method.

When `dump` and/or `dd` are called, dump die will intercept the page
response and replace the contents of the response with detailed information
about the corresponding variables passed for inspection.

The entire concept is heavily based on the dump die functionality that comes
with Php's [Laravel](https://laravel.com/)
and [Symfony](https://symfony.com/) frameworks.

![dd_sample_output](https://user-images.githubusercontent.com/4390026/173413467-afcea349-a28b-42c0-bd18-5922df17b453.png)

## Quickstart
1.  Install the Django App via GitHub for now. Working on getting on Pypi soon.
    ```shell
    python -m pip install -e git+https://github.com/DJBarnes/django-dump-die@master
    ```
    or
    ```shell
    pipenv install -e "git+https://github.com/DJBarnes/django-dump-die#egg=django-dump-die"
    ```

<br>

2.  Add the corresponding app to your Django ``settings.py`` file:
    ```python
    INSTALLED_APPS = [

        'django_dump_die',
        ...
    ]
    ```

<br>

3.  Add the corresponding middleware to your Django ``settings.py`` file:
    ```python
    MIDDLEWARE = [

        'django_dump_die.middleware.DumpAndDieMiddleware',
        ...
    ]
    ```

4.  Ensure that you have **DEBUG** set to ``True`` in your Django ``settings.py`` file:
    ```python
    DEBUG = True
    ```

    ---
    :information_source: **NOTE**
    Neither the `dump` command nor the `dd` command will do anything if **DEBUG** is not set to `True`.
    With that said, this is a tool for debugging. You should not include this package
    in production nor should you ever have **DEBUG** set to `True` in production.

    ---

5.  From a file that is part of the request / response cycle such as a Django
    View in `views.py`, make a call to dd sending it the contents of a variable
    to inspect.

    **views.py**
    ```python
    def my_awesome_view(request):
        dd(request)
    ```

## Usage
The middleware is where most of this package's heavy lifting happens.

By having the middleware installed, you can run ``dump(<variable>)`` and/or
``dd(<variable>)`` in any file that is part of the request response cycle,
and it will run the dump logic. No importing or extra logic is required.

Each ``dump(<variable>)`` command will add the passed object to an internal
list that will be dumped either when a ``dd(<variable>)`` is used, or if the
entirety of the request finishes. You can have as many ``dump(<variable>)``
statements as you want leading up to an optional ``dd(<variable>)``.

If you make a call to ``dd(<variable>)``, execution will immediately stop
and all dumped objects (including the the one sent to dd) will be output.

If you do not make a call to ``dd(<variable>)`` and only use
``dump(<variable>)`` statements, the request will continue processing until
it is time to return the response. At this point, Django-Dump-Die will
intercept and replace the response with the data that has been dumped thus
far.

---
:information_source: **NOTE**
Because dump die uses middleware to internally handle keeping track of
what to dump and then actually dumping the data to the browser, any
call to ``dump`` or ``dd`` must be done in a file that will be processed
during the request response cycle. Most commonly this will be a
``views.py`` file, but could also be utils called from a view.
Attempting to ``dump`` or ``dd`` from a console command will not work.

---

<br>

Example:
```python
# Sample classes for output.
class EmptyClass:
    """Empty Class."""
    pass


class SomeClass:
    """Some Class."""
    SAMPLE_CONST = 41

    def __init__(self, *args, **kwargs):
        self.my_number = 32
        self.my_string = 'A super cool string'
        self.works = True
        self.nothing = None
        self.bytes = bytes('My Bytes', 'utf-8')
        self.list_o_stuff = ['A', 'B', 'C']
        self.sample_set = {'A', 'B', 'C'}
        self.sample_tuple = ('A', 12, True)
        self.empty_class = EmptyClass()
        self.empty_class_dup = self.empty_class

    def do_work(self):
        """Do some work"""
        return True


# Example Usage
empty_class = EmptyClass()
some_class = SomeClass()

dump('Simple String')
dump(empty_class)
dd(some_class)
```
![django-dump-die-sample-output](https://user-images.githubusercontent.com/4390026/159033583-b2d4d98e-52c1-487e-93a3-5c56e7038893.png)

<br>

---
:information_source: **NOTE**
Most editors will give a red error squiggle for the dd command.
This is intentional, and the command will still run. This is because this
command is meant to be used for debugging, and is not meant to stay
long-term. The red squiggle helps identify it as something that should be
removed before any actual commits.

---

### Available Parameters
Both the `dd()` and `dump()` functions take the same parameters, in the same ordering:

#### Arg1 / Kwarg: index_range
Type: ```int, list, tuple```<br>
Default: ```None```

An index range to modify output values of parent entity (if iterable).<br>
Allows changing the range of which direct-child indexes are fully examined. Only affects the direct children of the
outermost parent object. Can be useful with large datasets, when only wanting to examine a specific range of values.

When an index range is passed, the end index of that range overrides the `DJANGO_DD_MAX_ITERABLE_LENGTH` value set in settings.

Value can be:
* A single index.
* A range of two values, to specify starting and ending index (defined such as in a list or tuple).

**Example:**
```python
# Single index
dump(my_list, index_range=18)  # Will do from index 18 to 18 + DJANGO_DD_MAX_ITERABLE_LENGTH
# Range index
dd(my_list, index_range=(18, 37))  # Will do from index 18 to 37
```

#### Arg2 / Kwarg: deepcopy
Type: ```bool```<br>
Default: ```False```

A boolean to specify if passed objects should be deep-copied before being passed into dd/dump logic.<br>
If set to `True`, then preserves exact state of object at time of passing into dd/dump.
Useful if you are dumping an object, then making changes to that object, and then dumping it again.

**Example:**
```python
# Dump starting state
dump(my_list, deepcopy=True)
# Update list
my_list[5] = 42
# Dump updated state
dd(my_list)
```


## Configuration
The package has a few configuration options available to you. Each of the following options can be set by adding the associated option and value into your settings file for Django.

### DJANGO_DD_MAX_RECURSION_DEPTH
As the tool inspects an object it recurses into other objects that are part of the original object. This recursion could become quite deep depending on the size of the object being dumped. This setting will limit the depth of recursion as to prevent long processing times.
<br>

---
:information_source: **NOTE**
Setting the value to ```None``` will mean no limit.

---

Type: ```int```<br>
Default: ```20```

Example:
```python
DJANGO_DD_MAX_RECURSION_DEPTH = 30
```

### DJANGO_DD_MAX_ITERABLE_LENGTH
As the tool inspects an iterable object it will recurse into each object in the iterable. This may mean a lot of recursion for a very long iterable. This setting will limit the length or processed elements in an iterable to prevent long processing times.
<br>

---
:information_source: **NOTE**
Setting the value to ```None``` will mean no limit.

---

Type: ```int```<br>
Default: ```20```

Example:
```python
DJANGO_DD_MAX_ITERABLE_LENGTH = 30
```

### DJANGO_DD_ADDITIONAL_SIMPLE_TYPES
A "simple type" is a variable type which is common in most languages, and generally the user only want to see the literal assigned value.

When the tool encounters a defined simple type it will no longer recurse further and instead simply output a string representation of that simple type.

Predefined simple types include:
* bool
* BoundField
* bytes
* Decimal
* float
* int
* module
* str

If you would like to add additional simple types that are specific to your project, you can do that here. Be sure to list each type in the list as a string of the type to treat as a simple type.

Type: ```list```<br>
Default: ```[]```

Example:
```python
DJANGO_DD_ADDITIONAL_SIMPLE_TYPES = [
    'Cell' #  From openpyxl package
]
```

### DJANGO_DD_ADDITIONAL_INTERMEDIATE_TYPES
An "intermediate type" is a variable which may have useful properties for expanded output, but generally most users will only want to see the literal assigned value.

Some of these "intermediate type" variables have recurse an unhelpful number of times, if each attribute is examined fully.

When the tool encounters a defined intermediate type it will no longer recurse further and instead output a string representation as well as the direct attributes. For the sake of processing times, these attributes are not further expandable.

Predefined intermediate types include:
* bytesarray
* complex number
* datetime
* date
* time
* timezone
* pathlib paths

If you would like to add additional intermediate types that are specific to your project, you can do that here. Be sure to list each type in the list as a string of the type to treat as an intermediate type.

Type: ```list```<br>
Default: ```[]```

Example:
```python
DJANGO_DD_ADDITIONAL_INTERMEDIATE_TYPES = [
    'Cell' #  From openpyxl package
]
```

### DJANGO_DD_INCLUDE_PRIVATE_MEMBERS
By default, Private members (those that start with an underscore) are not included in the output. If you would like to include private members in the output set this setting to ```True```.

Type: ```bool```<br>
Default: ```False```

Example:
```python
DJANGO_DD_INCLUDE_PRIVATE_MEMBERS = True
```

### DJANGO_DD_INCLUDE_MAGIC_METHODS
By default, Magic methods (those enclosed by dunders) are not included in the output. If you would like to include magic methods in the output, set this setting to ```True```.
<br>

---
:information_source: **NOTE**
This is only for methods. Has no effect on attributes.

---

Type: ```bool```<br>
Default: ```False```

Example:
```python
DJANGO_DD_INCLUDE_MAGIC_METHODS = True
```

### DJANGO_DD_INCLUDE_FILENAME_LINENUMBER
By default, output will not include the filename and line number that dump or dd was called from. If you would like to enable this, set this setting to ```True```.

Type: ```bool```<br>
Default: ```False```

Example:
```python
DJANGO_DD_INCLUDE_FILENAME_LINENUMBER = True
```

### DJANGO_DD_INCLUDE_ATTRIBUTES
By default, all attributes for an object are included in the output. If you would like to disable this, set this setting to ```False```.

Type: ```bool```<br>
Default: ```True```

Example:
```python
DJANGO_DD_INCLUDE_ATTRIBUTES = False
```

### DJANGO_DD_INCLUDE_FUNCTIONS
By default, all methods for an object are not included in the output. If you would like to include them, set this setting to ```True```.

Type: ```bool```<br>
Default: ```False```

Example:
```python
DJANGO_DD_INCLUDE_FUNCTIONS = True
```

### DJANGO_DD_MULTILINE_FUNCTION_DOCS
By default, all function documentation output is collapsed into one line (aka line breaks are ignored). To expand function doc output to multiple lines, set this setting to ```True```.

Type: ```bool```<br>
Default: ```False```

Example:
```python
DJANGO_DD_MULTILINE_FUNCTION_DOCS = True
```

### DJANGO_DD_CONTENT_STARTS_EXPANDED
By default, everything is collapsed when dumped to the screen. Optionally, the each content item can be expanded to show the Attribute and Function sections.

See below related `DJANGO_DD_ATTRIBUTES_START_EXPANDED` and `DJANGO_DD_FUNCTIONS_START_EXPANDED` settings for details of how those sections are handled.

Type: ```bool```<br>
Default: ```False```

Example:
```python
DJANGO_DD_CONTENT_STARTS_EXPANDED = True
```

### DJANGO_DD_ATTRIBUTES_START_EXPANDED
Controls if Attribute sections are expanded on page load or not.

---
:information_source: **NOTE**
Only applies when ``DJANGO_DD_INCLUDE_ATTRIBUTES`` and
``DJANGO_DD_INCLUDE_FUNCTIONS`` are both set to ``True``.
If **Attributes** are not turned on, they can't be expanded.
If **Functions** are not also turned on, **Attributes** will automatically
be expanded as they will be the only content available for the dumped
object.

---

If set to `True`, then opening an item will instantly show the fully expanded Attribute section.

If set to `False`, then opening an item will only show the Attribute section header, and will need an additional click to expand.

Type: ```bool```<br>
Default: ```True```

Example:
```python
DJANGO_DD_ATTRIBUTES_START_EXPANDED = False
```

### DJANGO_DD_FUNCTIONS_START_EXPANDED
Controls if Function sections are expanded on page load or not.

---
:information_source: **NOTE**
Only applies when ``DJANGO_DD_INCLUDE_ATTRIBUTES`` and
``DJANGO_DD_INCLUDE_FUNCTIONS`` are both set to ``True``.
If **Functions** are not turned on, they can't be expanded.
If **Attributes** are not also turned on, **Functions** will automatically
be expanded as they will be the only content available for the dumped
object.

---

If set to `True`, then opening an item will instantly show the fully expanded Function section.

If set to `False`, then opening an item will only show the Function section header, and will need an additional click to expand.

Type: ```bool```<br>
Default: ```False```

Example:
```python
DJANGO_DD_FUNCTIONS_START_EXPANDED = True
```


### DJANGO_DD_INCLUDE_UTILITY_TOOLBAR
By default, a **Utility Toolbar** will show at top of the page during DD output.
This toolbar provides buttons to easily expand and collapse multiple objects
at once.

Type: ```bool```<br>
Default: ```True```

Example:
```python
DJANGO_DD_INCLUDE_UTILITY_TOOLBAR = False
```

### DJANGO_DD_COLORIZE_DUMPED_OBJECT_NAME
By default, all dumped object names are syntax highlighted. If you would like to disable this so that the dumped name is all the same color regardless of its contents, set this setting to ```False```.

Type: ```bool```<br>
Default: ```True```

Example:
```python
DJANGO_DD_COLORIZE_DUMPED_OBJECT_NAME = False
```

### DJANGO_DD_FORCE_LIGHT_THEME
By default, the included color theme will change depending on the setting of your browser to either light or dark. If you normally have your browser set to dark but would like to force this tool to display the light theme, change this setting to ```True```.

Type: ```bool```<br>
Default: ```False```

Example:
```python
DJANGO_DD_FORCE_LIGHT_THEME = True
```

### DJANGO_DD_FORCE_DARK_THEME
By default, the included color theme will change depending on the setting of your browser to either light or dark. If you normally have your browser set to light but would like to force this tool to display the dark theme, change this setting to ```True```

Type: ```bool```<br>
Default: ```False```

Example:
```python
DJANGO_DD_FORCE_DARK_THEME = True
```

### DJANGO_DD_COLOR_SCHEME
By default, the tool uses the Solarized color scheme. If you want full control over the color theme and would like to define your own, here is where you do that. The format is in dictionary format and needs to follow the same format. In the sample below, ```<value>``` should be a string hexcode for a color with the hash symbol included.

**EX:** ```#FF88CC```.

---
:information_source: **NOTE**
Not all values need to be included. Any excluded values will fall back
to a default. Feel free to only include the values you wish to modify.

---

Type: ```dict```<br>
Default: ```None```

Example:
```python
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
    },
}
```
