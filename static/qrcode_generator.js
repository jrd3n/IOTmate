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

// Check if the user is on a mobile device
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  }

// Get the element you want to hide
var nonMobileElement = document.getElementById('qrcode');

// Hide the element if the user is on a mobile device
if (isMobileDevice()) {
  nonMobileElement.style.display = 'none';
} else {
  nonMobileElement.style.display = 'block';
}