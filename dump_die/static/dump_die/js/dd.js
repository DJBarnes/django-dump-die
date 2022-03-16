
$(document).ready(function() {

    /**
     * A "Unique" refers to an instance of a unique variable.
     * If two or more variables point to the same memory instance of a value/object,
     * then they are grouped as a single "Unique".
     */
    // Add class to uniques that are duplicated for highlighting on hover.
    // Var for all uniques.
    var allUniques = [];
    // Get all uniques from page.
    const allUniquesJQ = $('.unique');
    // Convert JQ uniques to array of unique text.
    allUniquesJQ.each(function(index) {
        allUniques.push($(this).html());
    });

    // Function to find duplicates inside our dataset.
    const toFindDuplicates = arry => arry.filter((item, index) => arry.indexOf(item) !== index);

    // Find the duplicates and save to separate array.
    const dupUniques = toFindDuplicates(allUniques);

    // Iterate through each Unique found.
    allUniquesJQ.each(function(index) {

        // Check if Unique has one or more instances.
        // If so, set a class identifier on all matching elements which match said Unique.
        if (dupUniques.includes($(this).html())) {
            // Create the css class to identify Unique group.
            var cssClass = 'duplicate-' + $(this).html();

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


    // Allow ability to CTRL click on an expandable element and have it auto
    // expand all children elements that can be expanded.
    $('.arrow-toggle').click(function(event) {

        // Check if CTRL key was pressed.
        if (event.ctrlKey) {
            // Get the sibling ddwrapper for the clicked anchor tag.
            var siblingDDWrapper = $(event.currentTarget).siblings('.dd-wrapper, .li-wrapper');

            // If the ddwrapper has the class show, we want to remove the show class from all other
            // ddwrappers as this one is about to loose that class from the bootstrap event.
            // NOTE: Could be race condition on whether this is right order.
            if ($(siblingDDWrapper).hasClass('show')) {
                childDivs = $(siblingDDWrapper).find('.dd-wrapper, .li-wrapper');
                childDivs.removeClass('show');

                childArrows = $(siblingDDWrapper).find('.arrow');
                childArrows.html('▶');
            // Else, need to add show class to all elements.
            } else {
                childDivs = $(siblingDDWrapper).find('.dd-wrapper, .li-wrapper');
                childDivs.addClass('show');

                childArrows = $(siblingDDWrapper).find('.arrow');
                childArrows.html('▼');
            }
        }

    });


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
    // Update arrow on hide.
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
    // Update arrow on hide.
    $('.dd-wrapper').on('hide.bs.collapse', function(event) {
        unique = $(event.target).data('unique-functions');
        arrow_element = $('#arrow-' + unique);
        $(arrow_element).html('▶');
    });
});
