$(document).ready(function () {
  $(window).keydown(function (event) {
    if (event.keyCode == 13) {
      event.preventDefault();
      return false;
    }
  });
});
const checkJpeg = (input) => {
  var file = input.files[0];
  if (file.type != "image/jpeg") {
    alert("Only jpg files are allowed");
    input.value = "";
  }
};

const checkPdf = (input) => {
  var file = input.files[0];
  if (file.type != "application/pdf") {
    alert("Only PDF files are allowed");
    input.value = "";
  }
};

const deleteDoc = (doc_type, is_prof = false) => {
  if (doc_type != "pic" && doc_type != "cv" && doc_type != "transcript") return;
  const url = is_prof ? "/delete-prof-doc" : "/delete-student-doc";
  $.ajax({
    url: url,
    method: "POST",
    data: {
      type: doc_type,
      csrfmiddlewaretoken: document.getElementsByName("csrfmiddlewaretoken")[0]
        .value,
    },
    success: (r) => {
      console.log(r);
      // TODO add some loading screen in these.
      setTimeout(() => {
        location.reload();
      }, 1000);
    },
    error: (e) => {
      // TODO error handling
      console.error(e);
    },
  });
};

$(function () {
  $("#profile-form").submit(function (event) {
    $("#loader").fadeIn(100);
    $.ajax({
      method: $(this).attr("method"),
      url: $(this).attr("action"),
      data: new FormData($("form")[0]),

      cache: false,
      contentType: false,
      processData: false,

      headers: {
        "X-CSRFTOKEN": document.getElementsByName("csrfmiddlewaretoken")[0]
          .value,
      },
      success: (r) => {
        console.log(r);
        // TODO add some loading screen in these.
        setTimeout(() => {
          location.reload();
        }, 1000);
      },
      error: (e) => {
        console.error(e);
        $("#loader").fadeOut(100);
      },
    });

    return false;
  });
});
