/**
 * Expand/collapse, toolbar, and duplicate highlighting for Django DumpDie output.
 *
 * Plain JavaScript, with no jQuery or Bootstrap JavaScript.
 * Uses Bootstrap's "collapse", "collapsing", and "show" classes, so that Bootstrap's CSS
 * still hides collapsed sections and animates the height while they open and close.
 *
 * Each toggle (".arrow-toggle") is directly followed by the section it opens and closes
 * (".dd-wrapper" or ".li-wrapper"), and contains that section's arrow (".arrow").
 * All handlers are delegated from the document, so the cost of a click does not grow
 * with the size of the dump.
 */
const djangoDumpDie = {

    // Arrow text for each state.
    ARROW_OPEN: '▼',
    ARROW_CLOSED: '▶',

    // Length of Bootstrap's collapse transition (.collapsing), plus a margin, in milliseconds.
    // Used to finish a transition if no "transitionend" event arrives (such as for an element that isn't displayed).
    TRANSITION_FALLBACK_MS: 400,

    /**
     * Section that a toggle opens and closes.
     */
    getSection(toggle) {
        const section = toggle.nextElementSibling;
        if (section && (section.classList.contains('dd-wrapper') || section.classList.contains('li-wrapper'))) {
            return section;
        }
        return null;
    },

    /**
     * Whether a toggle can be opened and closed. "Always show" sections can't.
     */
    isCollapsible(toggle) {
        return toggle.dataset.ddToggle === 'collapse';
    },

    /**
     * Whether a section is open, or opening.
     */
    isOpen(section) {
        return section.classList.contains('show') || section.dataset.ddTransition === 'show';
    },

    /**
     * Set a toggle's state and arrow to match whether its section is open.
     */
    setToggleState(toggle, open) {
        toggle.classList.toggle('collapsed', !open);
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        const arrow = toggle.querySelector(':scope > .arrow');
        if (arrow) {
            arrow.textContent = open ? djangoDumpDie.ARROW_OPEN : djangoDumpDie.ARROW_CLOSED;
        }
    },

    /**
     * Open or close a toggle's section at once, without animation.
     * Used for many sections at a time, where animating each one would be slow.
     */
    setOpen(toggle, open) {
        const section = djangoDumpDie.getSection(toggle);
        if (!section || !djangoDumpDie.isCollapsible(toggle)) {
            return;
        }
        djangoDumpDie.finishTransition(section);
        section.classList.add('collapse');
        section.classList.toggle('show', open);
        djangoDumpDie.setToggleState(toggle, open);
    },

    /**
     * End a running open/close animation on a section, leaving it in its final state.
     */
    finishTransition(section) {
        const transition = section.dataset.ddTransition;
        if (!transition) {
            return;
        }
        clearTimeout(section._ddTransitionTimer);
        section.removeEventListener('transitionend', section._ddTransitionEnd);
        delete section.dataset.ddTransition;
        section.classList.remove('collapsing');
        section.classList.add('collapse');
        section.classList.toggle('show', transition === 'show');
        section.style.height = '';
    },

    /**
     * Wait for a section's height transition to end, then leave it in its final state.
     */
    onTransitionEnd(section) {
        const finish = (event) => {
            if (event && event.target !== section) {
                // A transition of a nested section, which bubbled up.
                return;
            }
            djangoDumpDie.finishTransition(section);
        };
        section._ddTransitionEnd = finish;
        section.addEventListener('transitionend', finish);
        section._ddTransitionTimer = setTimeout(finish, djangoDumpDie.TRANSITION_FALLBACK_MS);
    },

    /**
     * Open a toggle's section, animating its height like Bootstrap's collapse.
     */
    show(toggle) {
        const section = djangoDumpDie.getSection(toggle);
        if (!section || djangoDumpDie.isOpen(section)) {
            return;
        }
        djangoDumpDie.finishTransition(section);
        djangoDumpDie.setToggleState(toggle, true);

        section.dataset.ddTransition = 'show';
        section.classList.remove('collapse');
        section.classList.add('collapsing');
        section.style.height = '0';
        djangoDumpDie.onTransitionEnd(section);
        // Reading scrollHeight starts the transition from a height of 0.
        section.style.height = section.scrollHeight + 'px';
    },

    /**
     * Close a toggle's section, animating its height like Bootstrap's collapse.
     */
    hide(toggle) {
        const section = djangoDumpDie.getSection(toggle);
        if (!section || !djangoDumpDie.isOpen(section)) {
            return;
        }
        djangoDumpDie.finishTransition(section);
        djangoDumpDie.setToggleState(toggle, false);

        // Start from the current height, then let .collapsing animate it to 0.
        section.style.height = section.getBoundingClientRect().height + 'px';
        // Reading offsetHeight applies the height before the transition starts.
        section.offsetHeight;
        section.dataset.ddTransition = 'hide';
        section.classList.add('collapsing');
        section.classList.remove('collapse', 'show');
        djangoDumpDie.onTransitionEnd(section);
        section.style.height = '';
    },

    /**
     * Open or close every section inside a toggle's section, at once.
     * "Always show" sections stay open, with no arrow.
     */
    setDescendantsOpen(toggle, open) {
        const section = djangoDumpDie.getSection(toggle);
        if (!section) {
            return;
        }
        section.querySelectorAll('.arrow-toggle').forEach((child) => {
            if (djangoDumpDie.isCollapsible(child)) {
                djangoDumpDie.setOpen(child, open);
            } else {
                const childSection = djangoDumpDie.getSection(child);
                if (childSection) {
                    childSection.classList.add('collapse', 'show');
                }
                const arrow = child.querySelector(':scope > .arrow');
                if (arrow) {
                    arrow.textContent = '';
                }
            }
        });
    },

    /**
     * Handle clicks on toggles. CTRL+click also opens or closes everything inside.
     */
    onToggleClick(event) {
        const toggle = event.target.closest('.arrow-toggle');
        if (!toggle) {
            return;
        }
        const section = djangoDumpDie.getSection(toggle);
        if (!section) {
            return;
        }
        const open = !djangoDumpDie.isOpen(section);

        if (event.ctrlKey) {
            djangoDumpDie.setDescendantsOpen(toggle, open);
        }
        if (djangoDumpDie.isCollapsible(toggle)) {
            if (open) {
                djangoDumpDie.show(toggle);
            } else {
                djangoDumpDie.hide(toggle);
            }
        }
    },

    /**
     * Set up hover highlighting of uniques that appear more than once.
     *
     * A "Unique" refers to an instance of a unique variable.
     * If two or more variables point to the same memory instance of a value/object,
     * then they are listed as a single "Unique".
     * Hovering over one swaps the text and background colors of all of them.
     * TODO: Consider making the highlight scoped per dump call.
     * Right now looks through for whole page, so if a var is dumped twice,
     * or even appears twice via another dumped object it will highlight.
     */
    setUpUniqueDupHighlighting() {
        // Group the unique elements by their value, in one pass.
        const groups = new Map();
        document.querySelectorAll('.unique').forEach((element) => {
            const key = element.dataset.highlightUnique;
            if (!groups.has(key)) {
                groups.set(key, []);
            }
            groups.get(key).push(element);
        });
        // Only uniques that appear more than once are highlighted.
        groups.forEach((elements, key) => {
            if (elements.length < 2) {
                groups.delete(key);
            }
        });
        djangoDumpDie.duplicateGroups = groups;
        if (groups.size === 0) {
            return;
        }

        const getGroup = (target) => {
            const unique = target instanceof Element ? target.closest('.unique') : null;
            return unique ? groups.get(unique.dataset.highlightUnique) : undefined;
        };

        document.addEventListener('mouseover', (event) => {
            const group = getGroup(event.target);
            if (!group || group === getGroup(event.relatedTarget)) {
                return;
            }
            // Swap colors, as computed before highlighting.
            const foreground = getComputedStyle(group[0]).color;
            const background = getComputedStyle(document.body).backgroundColor;
            group.forEach((element) => {
                element.style.color = background;
                element.style.backgroundColor = foreground;
            });
        });
        document.addEventListener('mouseout', (event) => {
            const group = getGroup(event.target);
            if (!group || group === getGroup(event.relatedTarget)) {
                return;
            }
            // Restore colors.
            group.forEach((element) => {
                element.style.color = '';
                element.style.backgroundColor = '';
            });
        });
    },

    /**
     * Toggles that a toolbar button applies to.
     */
    getToggles(filter) {
        return Array.from(document.querySelectorAll('.arrow-toggle')).filter(filter || (() => true));
    },

    /**
     * Open or close toggles at one depth level, and the "Attribute" and "Function" sections directly inside them.
     */
    setLevelOpen(depth, open) {
        djangoDumpDie.getToggles((toggle) => toggle.dataset.objectDepth === String(depth)).forEach((toggle) => {
            djangoDumpDie.setOpen(toggle, open);
            const section = djangoDumpDie.getSection(toggle);
            if (section) {
                section.querySelectorAll(':scope > .attribute-list > .arrow-toggle').forEach((child) => {
                    djangoDumpDie.setOpen(child, open);
                });
            }
        });
    },

    /**
     * Open or close all toggles of one type ("type", "attr", "result", or "func"), or all toggles.
     */
    setTypeOpen(type, open) {
        const filter = type ? (toggle) => toggle.dataset.ddType === type : null;
        djangoDumpDie.getToggles(filter).forEach((toggle) => djangoDumpDie.setOpen(toggle, open));
    },

    /**
     * Functions to expand various groupings of collapsable elements.
     */
    expandAllElements() {
        djangoDumpDie.setTypeOpen(null, true);
    },
    expandAllTypes() {
        djangoDumpDie.setTypeOpen('type', true);
    },
    expandAllAttributes() {
        djangoDumpDie.setTypeOpen('attr', true);
    },
    expandAllFunctionResults() {
        djangoDumpDie.setTypeOpen('result', true);
    },
    expandAllFunctions() {
        djangoDumpDie.setTypeOpen('func', true);
    },
    expandFirstLevel() {
        djangoDumpDie.setLevelOpen(1, true);
    },
    expandSecondLevel() {
        djangoDumpDie.setLevelOpen(2, true);
    },

    /**
     * Functions to collapse various groupings of collapsable elements.
     */
    collapseAllElements() {
        djangoDumpDie.setTypeOpen(null, false);
    },
    collapseAllTypes() {
        djangoDumpDie.setTypeOpen('type', false);
    },
    collapseAllAttributes() {
        djangoDumpDie.setTypeOpen('attr', false);
    },
    collapseAllFunctionResults() {
        djangoDumpDie.setTypeOpen('result', false);
    },
    collapseAllFunctions() {
        djangoDumpDie.setTypeOpen('func', false);
    },
    collapseFirstLevel() {
        djangoDumpDie.setLevelOpen(1, false);
    },
    collapseSecondLevel() {
        djangoDumpDie.setLevelOpen(2, false);
    },

    /**
     * Add handling for the utility toolbar's buttons.
     */
    setUpUtilityToolbar() {
        const buttons = {
            'expand-all': djangoDumpDie.expandAllElements,
            'expand-types': djangoDumpDie.expandAllTypes,
            'expand-attrs': djangoDumpDie.expandAllAttributes,
            'expand-results': djangoDumpDie.expandAllFunctionResults,
            'expand-funcs': djangoDumpDie.expandAllFunctions,
            'expand-1st-lvl': djangoDumpDie.expandFirstLevel,
            'expand-2nd-lvl': djangoDumpDie.expandSecondLevel,
            'collapse-all': djangoDumpDie.collapseAllElements,
            'collapse-types': djangoDumpDie.collapseAllTypes,
            'collapse-attrs': djangoDumpDie.collapseAllAttributes,
            'collapse-results': djangoDumpDie.collapseAllFunctionResults,
            'collapse-funcs': djangoDumpDie.collapseAllFunctions,
            'collapse-1st-lvl': djangoDumpDie.collapseFirstLevel,
            'collapse-2nd-lvl': djangoDumpDie.collapseSecondLevel,
        };
        Object.entries(buttons).forEach(([id, handler]) => {
            const button = document.querySelector('.dump-toolbar #' + id);
            if (button) {
                button.addEventListener('click', handler);
            }
        });
    },

    /**
     * Set up all handling. Runs once per page, even if the script is included more than once.
     */
    setUp() {
        if (djangoDumpDie.isSetUp) {
            return;
        }
        djangoDumpDie.isSetUp = true;
        document.addEventListener('click', djangoDumpDie.onToggleClick);
        djangoDumpDie.setUpUniqueDupHighlighting();
        djangoDumpDie.setUpUtilityToolbar();
    },
};

// Make the object available as window.djangoDumpDie, since a top-level const is not a window property.
window.djangoDumpDie = djangoDumpDie;

/**
 * Set up once the document is parsed.
 */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', djangoDumpDie.setUp);
} else {
    djangoDumpDie.setUp();
}
