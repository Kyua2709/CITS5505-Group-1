$(document).ready(function () {
  async function renderAnalysis(id) {
    let url = `/analyze/result/${id}`;
    let upload = await fetch(url).then((r) => r.json());

    let all_comments = upload.comments;
    let comments_positive = [];
    let comments_neutral = [];
    let comments_negative = [];

    for (let comment of all_comments) {
      // these thresholds are purely emperical
      if (comment.score < 37.5) {
        comments_negative.push(comment);
      } else if (comment.score < 50) {
        comments_neutral.push(comment);
      } else {
        comments_positive.push(comment);
      }
    }

    /* Fill in header */

    $("#upload-description").text(upload.description);

    /* Fill in statistics */

    const total = all_comments.length;
    $("#total-comments").text(total);

    const percentage = total ? (comments) => Math.round((100 * comments.length) / total) : () => 0;
    $("#percentage-positive").text(percentage(comments_positive));
    $("#percentage-neutral").text(percentage(comments_neutral));
    $("#percentage-negative").text(percentage(comments_negative));

    /* Fill in word cloud */

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
            //.style("font-family", "")
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
  }

  $("#upload-select").change(function (e) {
    let info = $("#info-pannel");
    let result = $("#analysis-result");

    const classes = "disabled h-0 overflow-hidden";
    info.html("Loading...");
    result.addClass(classes);

    renderAnalysis(e.target.value)
      .then(() => {
        info.empty();
        result.removeClass(classes);
      })
      .catch((e) => info.html(`Failed to load: ${e}`));
  });
});
