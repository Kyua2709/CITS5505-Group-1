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

  // Create sentiment intensity histogram
  const ctxHistogram = document.getElementById("intensityHistogram").getContext("2d");

  new Chart(ctxHistogram, {
    type: "bar",
    data: {
      labels: HISTOGRAM_DATA.labels,
      datasets: [
        {
          label: "Positive",
          data: HISTOGRAM_DATA.positive,
          backgroundColor: "rgba(0, 128, 0, 0.5)",
          stack: "sentiment"
        },
        {
          label: "Neutral",
          data: HISTOGRAM_DATA.neutral,
          backgroundColor: "rgba(255, 165, 0, 0.5)",
          stack: "sentiment"
        },
        {
          label: "Negative",
          data: HISTOGRAM_DATA.negative,
          backgroundColor: "rgba(255, 0, 0, 0.5)",
          stack: "sentiment"
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "top" },
        title: {
          display: true,
          text: "Emotion Intensity Distribution by Sentiment"
        },
        tooltip: {
          callbacks: {
            afterBody: function (tooltipItems) {
              const item = tooltipItems[0];
              const label = item.label;
              const sentiment = item.dataset.label.toLowerCase();
              const examples = HISTOGRAM_DATA.samples[label]?.[sentiment] || [];
              return examples.length
                ? [`e.g.: ${examples.slice(0, 2).join(" / ")}`]
                : [];
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          stacked: true
        },
        x: {
          stacked: true
        }
      }
    }
  });

  // Sentiment distribution pie chart
  const ctxDist = document.getElementById('distributionChart').getContext('2d');
  new Chart(ctxDist, {
    type: 'pie',
    data: {
      labels: ['Positive', 'Neutral', 'Negative'],
      datasets: [{
        data: [
          DISTRIBUTION_DATA.positive,
          DISTRIBUTION_DATA.neutral,
          DISTRIBUTION_DATA.negative
        ],
        backgroundColor: ['green', 'orange', 'red'],
        hoverOffset: 10
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' },
        title: { display: true, text: 'Sentiment Distribution' }
      }
    }
  });

  /* ===========================
  Word Clouds
  ============================ */
  const blacklist = new Set(`i|me|my|myself|we|us|our|ours|ourselves|you|your|yours|yourself|yourselves|he|him|his|himself|she|her|hers|herself|it|its|itself|they|them|their|theirs|themselves|what|which|who|whom|whose|this|that|these|those|am|is|are|was|were|be|been|being|have|has|had|having|do|does|did|doing|will|would|should|can|could|ought|cannot|a|an|the|and|but|if|or|because|as|until|while|of|at|by|for|with|about|against|between|into|through|during|before|after|above|below|to|from|up|upon|down|in|out|on|off|over|under|again|further|then|once|here|there|when|where|why|how|all|any|both|each|few|more|most|other|some|such|no|nor|not|only|own|same|so|than|too|very|say|says|said|shall`.split("|"));
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
      .slice(0, 50);

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
      .rotate(() => 0)
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

  // ===========================
  // Comment List & Search
  // ===========================
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

  loadPage(1);
  search.on("keydown", function (e) {
    if (e.key === "Enter" || e.keyCode === 13) {
      loadPage(1);
    }
  });

  // ===========================
  // Resize & Ready for iframe
  // ===========================
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

  // ========== Export PDF ========== //

  async function loadAllComments() {
    return new Promise((resolve, reject) => {
      $.get(`${location.pathname}?partial=1&per_page=-1`, function (data) {
        resolve(data);
      }).fail(() => reject("Failed to load all comments"));
    });
  }

  function getDPI() {
    const div = document.createElement("div");
    div.style.width = "1in";
    div.style.height = "1in";
    div.style.position = "absolute";
    div.style.top = "-100%";
    document.body.appendChild(div);
    const dpi = div.offsetWidth;
    document.body.removeChild(div);
    return dpi;
  }

  // Check if the user is the owner of the upload
  if (!IS_OWNER) {
    $('#export-pdf').hide();
  }

  $("#export-pdf").on("click", async function () {
    const hideOnExport = $("#action-buttons, #comment-list-for-view");
    const showOnExport = $("#comment-list-for-export");

    try {
      // Load all comments (without pagination)
      const allCommentsHtml = await loadAllComments();
      showOnExport.html(allCommentsHtml);

      // Hide and show elements
      hideOnExport.addClass("d-none");
      showOnExport.removeClass("d-none");

      // Delay to allow DOM rendering
      await new Promise(requestAnimationFrame);

      const element = document.body;
      const dpi = getDPI();
      const pxToInch = (px) => px / dpi;

      // Calculate horizontal margins
      const pageWidthInInch = pxToInch(element.offsetWidth);
      const contentWidthInInch = pxToInch(showOnExport.width());
      const margin = (pageWidthInInch - contentWidthInInch) / 2;

      // Use the same margin value for vertical handling
      const pageHeightInInch = Math.ceil(pxToInch(element.offsetHeight) + 2 * margin);

      await html2pdf()
        .set({
          margin: [margin, 0, 0, 0],
          filename: `${upload.title || "analysis_result"}.pdf`,
          image: { type: "jpeg", quality: 0.98 },
          html2canvas: { scale: 4 },
          jsPDF: {
            unit: "in",
            format: [pageWidthInInch, pageHeightInInch], // WYSIWYG
          },
        })
        .from(element)
        .save();
    } catch (error) {
      alert("Failed to load all comments when exporting. Please try again later.");
    }

    hideOnExport.removeClass("d-none");
    showOnExport.addClass("d-none");
    window.dispatchEvent(new Event("resize")); // Force refresh of iframe height
  });

  // Check URL parameters, automatically export PDF if needed
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('export_pdf') === 'true') {
    // Add a small delay to ensure page is fully rendered
    setTimeout(function () {
      $("#export-pdf").click();
    }, 1000);
  }
});