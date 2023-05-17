document.addEventListener("DOMContentLoaded", function(){
    var qrcode = new QRCode(document.getElementById("qrcode"), {
        text: This_page_url,
        width: 200,
        height: 200,
        colorDark : "#000000",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
    });
});