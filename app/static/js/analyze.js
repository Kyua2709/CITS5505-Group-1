$(document).ready(function () {
  const select = document.getElementById("upload-select");
  const iframe = document.getElementById("analyze-result-iframe");
  const info = document.getElementById("analyze-result-info");

  // Update iframe height as reported by iframe
  const handlers = { height: (data) => (iframe.style.height = data.height + "px") };

  // Global event handler for iframe messages
  window.addEventListener("message", ({ source, data }) => {
    if (source !== iframe.contentWindow || !data) return;
    handlers[data.type](data);
  });

  select.onchange = async function onchange() {
    // Disable select to prevent re-enter
    select.setAttribute("disabled", "");

    // Show loading info
    info.textContent = "Loading...";

    // Set location state
    let params = new URLSearchParams(window.location.search);
    let upload_id = select.value;
    params.set("upload_id", upload_id);
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, "", newUrl);

    // Unload previous iframe
    iframe.src = "about:blank";
    iframe.style.height = "0";

    // wait for iframe ready
    let promise = new Promise((resolve) => (handlers["ready"] = resolve));
    iframe.src = `/analyze/result/${upload_id}`;
    let data = await promise;

    // Set loading info
    // if data.info is empty, then the text will be hidden
    info.textContent = data.info;

    // Enable select again
    select.removeAttribute("disabled");
  };

  // if has initially selected dataset, load
  {
    let params = new URLSearchParams(window.location.search);
    let upload_id = params.get("upload_id");
    const optionExists = Array.from(select.options).some((option) => option.value === upload_id);
    if (optionExists) {
      select.value = upload_id;
      select.onchange();
    }
  }
});
