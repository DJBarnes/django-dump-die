$(document).ready(function() {
    // Add class to uniques that are duplicated for highlighting on hover
    // Var for all uniques
    var allUniques = [];
    // Get all uniques from page
    const allUniquesJQ = $('.unique');
    // Convert JQ uniques to array of unique text
    allUniquesJQ.each(function(index) {
        allUniques.push($(this).html());
    });
    // Function to find duplicates
    const toFindDuplicates = arry => arry.filter((item, index) => arry.indexOf(item) !== index);
    // Find the duplicates
    const dupUniques = toFindDuplicates(allUniques);
    // For each unique text
    allUniquesJQ.each(function(index) {
        // If a specific unique's html is in the duplicate array
        // NOTE: this will set the class on all elements that have
        // a unique that matches the unique from the element.
        if (dupUniques.includes($(this).html())) {
            // Create the css class to add
            var cssClass = 'duplicate-' + $(this).html();
            // Add the css class to the element
            $(this).addClass(cssClass);
            // Append a period to the cssClass for jQuery
            cssClass = '.'+cssClass;
            // Get original foreground and background color
            var origForegroundColor = $(cssClass).css('color');
            var origBackgroundColor = $('body').css('background-color');
            // On ALL elements with the class, on hover, swap the colors
            $(cssClass).hover(function() {
                // Swap colors
                $(cssClass).css('color', origBackgroundColor);
                $(cssClass).css('background-color', origForegroundColor);
            }, function() {
                // onMouseOut restore colors
                $(cssClass).css('color', "");
                $(cssClass).css('background-color', "");
            });
        }
    });

    // Update arrow on show
    $('.dd-wrapper').on('show.bs.collapse', function(event) {
        unique = $(event.target).data('unique');
        arrow_element = $('#arrow-' + unique);
        $(arrow_element).html('▼');
    });
    // Update arrow on hide
    $('.dd-wrapper').on('hide.bs.collapse', function(event) {
        unique = $(event.target).data('unique');
        arrow_element = $('#arrow-' + unique);
        $(arrow_element).html('▶');
    });
});
