$(document).ready(function () {
  let interval = undefined;

  function switchPage(e) {
    e.preventDefault();

    // Prevent automatic refresh
    // Technically not required, but we want to avoid consecutive calls to refreshUploadsList
    clearInterval(interval);

    let params = new URLSearchParams(window.location.search);
    const page = $(e.target).data("page");
    params.set("page", page);

    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, "", newUrl);

    // force auto refresh
    refreshUploadsList();

    // enable auto refresh again
    interval = setInterval(refreshUploadsList, 2500);
  }

  function refreshUploadsList() {
    let params = new URLSearchParams(window.location.search);
    let refreshedPage = params.get("page") || "1";
    let url = `/upload?partial=1&page=${refreshedPage}`;

    $.get(url, function (data) {
      // there is a chance that we have switched the page before a old page refresh is completed
      // we need to prevent this old page refresh from overriding new page
      let params = new URLSearchParams(window.location.search);
      let currentpage = params.get("page") || "1";
      if (refreshedPage != currentpage) return;

      const container = $("#upload-list-container");
      container.html(data);
      container.find("a.page-link").on("click", switchPage);
    });
  }

  // initial load
  refreshUploadsList();

  // The initial uploads list is rendered by the backend when the page loads.
  // This fetches partial updates at regular intervals to keep the list fresh.
  interval = setInterval(refreshUploadsList, 2500);

  // Upload manual form
  $("#manualEntryForm form").submit(function (e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const description = formData.get("description");
    if (!description) {
      formData.set("description", "Text Input");
    }

    $.ajax({
      type: "POST",
      url: "/upload/text",
      data: formData,
      contentType: false,
      processData: false,
      success: function () {
        const successModal = new bootstrap.Modal(document.getElementById("successModal"));
        successModal.show();
      },
      error: function (error) {
        const msg = error.responseJSON?.message || "Upload failed.";
        alert(msg);
      },
    });
  });

  // Upload file form
  $("#fileUploadForm form").submit(function (e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const description = formData.get("description");
    const file = formData.get("file");
    if (!description) {
      formData.set("description", `File: ${file.name}`);
    }

    $.ajax({
      url: "/upload/file",
      method: "POST",
      data: formData,
      contentType: false,
      processData: false,
      success: function () {
        const successModal = new bootstrap.Modal(document.getElementById("successModal"));
        successModal.show();
      },
      error: function (error) {
        const msg = error.responseJSON?.error || "Upload failed.";
        alert(msg);
      },
    });
  });

  // Upload url
  $("#urlEntryForm form").submit(function (e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const description = formData.get("description");
    const url = formData.get("url");
    if (!description) {
      formData.set("description", `URL: ${url}`);
    }

    $.ajax({
      type: "POST",
      url: "/upload/url",
      data: formData,
      contentType: false,
      processData: false,
      success: function () {
        const successModal = new bootstrap.Modal(document.getElementById("successModal"));
        successModal.show();
      },
      error: function (error) {
        const msg = error.responseJSON?.message || "Upload failed.";
        alert(msg);
      },
    });
  });
});
