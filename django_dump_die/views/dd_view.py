"""Core view for DumpDie library. All logic renders from this."""

# Third-Party Imports.
from django.conf import settings
from django.shortcuts import render
from django.template.loader import render_to_string


def dd_view(request, objects, template_name="django_dump_die/dd.html", extra_context={}, as_string=False):
    """
    Return DumpDie view.
    :param request: Request object.
    :param objects: Set of objects to dump.
    """
    # Get toolbar options.
    include_util_toolbar = getattr(settings, "DJANGO_DD_INCLUDE_UTILITY_TOOLBAR", True)
    attrs_enabled = getattr(settings, "DJANGO_DD_INCLUDE_ATTRIBUTES", True)
    funcs_enabled = getattr(settings, "DJANGO_DD_INCLUDE_FUNCTIONS", False)

    # Get user theme choices.
    force_light_theme = getattr(settings, "DJANGO_DD_FORCE_LIGHT_THEME", False)
    force_dark_theme = getattr(settings, "DJANGO_DD_FORCE_DARK_THEME", False)
    custom_color_theme = getattr(settings, "DJANGO_DD_COLOR_SCHEME", None)
    multiline_function_docs = getattr(settings, "DJANGO_DD_MULTILINE_FUNCTION_DOCS", False)

    # Validate chosen themes.
    if force_light_theme and force_dark_theme:
        raise ValueError("You can't force both light and dark themes.")

    context = {
        "objects": objects,
        "include_util_toolbar": include_util_toolbar,
        "attrs_enabled": attrs_enabled,
        "funcs_enabled": funcs_enabled,
        "force_light_theme": force_light_theme,
        "force_dark_theme": force_dark_theme,
        "custom_color_theme": custom_color_theme,
        "multiline_function_docs": multiline_function_docs,
    }
    context.update(extra_context)

    # If returning the raw string, render to string and return string.
    if as_string:
        return render_to_string(template_name, context, request)

    # Render template.
    return render(request, template_name, context)
