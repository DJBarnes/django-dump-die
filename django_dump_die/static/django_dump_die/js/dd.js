const djangoDumpDie = {

    /**
     * Set up the ability to have duplicated unique identifiers highlight on hover.
     *
     * A "Unique" refers to an instance of a unique variable.
     * If two or more variables point to the same memory instance of a value/object,
     * then they are listed as a single "Unique".
     * TODO: Consider making the highlight scoped per dump call.
     * Right now looks through for whole page, so if a var is dumped twice,
     * or even appears twice via another dumped object it will highlight.
     */
    setUpUniqueDupHighlighting: () => {
        // Var for all uniques.
        let allUniques = [];
        // Get all uniques from page via jQuery.
        const allUniquesJQ = $('.unique');
        // Convert JQ uniques to array of unique text.
        allUniquesJQ.each(function(index) {
            allUniques.push($(this).data('highlight-unique'));
        });

        // Function to find duplicates inside our dataset.
        const toFindDuplicates = arry => arry.filter((item, index) => arry.indexOf(item) !== index);

        // Find the duplicates and save to separate array.
        const dupUniques = toFindDuplicates(allUniques);

        // Iterate through all Uniques found.
        allUniquesJQ.each(function(index) {

            // Check if Unique has one or more instances.
            // If so, set a class identifier on all matching elements which match said Unique.
            if (dupUniques.includes($(this).data('highlight-unique'))) {

                // Create the css class to identify Unique group.
                var cssClass = 'duplicate-' + $(this).data('highlight-unique');

                // Add the css class to the element.
                $(this).addClass(cssClass);

                // Append a period to the cssClass for jQuery.
                cssClass = '.'+cssClass;

                // Get original foreground and background color.
                var origForegroundColor = $(cssClass).css('color');
                var origBackgroundColor = $('body').css('background-color');

                // On ALL elements with the class, on hover, swap the colors.
                $(cssClass).hover(function() {
                    // Swap colors.
                    $(cssClass).css('color', origBackgroundColor);
                    $(cssClass).css('background-color', origForegroundColor);
                }, function() {
                    // onMouseOut restore colors.
                    $(cssClass).css('color', "");
                    $(cssClass).css('background-color', "");
                });

            }

        });
    },


    /**
     * Set up the ability to hold the CTRL key while clicking on an expandable
     * element and have it auto expand all child elements that can also be
     * expanded.
     */
    setUpCTRLClickFunctionality: () => {
        // Set up click listener on an arrow-toggle
        $('.arrow-toggle').click(function(event) {

            // Check if CTRL key was pressed.
            if (event.ctrlKey) {
                // Get the sibling dd-wrapper or li-wrapper for the clicked anchor tag.
                // This is the div that will be expanded via the click and bootstrap.
                let target = $(event.currentTarget).data('target')
                let selector = target + '.dd-wrapper, ' + target + '.li-wrapper';
                let siblingDDWrapper = $(event.currentTarget).siblings(selector);

                // Get all dd-wrapper and li-wrapper child divs that need to be updated.
                childDivs = $(siblingDDWrapper).find('.dd-wrapper, .li-wrapper');
                // Get all arrows that should also be updated.
                childArrows = $(siblingDDWrapper).find('.arrow');

                // If the dd-wrapper or li-wrapper has the class show, we want
                // to remove the show class from all other dd-wrappers as this
                // one is about to loose that class from the bootstrap event.
                // NOTE: Could be race condition on whether this is right order.
                if ($(siblingDDWrapper).hasClass('show')) {
                    // Remove the show class.
                    childDivs.removeClass('show');
                    // Change the arrow to the closed state.
                    childArrows.html('▶');

                // Else, need to add show class to all elements.
                } else {
                    // Add the show class.
                    childDivs.addClass('show');
                    // Change the arrow to the open state.
                    childArrows.html('▼');
                }

                // Handle if any child elements have value of "always-show".
                let alwaysShowArrows = $(siblingDDWrapper).find('.always-show .arrow');
                $(alwaysShowArrows).each(function() {
                    let parent = $(this).parent();
                    let parentDivs = $(parent).siblings('.dd-wrapper, .li-wrapper');
                    let parentArrows = $(parent).children('.arrow');

                    // Ensure is always shown.
                    if (! $(parentDivs).hasClass('show')) {
                        $(parentDivs).addClass('show');
                    }
                    // Ensure arrows are always hidden.
                    $(parentArrows).html('');
                });

            }

        });
    },

    /**
     * Hook into the events raised by Bootstrap when the collapse functionality
     * is triggered to also update the arrow so that it is displayed correctly.
     */
    setUpArrowUpdating: () => {
        // Update arrow on show.
        $('.dd-wrapper').on('show.bs.collapse', function(event) {
            unique = $(event.target).data('unique');
            arrow_element = $('.arrow-' + unique);
            $(arrow_element).html('▼');
        });
        // Update arrow on hide.
        $('.dd-wrapper').on('hide.bs.collapse', function(event) {
            unique = $(event.target).data('unique');
            arrow_element = $('.arrow-' + unique);
            $(arrow_element).html('▶');
        });

        // Update arrow on show attributes header.
        $('.dd-wrapper').on('show.bs.collapse', function(event) {
            if (! $(event.target).hasClass('always-show') ) {
                unique = $(event.target).data('unique-attributes');
                arrow_element = $('.arrow-' + unique);
                $(arrow_element).html('▼');
            }
        });
        // Update arrow on hide attributes header.
        $('.dd-wrapper').on('hide.bs.collapse', function(event) {
            if (! $(event.target).hasClass('always-show') ) {
                unique = $(event.target).data('unique-attributes');
                arrow_element = $('.arrow-' + unique);
                $(arrow_element).html('▶');
            }
        });

        // Update arrow on show functions header.
        $('.dd-wrapper').on('show.bs.collapse', function(event) {
            if (! $(event.target).hasClass('always-show') ) {
                unique = $(event.target).data('unique-functions');
                arrow_element = $('#arrow-' + unique);
                $(arrow_element).html('▼');
            }
        });
        // Update arrow on hide functions header.
        $('.dd-wrapper').on('hide.bs.collapse', function(event) {
            if (! $(event.target).hasClass('always-show') ) {
                unique = $(event.target).data('unique-functions');
                arrow_element = $('#arrow-' + unique);
                $(arrow_element).html('▶');
            }
        });
    },

    /**
     * Add handling for UtilityToolbar logic, such as button click events, etc.
     */
    setUpUtilityToolbar() {

        // Set up expand/collapse button handling.
        $('.dump-toolbar #expand-all').on('click', djangoDumpDie.expandAllElements);
        $('.dump-toolbar #expand-types').on('click', djangoDumpDie.expandAllTypes);
        $('.dump-toolbar #expand-attrs').on('click', djangoDumpDie.expandAllAttributes);
        $('.dump-toolbar #expand-funcs').on('click', djangoDumpDie.expandAllFunctions);
        $('.dump-toolbar #expand-1st-lvl').on('click', djangoDumpDie.expandFirstLevel);
        $('.dump-toolbar #expand-2nd-lvl').on('click', djangoDumpDie.expandSecondLevel);
        $('.dump-toolbar #collapse-all').on('click', djangoDumpDie.collapseAllElements);
        $('.dump-toolbar #collapse-types').on('click', djangoDumpDie.collapseAllTypes);
        $('.dump-toolbar #collapse-attrs').on('click', djangoDumpDie.collapseAllAttributes);
        $('.dump-toolbar #collapse-funcs').on('click', djangoDumpDie.collapseAllFunctions);
        $('.dump-toolbar #collapse-1st-lvl').on('click', djangoDumpDie.collapseFirstLevel);
        $('.dump-toolbar #collapse-2nd-lvl').on('click', djangoDumpDie.collapseSecondLevel);
    },

    /**
     * Functions to expand various groupings of collapsable elements.
     */
    expandAllElements() {
        console.log('Called expandAllElements().');

        // Find all expandable arrow elements and expand them.
        $('.arrow-toggle').each(function() {

            if ($(this).hasClass('collapsed') || $(this).hasClass('collapsing')) {
                $(this).click();
            }
        });
    },
    expandAllTypes() {
        console.log('Called expandAllTypes().');

        // Find all expandable arrow elements (with the "type" dataset) and expand them.
        $('.arrow-toggle').filter('[data-dd-type="type"]').each(function() {

            if ($(this).hasClass('collapsed') || $(this).hasClass('collapsing')) {
                $(this).click();
            }
        });

    },
    expandAllAttributes() {
        console.log('Called expandAllAttributes().');

        // Find all expandable arrow elements (with the "attr" dataset) and expand them.
        $('.arrow-toggle').filter('[data-dd-type="attr"]').each(function() {

            if ($(this).hasClass('collapsed') || $(this).hasClass('collapsing')) {
                $(this).click();
            }
        });
    },
    expandAllFunctions() {
        console.log('Called expandAllFunctions().');

        // Find all expandable arrow elements (with the "func" dataset) and expand them.
        $('.arrow-toggle').filter('[data-dd-type="func"]').each(function() {

            if ($(this).hasClass('collapsed') || $(this).hasClass('collapsing')) {
                $(this).click();
            }
        });
    },
    expandFirstLevel() {
        console.log('Called expandFirstLevel().');

        // Find all elements at depth level of 1 and expand them.
        $('.arrow-toggle').filter('[data-object-depth="1"]').each(function() {

            // Expand parent element at first level.
            if ($(this).hasClass('collapsed') || $(this).hasClass('collapsing')) {
                $(this).click();
            }

            // Expand direct "Attribute" and "Function" sections at this level,
            // for when both are enabled.
            let siblingDivs = $(this).siblings('.dd-wrapper, .li-wrapper');
            let siblingLists = $(siblingDivs).children('.attribute-list');
            $(siblingLists).each(function() {
                let siblingArrow = $(this).children('.arrow-toggle');
                if ($(siblingArrow).hasClass('collapsed') || $(siblingArrow).hasClass('collapsing')) {
                    $(siblingArrow).click();
                }
            });

        });
    },
    expandSecondLevel() {
        console.log('Called expandSecondLevel().');

        // Find all elements at depth level of 2 and expand them.
        $('.arrow-toggle').filter('[data-object-depth="2"]').each(function() {

            // Expand parent element at second level.
            if ($(this).hasClass('collapsed') || $(this).hasClass('collapsing')) {
                $(this).click();
            }

            // Expand direct "Attribute" and "Function" sections at this level,
            // for when both are enabled.
            let siblingDivs = $(this).siblings('.dd-wrapper, .li-wrapper');
            let siblingLists = $(siblingDivs).children('.attribute-list');
            $(siblingLists).each(function() {
                let siblingArrow = $(this).children('.arrow-toggle');
                if ($(siblingArrow).hasClass('collapsed') || $(siblingArrow).hasClass('collapsing')) {
                    $(siblingArrow).click();
                }
            });

        });
    },

    /**
     * Functions to collapse various groupings of collapsable elements.
     */
    collapseAllElements() {
        console.log('Called collapseAllElements().');

        // Find all expandable arrow elements and collapse them.
        $('.arrow-toggle').each(function() {

            if (! ($(this).hasClass('collapsed') || $(this).hasClass('collapsing'))) {
                $(this).click();
            }
        });
    },
    collapseAllTypes() {
        console.log('Called collapseAllTypes().');

        // Find all expandable arrow elements (with the "type" dataset) and collapse them.
        $('.arrow-toggle').filter('[data-dd-type="type"]').each(function() {

            if (! ($(this).hasClass('collapsed') || $(this).hasClass('collapsing'))) {
                $(this).click();
            }
        });
    },
    collapseAllAttributes() {
        console.log('Called collapseAllAttributes().');

        // Find all expandable arrow elements (with the "attr" dataset) and collapse them.
        $('.arrow-toggle').filter('[data-dd-type="attr"]').each(function() {

            if (! ($(this).hasClass('collapsed') || $(this).hasClass('collapsing'))) {
                $(this).click();
            }
        });
    },
    collapseAllFunctions() {
        console.log('Called collapseAllFunctions().');

        // Find all expandable arrow elements (with the "func" dataset) and collapse them.
        $('.arrow-toggle').filter('[data-dd-type="func"]').each(function() {

            if (! ($(this).hasClass('collapsed') || $(this).hasClass('collapsing'))) {
                $(this).click();
            }
        });
    },
    collapseFirstLevel() {
        console.log('Called collapseFirstLevel().');

        // Find all elements at depth level of 1 and collapse them.
        $('.arrow-toggle').filter('[data-object-depth="1"]').each(function() {

            // Expand parent element at first level.
            if (! ($(this).hasClass('collapsed') || $(this).hasClass('collapsing'))) {
                $(this).click();
            }

            // Collapse direct "Attribute" and "Function" sections at this level,
            // for when both are enabled.
            let siblingDivs = $(this).siblings('.dd-wrapper, .li-wrapper');
            let siblingLists = $(siblingDivs).children('.attribute-list');
            $(siblingLists).each(function() {
                let siblingArrow = $(this).children('.arrow-toggle');
                if (! ($(siblingArrow).hasClass('collapsed') || $(siblingArrow).hasClass('collapsing'))) {
                    $(siblingArrow).click();
                }
            });

        });
    },
    collapseSecondLevel() {
        console.log('Called collapseSecondLevel().');

        // Find all elements at depth level of 2 and collapse them.
        $('.arrow-toggle').filter('[data-object-depth="2"]').each(function() {

            // Expand parent element at second level.
            if (! ($(this).hasClass('collapsed') || $(this).hasClass('collapsing'))) {
                $(this).click();
            }

            // Collapse direct "Attribute" and "Function" sections at this level,
            // for when both are enabled.
            let siblingDivs = $(this).siblings('.dd-wrapper, .li-wrapper');
            let siblingLists = $(siblingDivs).children('.attribute-list');
            $(siblingLists).each(function() {
                let siblingArrow = $(this).children('.arrow-toggle');
                if (! ($(siblingArrow).hasClass('collapsed') || $(siblingArrow).hasClass('collapsing'))) {
                    $(siblingArrow).click();
                }
            });

        });
    }
}

/**
 * Code to be run when the document is fully loaded.
 */
$(document).ready(function() {

    // Set up the unique duplicate highlighting.
    djangoDumpDie.setUpUniqueDupHighlighting();
    // Set up the CTRL click functionality.
    djangoDumpDie.setUpCTRLClickFunctionality();
    // Set up the Arrow Updating.
    djangoDumpDie.setUpArrowUpdating();
    // Set up toolbar handling.
    djangoDumpDie.setUpUtilityToolbar();

});
