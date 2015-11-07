<!-- Script to insert character counts -->
<!-- Requres jQuery -->
$('textarea').on('input propertychange', function () {
    var ctrl = $(this),
        max_len = 250,
        len = $(ctrl).val().trim().length;
    var c = $(ctrl).parent().find('#char_count');
    len = max_len - len;
    c.text(len > 0 ? (len + ' character' + (len == 1 ? '' : 's') + ' remaining.') : '');
    $(ctrl).val($(ctrl).val().substring(0, max_len));
});
