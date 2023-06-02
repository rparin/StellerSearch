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

  $(".page-button-container").css("display", "none");

  // https://stackoverflow.com/questions/979662/how-can-i-detect-pressing-enter-on-the-keyboard-using-jquery
  // On keyboard 'enter'
  $("#search").on("keypress", function (e) {
    if (e.which == 13) {
    }
  });

  // $("#form").on("submit", function (e) {
  //   var userQuery = $("#search").val();
  //   e.preventDefault();
  //   $.ajax({
  //     url: "http://127.0.0.1:5000/query/",
  //     method: "POST",
  //     success: function (data) {
  //       console.log(data);
  //       $("#search").val("");
  //       $("#result").html("Your results for " + userQuery + " are:");
  //       $(".page-button-container").css("display", "flex");
  //     },
  //   });
  // });

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
