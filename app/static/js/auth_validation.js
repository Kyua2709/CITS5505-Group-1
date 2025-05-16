$(document).ready(function () {
  function setLoading($button, isLoading) {
    if (isLoading) {
      $button.prop("disabled", true);
      $button.html(
        `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...`,
      );
    } else {
      $button.prop("disabled", false);
      $button.html($button.data("original-text"));
    }
  }

  // LOGIN
  $("#loginModal form").submit(function (e) {
    e.preventDefault();
    const $form = $(this);
    const $errorBox = $("#loginError");
    const $button = $form.find('button[type="submit"]');

    $errorBox.hide().empty();
    $button.data("original-text", $button.html());
    setLoading($button, true);

    $.ajax({
      type: "POST",
      url: "/login",
      data: $form.serialize(),
      success: function (response) {
        window.location.reload();
      },
      error: function (error) {
        const msg = error.responseJSON?.message || "Login failed.";
        $errorBox.html(`<div class="alert alert-danger">${msg}</div>`).show();
        setLoading($button, false);
      },
    });
  });

  // REGISTER
  $("#registerModal form").submit(function (e) {
    e.preventDefault();
    const $form = $(this);
    const $errorBox = $("#registerError");
    const $button = $form.find('button[type="submit"]');

    $errorBox.hide().empty();
    $button.data("original-text", $button.html());
    setLoading($button, true);

    $.ajax({
      type: "POST",
      url: "/register",
      data: $form.serialize(),
      success: function (response) {
        $errorBox.html(`<div class="alert alert-success">${response.message}</div>`).show();
        setTimeout(function () {
          window.location.reload();
        }, 1000);
      },
      error: function (error) {
        const msg = error.responseJSON?.message || "Registration failed.";
        $errorBox.html(`<div class="alert alert-danger">${msg}</div>`).show();
        setLoading($button, false);
      },
    });
  });
});
