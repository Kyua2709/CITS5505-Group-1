$(document).ready(async function () {
  let upload = UPLOAD;
  let comments_positive = COMMENTS_POSITIVE;
  let comments_negative = COMMENTS_NEGATIVE;

  if (upload.status === "Processing") {
    if (parent) {
      parent.postMessage({ type: "ready", info: "The dataset is still being processed, please try again later" }, "*");
    }
    return;
  } else if (upload.status !== "Completed") {
    if (parent) {
      parent.postMessage({ type: "ready", info: "There was an error when processing the dataset, please contact administrator for assistance" }, "*");
    }
    return;
  }

  /* Fill in word cloud */

  const blacklist = new Set("i|me|my|myself|we|us|our|ours|ourselves|you|your|yours|yourself|yourselves|he|him|his|himself|she|her|hers|herself|it|its|itself|they|them|their|theirs|themselves|what|which|who|whom|whose|this|that|these|those|am|is|are|was|were|be|been|being|have|has|had|having|do|does|did|doing|will|would|should|can|could|ought|cannot|a|an|the|and|but|if|or|because|as|until|while|of|at|by|for|with|about|against|between|into|through|during|before|after|above|below|to|from|up|upon|down|in|out|on|off|over|under|again|further|then|once|here|there|when|where|why|how|all|any|both|each|few|more|most|other|some|such|no|nor|not|only|own|same|so|than|too|very|say|says|said|shall".split("|"));

  const getWords = (content) =>
    (content.match(/\b[a-zA-Z']+\b/g) || [])
      .filter((word) => word.length > 1)
      .filter((word) => word.indexOf("'") < 0)
      .filter((word) => isNaN(word))
      .filter((word) => !blacklist.has(word.toLowerCase()));

  function displayWordCloud(comments, selector) {
    let wordCounts = new Map();
    for (let { content } of comments) {
      for (let word of getWords(content)) {
        wordCounts.set(word, (wordCounts.get(word) || 0) + 1);
      }
    }

    let data = Array.from(wordCounts, ([text, size]) => ({ text, size }))
      .sort((a, b) => b.size - a.size)
      .slice(0, 50); // top 50 words

    let container = $(selector);
    container.empty();

    if (!data.length) {
      container.addClass("bg-light");
      container.text("No Data");
      return;
    }

    container.removeClass("bg-light");
    let width = container.width();
    let height = container.height();
    const fill = d3.scale.category20();

    let max = data[0].size;
    data = data.map(function (d) {
      d.size = 10 + (d.size / max) * (height / 3);
      return d;
    });

    d3.layout
      .cloud()
      .size([width, height])
      .words(data)
      .padding(5)
      .fontSize((d) => d.size)
      .rotate(() => 0) // do not rotate words
      .on("end", function (words) {
        d3.select(selector)
          .append("svg")
          .attr("width", width)
          .attr("height", height)
          .append("g")
          .attr("transform", `translate(${width / 2},${height / 2})`)
          .selectAll("text")
          .data(words)
          .enter()
          .append("text")
          .style("font-size", (d) => `${d.size}px`)
          .style("fill", (d, i) => fill(i))
          .attr("text-anchor", "middle")
          .attr("transform", (d) => `translate(${d.x}, ${d.y}) rotate(${d.rotate})`)
          .text((d) => d.text);
      })
      .start();
  }

  displayWordCloud(comments_positive, "#words-positive");
  displayWordCloud(comments_negative, "#words-negative");

  /* Init comment list */

  const search = $("#comment-search");

  function switchPage(e) {
    e.preventDefault();
    const page = $(e.target).data("page");
    loadPage(page);
  }

  function loadPage(page) {
    let url = `${location.pathname}?partial=1&page=${page}&search=${search.val()}`;
    $.get(url, function (data) {
      const container = $("#comment-list-container");
      container.html(data);
      container.find("a.page-link").on("click", switchPage);
    });
  }

  // initial load
  loadPage(1);

  // Initiate search on ENTER
  search.on("keydown", function (e) {
    if (e.key === "Enter" || e.keyCode === 13) {
      loadPage(1);
    }
  });

  /* Ready! */

  if (parent) {
    parent.postMessage({ type: "ready", info: "" }, "*");

    const sendHeight = () => parent.postMessage({ type: "height", height: document.body.scrollHeight }, "*");
    sendHeight();

    window.addEventListener("resize", () => {
      if (!window.innerHeight) return;
      sendHeight();
    });

    new MutationObserver(sendHeight).observe(document.body, { childList: true, subtree: true });
  }

  // ====== 新增：加载全部评论函数 ======
  async function loadAllComments() {
    return new Promise((resolve, reject) => {
      $.get(`${location.pathname}?partial=1&all_comments=1&search=`, function (data) {
        resolve(data);
      }).fail(() => reject("Failed to load all comments"));
    });
  }

  // ========== Export PDF ========== //
  document.getElementById("export-pdf")?.addEventListener("click", async function () {
    const container = $("#comment-list-container");

    // Hide search input box and search icon
    $("#comment-search").hide();
    $(".input-group-text").hide();

    // Backup current comments content
    const backupComments = container.html();

    try {
      // Load all comments (without pagination)
      const allCommentsHtml = await loadAllComments();
      container.html(allCommentsHtml);

      // Delay to let DOM render
      setTimeout(() => {
        const element = document.body;
        const opt = {
          margin: 0.5,
          filename: `${upload?.title || "analysis_result"}.pdf`,
          image: { type: "jpeg", quality: 0.98 },
          html2canvas: { scale: 2 },
          jsPDF: { unit: "in", format: "a4", orientation: "portrait" },
        };

        html2pdf()
          .set(opt)
          .from(element)
          .save()
          .then(() => {
            // Restore original content and search box
            container.html(backupComments);
            $("#comment-search").show();
            $(".input-group-text").show();

            // Rebind pagination events
            container.find("a.page-link").on("click", switchPage);
          });
      }, 300);
    } catch (error) {
      alert("Failed to load all comments when exporting. Please try again later.");
      // Restore search box display
      $("#comment-search").show();
      $(".input-group-text").show();
    }
  });
});
