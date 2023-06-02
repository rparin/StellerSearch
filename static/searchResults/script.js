$(document).ready(function () {
  /// Cite: https://web-design-weekly.com/change-font-size-within-input-field-based-on-length/
  $("#search").keypress(function () {
    var textLength = $(this).val().length;

    if (textLength < 20) {
      $(this).css("font-size", "2em");
    } else if (textLength < 40) {
      $(this).css("font-size", "1.5em");
    } else if (textLength > 40) {
      $(this).css("font-size", "1em");
    }
  });

  resizeUrl();
});

// Cite: https://codepen.io/jsstrn/pen/mMMmZB
function resizeUrl() {
  const getFontSize = (textLength) => {
    if (textLength > 90) {
      return ".7em";
    }
    if (textLength > 50) {
      console.log(textLength);
      return "1.2em";
    }
  };

  const urls = document.querySelectorAll(".result-container h2");

  urls.forEach((url) => {
    url.style.fontSize = getFontSize(url.textContent.length);
  });
}
