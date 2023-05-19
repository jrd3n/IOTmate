document.addEventListener("DOMContentLoaded", function(){
    var qrcode = new QRCode(document.getElementById("qrcode"), {
        text: This_page_url,
        width: 150,
        height: 150,
        colorDark : "#000000",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
    });
});