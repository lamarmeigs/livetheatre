$(document).ready(function() {
    // top nav search toggle
    $("#search-toggle").click(function(e) {
        e.preventDefault();
        span = $(this).children('span').first()
        span.toggleClass('glyphicon-search');
        span.toggleClass('glyphicon-remove');

        if ($("#search-form").is(":visible")) {
            $('#search-form').removeAttr('style');
            $('#navbar .navbar-right li').not($(this).parents('li')).show();
        } else {
            $('#search-form').attr('style','display: block !important');
            $('#navbar .navbar-right li').not($(this).parents('li')).hide();
        }
    });
});
