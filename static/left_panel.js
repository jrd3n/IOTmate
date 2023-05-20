$(document).ready(function () {
    $(".file-link").hover(function (e) {
        var imgSrc = $(this).data('img-src');
        if (imgSrc) {
            $("#preview-img").attr('src', imgSrc);
            $("#image-preview").css({ top: e.pageY + 50, left: e.pageX }).fadeIn();
        }
    }, function () {
        $("#image-preview").fadeOut();
    });
});