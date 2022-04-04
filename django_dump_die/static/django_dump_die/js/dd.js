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
            arrow_element = $('#arrow-' + unique);
            $(arrow_element).html('▼');
        });
        // Update arrow on hide.
        $('.dd-wrapper').on('hide.bs.collapse', function(event) {
            unique = $(event.target).data('unique');
            arrow_element = $('#arrow-' + unique);
            $(arrow_element).html('▶');
        });

        // Update arrow on show attributes header.
        $('.dd-wrapper').on('show.bs.collapse', function(event) {
            unique = $(event.target).data('unique-attributes');
            arrow_element = $('#arrow-' + unique);
            $(arrow_element).html('▼');
        });
        // Update arrow on hide attributes header.
        $('.dd-wrapper').on('hide.bs.collapse', function(event) {
            unique = $(event.target).data('unique-attributes');
            arrow_element = $('#arrow-' + unique);
            $(arrow_element).html('▶');
        });

        // Update arrow on show functions header.
        $('.dd-wrapper').on('show.bs.collapse', function(event) {
            unique = $(event.target).data('unique-functions');
            arrow_element = $('#arrow-' + unique);
            $(arrow_element).html('▼');
        });
        // Update arrow on hide functions header.
        $('.dd-wrapper').on('hide.bs.collapse', function(event) {
            unique = $(event.target).data('unique-functions');
            arrow_element = $('#arrow-' + unique);
            $(arrow_element).html('▶');
        });
    }
}

/**
 * Code to be run when the document is fully loaded.
 */
$(document).ready(function() {

    // Set up the unique duplicate highlighting
    djangoDumpDie.setUpUniqueDupHighlighting();
    // Set up the CTRL click functionality
    djangoDumpDie.setUpCTRLClickFunctionality();
    // Set up the Arrow Updating
    djangoDumpDie.setUpArrowUpdating();

});
