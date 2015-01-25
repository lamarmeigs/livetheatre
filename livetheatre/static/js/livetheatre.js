$(document).ready(function() {
    /* Top nav search toggle */
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


    /* Add captions to in-body images */
    $("#main-content img[alt]").each(function() {
        caption_text = $(this).attr('alt');
        float_str = this.style.float;
        $(this)
            .wrap('<div class="captioned ' + float_str + '"></div>')
            .after('<div class="caption">' + caption_text + '</div>');
    });
});
