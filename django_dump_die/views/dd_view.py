"""Core view for DumpDie library. All logic renders from this."""

# Third-Party Imports.
from django.shortcuts import render
from django.template.loader import render_to_string

# Internal Imports.
from django_dump_die.app_settings import app_settings


def dd_view(request, objects, template_name="django_dump_die/dd.html", extra_context=None, as_string=False):
    """
    Return DumpDie view.
    :param request: Request object.
    :param objects: Set of objects to dump.
    """
    # Get toolbar options.
    include_util_toolbar = app_settings.INCLUDE_UTILITY_TOOLBAR
    attrs_enabled = app_settings.INCLUDE_ATTRIBUTES
    funcs_enabled = app_settings.INCLUDE_FUNCTIONS
    results_enabled = app_settings.INCLUDE_FUNCTION_RESULTS

    # Get user theme choices.
    force_light_theme = app_settings.FORCE_LIGHT_THEME
    force_dark_theme = app_settings.FORCE_DARK_THEME
    custom_color_theme = app_settings.COLOR_SCHEME
    multiline_function_docs = app_settings.MULTILINE_FUNCTION_DOCS

    # Validate chosen themes.
    if force_light_theme and force_dark_theme:
        raise ValueError("You can't force both light and dark themes.")

    context = {
        "objects": objects,
        "include_util_toolbar": include_util_toolbar,
        "attrs_enabled": attrs_enabled,
        "funcs_enabled": funcs_enabled,
        "results_enabled": results_enabled,
        # With more than one section, each section has its own arrow, and the toolbar has buttons for each.
        "sections_collapsible": sum(bool(enabled) for enabled in (attrs_enabled, results_enabled, funcs_enabled)) > 1,
        "force_light_theme": force_light_theme,
        "force_dark_theme": force_dark_theme,
        "custom_color_theme": custom_color_theme,
        "multiline_function_docs": multiline_function_docs,
    }
    context.update(extra_context or {})

    # If returning the raw string, render to string and return string.
    if as_string:
        return render_to_string(template_name, context, request)

    # Render template.
    return render(request, template_name, context)
