"""
Browser tests for the DumpDie page's JavaScript: expanding and collapsing, the toolbar, and duplicate highlighting.

Need selenium and a browser. Choose the browser with the DJANGO_DD_SELENIUM_BROWSER environment variable
("firefox" by default, "chrome", or "none" to skip these tests), and set DJANGO_DD_SELENIUM_HEADLESS=true to run
it without a window.
"""

# System Imports.
from importlib.util import find_spec
from unittest import skipIf
from unittest.mock import patch

# Third-Party Imports.
from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.test import override_settings
from django.urls import reverse
from django_expanded_test_cases import LiveServerTestCase

SELENIUM_PRESENT = find_spec("selenium") is not None
SKIP_REASON = None
if not SELENIUM_PRESENT:
    SKIP_REASON = "The selenium package is not installed."
elif settings.DJANGO_DD_SELENIUM_BROWSER == "none":
    SKIP_REASON = "Browser tests are turned off with DJANGO_DD_SELENIUM_BROWSER=none."

if SELENIUM_PRESENT:
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait


# State of every toggle on the page, for checking what is open.
TOGGLE_STATES = """
return Array.from(document.querySelectorAll('.arrow-toggle')).map((toggle) => {
    const section = toggle.nextElementSibling;
    return {
        type: toggle.dataset.ddType,
        depth: toggle.dataset.objectDepth || null,
        collapsible: toggle.dataset.ddToggle === 'collapse',
        arrow: toggle.querySelector(':scope > .arrow').textContent.trim(),
        aria: toggle.getAttribute('aria-expanded'),
        toggle_collapsed: toggle.classList.contains('collapsed'),
        shown: section.classList.contains('show'),
        transitioning: section.classList.contains('collapsing'),
        displayed: section.offsetParent !== null,
    };
});
"""


@skipIf(SKIP_REASON is not None, SKIP_REASON)
@override_settings(DEBUG=True)
class DumpDieBrowserTestCase(LiveServerTestCase):
    """Verify expanding and collapsing in a browser."""

    # Serve static files from the apps, like StaticLiveServerTestCase, since the test settings have no STATIC_ROOT.
    static_handler = StaticFilesHandler

    @classmethod
    def setUpClass(cls):
        # Create the driver here instead of in the parent, so that the browser binary can be set first.
        super().setUpClass(initial_driver_count=0)
        if settings.DJANGO_DD_SELENIUM_BROWSER_BINARY:
            cls._options.binary_location = settings.DJANGO_DD_SELENIUM_BROWSER_BINARY
        cls.create_driver(cls)

    def setUp(self):
        super().setUp()
        self.driver = self.get_driver()

    def open_page(self, url_name="django_dump_die__tests__browser:nested"):
        """Open a test page and wait for the DumpDie script to be set up."""
        self.driver.get(self.live_server_url + reverse(url_name))
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script(
                "return typeof djangoDumpDie !== 'undefined' && djangoDumpDie.isSetUp === true"
            )
        )

    def get_states(self):
        """Wait for any open/close animation to finish, then get the state of every toggle."""
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script("return document.querySelectorAll('.collapsing').length === 0")
        )
        return self.driver.execute_script(TOGGLE_STATES)

    def assertToggleState(self, state, open):
        """Assert that a collapsible toggle and its section are open or closed, consistently."""
        self.assertEqual(state["shown"], open, state)
        self.assertEqual(state["arrow"], "▼" if open else "▶", state)
        self.assertEqual(state["aria"], "true" if open else "false", state)
        self.assertEqual(state["toggle_collapsed"], not open, state)

    def click_toolbar(self, button_id):
        """Click a toolbar button, hovering over its dropdown first, which shows the buttons inside it."""
        button = self.driver.find_element(By.CSS_SELECTOR, ".dump-toolbar #{0}".format(button_id))
        dropdown = button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'dropdown-container')]")
        ActionChains(self.driver).move_to_element(dropdown).move_to_element(button).click().perform()

    def test_page_does_not_load_jquery_or_bootstrap_js(self):
        """Verify the page works without loading jQuery or Bootstrap's JavaScript."""
        self.open_page()

        self.assertTrue(self.driver.execute_script("return typeof window.jQuery === 'undefined'"))
        self.assertTrue(self.driver.execute_script("return typeof window.bootstrap === 'undefined'"))

    def test_click_opens_and_closes_a_section_with_animation(self):
        """Verify clicking a toggle animates its section open, and clicking again animates it closed."""
        self.open_page()
        toggle = self.driver.find_elements(By.CSS_SELECTOR, '.arrow-toggle[data-object-depth="1"]')[0]
        self.assertToggleState(self.get_states()[0], False)

        # The section animates open, so it is "collapsing" right after the click.
        transitioning = self.driver.execute_script(
            "arguments[0].click(); return arguments[0].nextElementSibling.classList.contains('collapsing');",
            toggle,
        )
        self.assertTrue(transitioning)
        state = self.get_states()[0]
        self.assertToggleState(state, True)
        self.assertTrue(state["displayed"])

        transitioning = self.driver.execute_script(
            "arguments[0].click(); return arguments[0].nextElementSibling.classList.contains('collapsing');",
            toggle,
        )
        self.assertTrue(transitioning)
        state = self.get_states()[0]
        self.assertToggleState(state, False)
        self.assertFalse(state["displayed"])

    def test_ctrl_click_opens_and_closes_everything_inside(self):
        """Verify CTRL+click on a toggle also opens or closes every section inside its section."""
        self.open_page()
        root = self.driver.find_element(By.CSS_SELECTOR, '.arrow-toggle[data-object-depth="1"]')

        ActionChains(self.driver).key_down(Keys.CONTROL).click(root).key_up(Keys.CONTROL).perform()
        states = self.get_states()
        collapsible = [state for state in states if state["collapsible"]]
        self.assertGreater(len(collapsible), 3)
        for state in collapsible:
            self.assertToggleState(state, True)
        # The "always show" Attributes sections stay open, with no arrow.
        always_show = [state for state in states if not state["collapsible"]]
        self.assertGreater(len(always_show), 0)
        for state in always_show:
            self.assertTrue(state["shown"], state)
            self.assertEqual(state["arrow"], "", state)

        ActionChains(self.driver).key_down(Keys.CONTROL).click(root).key_up(Keys.CONTROL).perform()
        for state in self.get_states():
            if state["collapsible"]:
                self.assertToggleState(state, False)
            else:
                self.assertTrue(state["shown"], state)

    def test_toolbar_expands_and_collapses_all(self):
        """Verify the toolbar's "Expand All" and "Collapse All" buttons open and close every section."""
        self.open_page()

        self.click_toolbar("expand-all")
        for state in self.get_states():
            if state["collapsible"]:
                self.assertToggleState(state, True)

        self.click_toolbar("collapse-all")
        for state in self.get_states():
            if state["collapsible"]:
                self.assertToggleState(state, False)

    def test_toolbar_expands_and_collapses_one_level(self):
        """Verify the toolbar's level buttons only open and close sections at that depth."""
        self.open_page()

        self.click_toolbar("expand-1st-lvl")
        for state in self.get_states():
            if state["collapsible"] and state["type"] == "type":
                self.assertToggleState(state, state["depth"] == "1")

        self.click_toolbar("expand-2nd-lvl")
        self.click_toolbar("collapse-1st-lvl")
        for state in self.get_states():
            if state["collapsible"] and state["type"] == "type":
                self.assertToggleState(state, state["depth"] == "2")

        self.click_toolbar("collapse-2nd-lvl")
        for state in self.get_states():
            if state["collapsible"] and state["type"] == "type":
                self.assertToggleState(state, False)

    # The setting shows the toolbar's type buttons, and the patched constant adds the Functions sections.
    @override_settings(DJANGO_DD_INCLUDE_FUNCTIONS=True)
    @patch("django_dump_die.templatetags.dump_die.INCLUDE_FUNCTIONS", True)
    def test_toolbar_expands_and_collapses_one_section_type(self):
        """Verify the toolbar's type, attribute, and function buttons only open and close those sections."""
        self.open_page()
        types = {state["type"] for state in self.get_states() if state["collapsible"]}
        self.assertEqual(types, {"type", "attr", "func"})

        for name, section_type in (("types", "type"), ("attrs", "attr"), ("funcs", "func")):
            with self.subTest(button=name):
                self.click_toolbar("expand-{0}".format(name))
                for state in self.get_states():
                    if state["collapsible"] and state["type"] == section_type:
                        self.assertToggleState(state, True)

                self.click_toolbar("collapse-{0}".format(name))
                for state in self.get_states():
                    if state["collapsible"] and state["type"] == section_type:
                        self.assertToggleState(state, False)

    def test_duplicate_uniques_highlight_together(self):
        """Verify hovering over a unique that appears more than once highlights all of its copies."""
        self.open_page()
        self.click_toolbar("expand-all")
        self.get_states()
        duplicates = self.driver.execute_script("return Array.from(djangoDumpDie.duplicateGroups.values())[0];")
        self.assertEqual(len(duplicates), 2)
        other = self.driver.find_element(By.CSS_SELECTOR, ".dump-toolbar h1")

        ActionChains(self.driver).move_to_element(duplicates[0]).perform()
        for element in duplicates:
            self.assertNotEqual(element.get_attribute("style"), "")

        ActionChains(self.driver).move_to_element(other).perform()
        for element in duplicates:
            self.assertEqual(element.get_attribute("style") or "", "")

    def test_template_dump_toggles_work_without_toolbar(self):
        """Verify sections from the dump template tag open and close in a normal page."""
        self.open_page("django_dump_die__tests__browser:template_dump")
        toggle = self.driver.find_element(By.CSS_SELECTOR, '.arrow-toggle[data-object-depth="1"]')

        toggle.click()
        self.assertToggleState(self.get_states()[0], True)
        toggle.click()
        self.assertToggleState(self.get_states()[0], False)
