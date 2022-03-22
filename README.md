Django Dump & Die
============================

Django App providing a mechanism for extracting the details of any python variable and dumping it to the browser.
This is effectively a debugging tool, used to quickly and easily output an object's full data to screen.

Inspired by the dump and dump/die functionality from Symfony / Laravel.


## Installation
Import the package via either:
```shell
python -m pip install -e "git+https://github.com/DJBarnes/django-dump-die#egg=django-dump-die"
```
or
```shell
pipenv install -e "git+https://github.com/DJBarnes/django-dump-die#egg=django-dump-die"
```

<br>

Next add the corresponding app to your Django `settings.py` file:
```python
INSTALLED_APPS = [
    ...

    'django_dump_die',

    ...
]
```

<br>

Lastly add the corresponding middleware to your Django `settings.py` file:
```python
MIDDLEWARE = [
    ...

    'django_dump_die.middleware.DumpAndDieMiddleware',

    ...
]
```

## Usage
The middleware is where most of this package's heavy lifting happens.

By having the middleware installed, you can run `dump(<value>)` and/or `dd(<value>)` anywhere you want, and it will run the dump logic.
No importing is required, nor is any extra logic. Just type **"dump"** and/or **"dd"** anywhere you want in a python file and it will run.
The `dump()` command will add the object to dump to an internal list to be dumped when a `dd()` is used.
You can have as many `dump(<value>)` statements as you want leading up to a `dd(<value>)`,
but in order for there to be actual output to the screen you must issue a `dd(<value)` as the last thing you do.

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

**Note:** that most editors will give a red error squiggle for the dd command.

This is intentional, and the command will still run. This is because this command is meant to be used for debugging,
and is not meant to stay long-term. The red squiggle helps identify it as something that should be removed before
any actual commits.

## Configuration
The package has a few configuration options available to you. Each of the following options can be set by adding the associated option and value into your settings file for Django.

### DJANGO_DD_MAX_RECURSION_DEPTH
Default: ```20```<br>
As the tool inspects an object it recurses into other objects that are part of the original object. This recursion could become quite deep depending on the size of the object being dumped. This setting will limit the depth of recursion as to prevent long processing times.
<br>
**NOTE:** Setting the value to ```None``` will mean no limit.
```python
DJANGO_DD_MAX_RECURSION_DEPTH = 30
```

### DJANGO_DD_MAX_ITERABLE_LENGTH
Default: ```20```<br>
As the tool inspects an iterable object it will recurse into each object in the iterable. This may mean a lot of recursion for a very long iterable. This setting will limit the length or processed elements in an iterable to prevent long processing times.
<br>
**NOTE:** Setting the value to ```None``` will mean no limit.
```python
DJANGO_DD_MAX_ITERABLE_LENGTH = 30
```

### DJANGO_DD_ADDITIONAL_SIMPLE_TYPES
Default: ```[]``` (Empty List)<br>
When the tool encounters a defined simple type it will no longer recurse further and instead simply output a string representation of that simple type.
Predefined simple types include:
* str
* bytes
* int
* float
* bool
* module
* BoundField

If you would like to add additional simple types that are specific to your project, you can do that here. Be sure to list each type in the list as a string of the type to treat as a simple type.
```python
DJANGO_DD_ADDITIONAL_SIMPLE_TYPES = [
    'Cell' #  From openpyxl package
}
```

### DJANGO_DD_INCLUDE_PRIVATE_MEMBERS
Default: ```False```<br>
By default, Private members (those that start with an underscore) are not included in the output. If you would like to include private members in the output set this setting to ```True```.
```python
DJANGO_DD_INCLUDE_PRIVATE_MEMBERS = True
```

### DJANGO_DD_INCLUDE_MAGIC_METHODS
Default: ```False```<br>
By default, Magic methods (those enclosed by dunders) are not included in the output. If you would like to include magic methods in the output, set this setting to ```True```.
<br>
**NOTE:** This is only for methods. Has no effect on attributes.
```python
DJANGO_DD_INCLUDE_MAGIC_METHODS = True
```

### DJANGO_DD_INCLUDE_ATTRIBUTES
Default: ```True```<br>
By default, all attributes for an object are included in the output. If you would like to disable this, set this setting to ```False```.
```python
DJANGO_DD_INCLUDE_ATTRIBUTES = False
```

### DJANGO_DD_INCLUDE_FUNCTIONS
Default: ```False```<br>
By default, all methods for an object are not included in the output. If you would like to include them, set this setting to ```True```.
```python
DJANGO_DD_INCLUDE_FUNCTIONS = True
```

### DJANGO_DD_ATTRIBUTE_TYPES_START_EXPANDED
Default: ```False```<br>
By default, everything is collapsed when dumped to the screen. If you would like the first level of expansion that shows the attribute types (Attributes and Functions heading) already expanded, set this setting to ```True```. This will not show you the attributes or functions for a method, but rather the headings for those sections.
```python
DJANGO_DD_ATTRIBUTE_TYPES_START_EXPANDED = True
```

### DJANGO_DD_ATTRIBUTES_START_EXPANDED
Default: ```True```<br>
By default, all attributes are already expanded so that when you expand a specific object to show the attribute types you can immediately see the attributes without having to also expand the attributes section. If you would rather have this closed by default, set this setting to ```False```.
```python
DJANGO_DD_ATTRIBUTES_START_EXPANDED = False
```

### DJANGO_DD_FUNCTIONS_START_EXPANDED
Default: ```False```<br>
By default, all functions are collapsed so that when you expand a specific object to show the attribute types you still have to manually expand the functions section. If you would rather have this section already expanded, set this setting to ```True```.
```python
DJANGO_DD_FUNCTIONS_START_EXPANDED = True
```

### DJANGO_DD_FORCE_LIGHT_THEME
Default: ```False```<br>
By default, the included color theme will change depending on the setting of your browser to either light or dark. If you normally have your browser set to dark but would like to force this tool to display the light theme, change this setting to ```True```
```python
DJANGO_DD_FORCE_LIGHT_THEME = True
```

### DJANGO_DD_FORCE_DARK_THEME
Default: ```False```<br>
By default, the included color theme will change depending on the setting of your browser to either light or dark. If you normally have your browser set to light but would like to force this tool to display the dark theme, change this setting to ```True```
```python
DJANGO_DD_FORCE_DARK_THEME = True
```

### DJANGO_DD_COLOR_SCHEME
Default: ```None```<br>
By default, the tool uses the Solarized color scheme. If you want full control over the color theme and would like to define your own, here is where you do that. The format is in dictionary format and needs to follow the same format. In the sample below, ```<value>``` should be a string hexcode for a color with the hash symbol included.
<br>
**EX:** ```#FF88CC```.
```python
{
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
        'docs': <value>,            #  Class function documentation
        'constant': <value>,        #  Class constants
        'index': <value>,           #  Index values for indexable types
        'key': <value>,             #  Key values for dict
        'string': <value>,          #  Strings
        'bool': <value>,            #  Bools
        'number': <value>,          #  Ints and Floats
        'none': <value>,            #  None
        'empty': <value>,           #  No Attributes or methods available
    }
}
```
