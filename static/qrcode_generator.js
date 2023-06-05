// document.addEventListener("DOMContentLoaded", function() {
//   var qrcode = new QRCode(document.getElementById("qrcode"), {
//     text: "This_page_url",
//     colorDark: "#000000",
//     colorLight: "#ffffff",
//     correctLevel: QRCode.CorrectLevel.H
//   });
// });

document.addEventListener("DOMContentLoaded", function(){
  var style = document.createElement("style");
  style.textContent = "#qrcode img, #qrcode canvas { width: 100%; height: 100%; }";
  //style.textContent = "#qrcode { display: flex; justify-content: center; align-items: center; } #qrcode img, #qrcode canvas { width: 100%; height: 100%; }";
  document.head.appendChild(style);

  var qrcode = new QRCode(document.getElementById("qrcode"), {
      text: This_page_url,
      colorDark: "#000000",
      colorLight: "#ffffff",
      correctLevel: QRCode.CorrectLevel.H
  });
});


// // Check if the user is on a mobile device
// function isMobileDevice() {
//     return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
// }

// // Get the element you want to hide
// var nonMobileElement = document.getElementById('qrcode');

// // Hide the element if the user is on a mobile device
// if (isMobileDevice()) {
//   nonMobileElement.style.display = 'none';
// } else {
//   nonMobileElement.style.display = 'block';
// }