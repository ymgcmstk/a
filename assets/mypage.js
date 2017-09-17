$(function(){
    var targtd_length = $('.targtd').length;
    $(document).on('keydown', 'body', function(e) {
        var keycode = e.keyCode - 48;
        if (keycode < targtd_length + 1 && keycode > 0) {
            e.preventDefault();
            window.location.href = $('#td' + keycode.toString()).attr('href');
        }
    });
});
