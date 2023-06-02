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

  getSummaries();
  resizeUrl();
});

//Cite: https://www.geeksforgeeks.org/pass-javascript-variables-to-python-in-flask/
async function getSummaries() {
  const urls = document.querySelectorAll(".result-container h2 a");
  const summaries = document.querySelectorAll(".result-container p");

  for (let i = 0; i < summaries.length; i++) {
    $.ajax({
      url: "/summary",
      type: "POST",
      data: { data: urls[i].innerHTML },
      success: function (response) {
        summaries[i].innerHTML = response;
      },
      error: function (error) {
        console.log(error);
      },
    });
  }
}

// Cite: https://codepen.io/jsstrn/pen/mMMmZB
function resizeUrl() {
  const getFontSize = (textLength) => {
    if (textLength > 120) {
      return ".8em";
    }
    if (textLength > 90) {
      return "1em";
    }
    if (textLength > 50) {
      return "1.2em";
    }
  };

  const urls = document.querySelectorAll(".result-container h2");

  urls.forEach((url) => {
    url.style.fontSize = getFontSize(url.textContent.length);
  });
}
