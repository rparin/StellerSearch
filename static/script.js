$(document).ready(function () {
  $("#img-button").click(function () {
    $(".line").toggle(); // Toggle the visibility of the horizontal line
    $(".results-container").toggle(); // Toggle the visibility of results container
  });

  $("#results-list").on("click", "#info-icon", function () {
    ///citation: https://www.geeksforgeeks.org/jquery-parent-parents-with-examples/
    $(this).parent().next("p").toggle();
  });
});
