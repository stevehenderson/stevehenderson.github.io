// Self-contained client-side search over /search.json.
// No external services or dependencies — fits the site's no-tracking posture.
(function () {
  "use strict";

  var input = document.getElementById("search-input");
  var results = document.getElementById("search-results");
  var status = document.getElementById("search-status");
  if (!input || !results) return;

  var index = [];
  var ready = false;

  function escapeHTML(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // Build a short snippet centered on the first query hit.
  function snippet(text, query) {
    if (!text) return "";
    var lower = text.toLowerCase();
    var at = lower.indexOf(query);
    var start = at < 0 ? 0 : Math.max(0, at - 60);
    var slice = text.slice(start, start + 180);
    if (start > 0) slice = "…" + slice;
    if (start + 180 < text.length) slice = slice + "…";
    return escapeHTML(slice);
  }

  function score(item, terms) {
    var title = (item.title || "").toLowerCase();
    var tags = (item.tags || "").toLowerCase();
    var content = (item.content || "").toLowerCase();
    var total = 0;
    for (var i = 0; i < terms.length; i++) {
      var t = terms[i];
      if (!t) continue;
      var hit = 0;
      if (title.indexOf(t) !== -1) hit += 10;
      if (tags.indexOf(t) !== -1) hit += 5;
      if (content.indexOf(t) !== -1) hit += 1;
      if (hit === 0) return 0; // every term must appear somewhere (AND)
      total += hit;
    }
    return total;
  }

  function render(query) {
    var q = query.trim().toLowerCase();
    results.innerHTML = "";
    if (!q) {
      if (status) status.textContent = "";
      return;
    }
    if (!ready) {
      if (status) status.textContent = "Loading index…";
      return;
    }
    var terms = q.split(/\s+/);
    var matches = [];
    for (var i = 0; i < index.length; i++) {
      var s = score(index[i], terms);
      if (s > 0) matches.push({ item: index[i], score: s });
    }
    matches.sort(function (a, b) { return b.score - a.score; });

    if (status) {
      status.textContent = matches.length +
        (matches.length === 1 ? " result" : " results") + " for “" + query.trim() + "”";
    }

    var frag = document.createDocumentFragment();
    for (var j = 0; j < matches.length; j++) {
      var it = matches[j].item;
      var li = document.createElement("li");
      li.className = "search-result";
      var meta = it.date ? '<span class="search-result__meta">' + escapeHTML(it.date) + "</span>" : "";
      li.innerHTML =
        '<a class="search-result__title" href="' + escapeHTML(it.url) + '">' +
        escapeHTML(it.title) + "</a>" + meta +
        '<p class="search-result__snippet">' + snippet(it.content, terms[0]) + "</p>";
      frag.appendChild(li);
    }
    results.appendChild(frag);
  }

  function debounce(fn, ms) {
    var t;
    return function () {
      clearTimeout(t);
      t = setTimeout(fn, ms);
    };
  }

  input.addEventListener("input", debounce(function () { render(input.value); }, 120));

  // Allow deep links like /search/?q=jekyll (replaces the old CSE query param).
  function queryFromURL() {
    var m = /[?&]q=([^&]+)/.exec(window.location.search);
    return m ? decodeURIComponent(m[1].replace(/\+/g, " ")) : "";
  }

  var base = (document.currentScript && document.currentScript.dataset.index) || "/search.json";
  fetch(base)
    .then(function (r) { return r.json(); })
    .then(function (data) {
      index = data;
      ready = true;
      var initial = queryFromURL();
      if (initial) {
        input.value = initial;
        render(initial);
      } else if (input.value) {
        render(input.value);
      }
      input.focus();
    })
    .catch(function () {
      if (status) status.textContent = "Search index failed to load.";
    });
})();
