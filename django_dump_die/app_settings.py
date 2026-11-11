"""
Settings for DumpDie, read from the project's Django settings.

Use them as attributes of app_settings, such as app_settings.MAX_RECURSION_DEPTH. Each is the Django setting of the
same name with the DJANGO_DD_ prefix, such as DJANGO_DD_MAX_RECURSION_DEPTH, or its default if the project doesn't
set it.

Settings are read each time they are used, not once on import. So override_settings works for them, in this
package's tests and in a project's own tests. And as attributes, instead of setting names in strings, a misspelled
setting is caught by editors, and by the package's tests (see general/test_app_settings.py).

Every setting is documented in docs/source/configuration.rst.
"""

# System Imports.
import copy

# Third-Party Imports.
from django.conf import settings

SETTING_PREFIX = "DJANGO_DD_"


class Setting:
    """
    A DumpDie setting, read from the Django setting of the same name with the DJANGO_DD_ prefix.

    A descriptor: as a class attribute of AppSettings, it reads the Django setting each time the attribute is used.
    """

    def __init__(self, default):
        self.default = default
        self.name = None
        self.setting_name = None

    def __set_name__(self, owner, name):
        self.name = name
        self.setting_name = SETTING_PREFIX + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        # A copy of a default list or dict, so that changing it doesn't change the default.
        return getattr(settings, self.setting_name, copy.copy(self.default))


class AppSettings:
    """DumpDie settings, with their defaults. See the module docstring."""

    # Object Output.
    # Max recursion depth to go while processing the dumped variable. Deep recursion will cause DD to take forever on
    # complex structures.
    MAX_RECURSION_DEPTH = Setting(5)
    # Max number of entries in an iterable to process further with recursion. After reaching an entry beyond this
    # length, it will just print the unique instead of recursing into the entry to find further details.
    # EX: if set to 20, a list of 30 will recursively inspect and print out 20 items and then simply print the unique
    # for the last 10.
    MAX_ITERABLE_LENGTH = Setting(20)
    # Class names of additional simple types, which are not recursively inspected.
    ADDITIONAL_SIMPLE_TYPES = Setting([])
    # Class names of additional intermediate types, which are only inspected one level deep.
    ADDITIONAL_INTERMEDIATE_TYPES = Setting([])
    # Whether the output should include private attributes and functions.
    INCLUDE_PRIVATE_MEMBERS = Setting(False)
    # Whether values whose names look sensitive, such as passwords, secret keys, tokens, and the session cookie, are
    # shown. Off by default, so that they are hidden like on Django's debug page. See utils.is_sensitive_name().
    SHOW_SENSITIVE_VALUES = Setting(False)
    # Whether the output should include magic methods.
    INCLUDE_MAGIC_METHODS = Setting(False)
    # Whether each dump should include the filename and linenumber of the dump call.
    INCLUDE_FILENAME_LINENUMBER = Setting(False)
    # Whether attributes should be included in the output.
    INCLUDE_ATTRIBUTES = Setting(True)
    # Whether the relations of model instances should be included in the output, in their own section.
    INCLUDE_RELATIONS = Setting(True)
    # How many relation steps from the dumped object to follow relations that return one object, such as foreign
    # keys, querying the database for those not loaded already. 0 only shows what is loaded.
    RELATED_OBJECT_DEPTH = Setting(3)
    # Whether functions should be included in the output.
    INCLUDE_FUNCTIONS = Setting(False)
    # Whether the results of some functions should be included in the output. Off by default, since it runs code.
    INCLUDE_FUNCTION_RESULTS = Setting(False)
    # Functions whose results are shown, by class name. A class's entry replaces its entry in
    # constants.DEFAULT_FUNCTION_RESULTS.
    FUNCTION_RESULTS = Setting({})
    # Whether dump() and dd() dump a deep copy of each object, as it is when dumped, instead of the object as it is when
    # the page is shown. The deepcopy argument of a call overrides it.
    DEEPCOPY = Setting(False)
    # Whether function doc output should try to fit on one line, or output with original newlines.
    MULTILINE_FUNCTION_DOCS = Setting(False)
    # Line shown across a break added with dump.br(): one of constants.BREAK_STYLES.
    BREAK_STYLE = Setting("dashed")
    # Default height of a break added with dump.br(), as a whole number of lines.
    BREAK_SIZE = Setting(1)

    # Expanding and Collapsing.
    # Whether objects overarching item content (Attribute, Function) should start expanded for viewing.
    CONTENT_STARTS_EXPANDED = Setting(False)
    # Whether the attributes for an object should start expanded for viewing.
    ATTRIBUTES_START_EXPANDED = Setting(True)
    # Whether the relations of a model instance should start expanded for viewing.
    RELATIONS_START_EXPANDED = Setting(True)
    # Whether the function results for an object should start expanded for viewing.
    FUNCTION_RESULTS_START_EXPANDED = Setting(True)
    # Whether the functions for an object should start expanded for viewing.
    FUNCTIONS_START_EXPANDED = Setting(False)

    # Page.
    # Whether the dump page shows the toolbar, with buttons to expand and collapse many objects at once.
    INCLUDE_UTILITY_TOOLBAR = Setting(True)
    # Whether dump() without dd() shows the dumps above an HTML page's own content, instead of replacing the page.
    SHOW_DUMPS_ABOVE_PAGE = Setting(False)
    # Whether dumps are shown above Django's error page, after an unhandled exception.
    SHOW_DUMPS_ON_ERROR_PAGE = Setting(True)
    # Whether or not to colorize the name of the dumped object.
    COLORIZE_DUMPED_OBJECT_NAME = Setting(True)

    # Colors.
    # Use the light or dark theme, instead of the one that matches the browser's preference. Not both.
    FORCE_LIGHT_THEME = Setting(False)
    FORCE_DARK_THEME = Setting(False)
    # Custom colors, as a dict. See configuration.rst.
    COLOR_SCHEME = Setting(None)


app_settings = AppSettings()
