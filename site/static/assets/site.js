// Learn Vulgultra: colour mode, sidebar, small-screen drawer, table of
// contents highlight and search. Every page works without this file; it
// only adds the interactive parts.
(function () {
  "use strict";

  var root = document.documentElement;
  var labels = JSON.parse(document.getElementById("site-labels").textContent);

  function stored(key, value) {
    // Browser storage can be missing or blocked; the site must not depend on it.
    try {
      if (value === undefined) return localStorage.getItem(key);
      localStorage.setItem(key, value);
    } catch (error) { /* ignore */ }
    return null;
  }

  function element(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  // ---- Colour mode -------------------------------------------------------

  var themeToggle = document.querySelector(".theme-toggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      stored("theme", next);
    });
  }

  // ---- Language menu (hover opens it; a tap needs a click) ----------------

  var dropdown = document.querySelector(".dropdown");
  if (dropdown) {
    var dropdownToggle = dropdown.querySelector(".dropdown-toggle");
    dropdownToggle.addEventListener("click", function () {
      dropdownToggle.setAttribute("aria-expanded", String(dropdown.classList.toggle("open")));
    });
    document.addEventListener("click", function (event) {
      if (!dropdown.contains(event.target)) dropdown.classList.remove("open");
    });
  }

  // ---- Sidebar ------------------------------------------------------------

  function wireCarets(scope) {
    scope.querySelectorAll(".menu-caret").forEach(function (caret) {
      caret.addEventListener("click", function () {
        var open = caret.closest(".menu-category").classList.toggle("open");
        caret.setAttribute("aria-expanded", String(open));
      });
    });
  }
  wireCarets(document);

  var sidebarMenu = document.querySelector(".sidebar .menu");
  if (sidebarMenu) {
    var current = sidebarMenu.querySelector('[aria-current="page"], .menu-row.active');
    if (current) current.scrollIntoView({ block: "center" });
  }

  var collapse = document.querySelector(".sidebar-collapse");
  if (collapse) {
    var collapseLabel = collapse.getAttribute("aria-label");
    var setHidden = function (hidden) {
      document.body.classList.toggle("sidebar-hidden", hidden);
      var label = hidden ? collapse.getAttribute("data-expand") : collapseLabel;
      collapse.setAttribute("aria-label", label);
      collapse.setAttribute("title", label);
    };
    setHidden(stored("sidebar") === "hidden");
    collapse.addEventListener("click", function () {
      var hidden = !document.body.classList.contains("sidebar-hidden");
      setHidden(hidden);
      stored("sidebar", hidden ? "hidden" : "shown");
    });
  }

  // ---- Drawer for small screens --------------------------------------------

  var navToggle = document.querySelector(".navbar-toggle");
  var drawer = null;

  function buildDrawer() {
    var backdrop = element("div", "drawer-backdrop");
    drawer = element("div", "drawer");
    var head = element("div", "drawer-head");
    head.appendChild(document.querySelector(".navbar .brand").cloneNode(true));
    var close = element("button", "icon-button");
    close.type = "button";
    close.setAttribute("aria-label", labels["Close navigation bar"]);
    close.innerHTML = '<svg width="21" height="21" viewBox="0 0 21 21" aria-hidden="true"><path stroke="currentColor" stroke-linecap="round" stroke-width="2" d="M4 4l13 13M17 4L4 17"/></svg>';
    head.appendChild(close);

    var body = element("div", "drawer-body");
    var nav = element("ul", "menu-list drawer-nav");
    document.querySelectorAll(".nav-links .nav-link").forEach(function (link) {
      var item = element("li");
      var copy = link.cloneNode(true);
      copy.className = "menu-link" + (link.classList.contains("active") ? " active" : "");
      item.appendChild(copy);
      nav.appendChild(item);
    });
    var languages = element("li", "drawer-languages");
    document.querySelectorAll(".dropdown-menu a").forEach(function (link) {
      languages.appendChild(link.cloneNode(true));
    });
    nav.appendChild(languages);
    body.appendChild(nav);
    if (sidebarMenu) {
      var menu = sidebarMenu.cloneNode(true);
      wireCarets(menu);
      body.appendChild(menu);
    }
    drawer.appendChild(head);
    drawer.appendChild(body);
    document.body.appendChild(backdrop);
    document.body.appendChild(drawer);
    backdrop.addEventListener("click", closeDrawer);
    close.addEventListener("click", closeDrawer);
  }

  function closeDrawer() {
    document.body.classList.remove("drawer-open", "no-scroll");
    navToggle.setAttribute("aria-expanded", "false");
    navToggle.focus();
  }

  if (navToggle) {
    navToggle.addEventListener("click", function () {
      if (!drawer) buildDrawer();
      document.body.classList.add("drawer-open", "no-scroll");
      navToggle.setAttribute("aria-expanded", "true");
      drawer.querySelector("button").focus();
    });
  }

  // ---- Table of contents: mark the section being read ----------------------

  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc a"));
  if (tocLinks.length) {
    var headings = tocLinks.map(function (link) {
      return document.getElementById(decodeURIComponent(link.getAttribute("href").slice(1)));
    });
    var markSection = function () {
      var offset = document.querySelector(".navbar").offsetHeight + 24;
      var active = 0;
      headings.forEach(function (heading, index) {
        if (heading && heading.getBoundingClientRect().top <= offset) active = index;
      });
      tocLinks.forEach(function (link, index) { link.classList.toggle("active", index === active); });
    };
    document.addEventListener("scroll", markSection, { passive: true });
    markSection();
  }

  // ---- Search ----------------------------------------------------------------

  var searchButton = document.querySelector(".search-button");
  var overlay = null, input = null, results = null, entries = null, selected = 0;

  function fold(text) {
    return text.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }

  function loadIndex(done) {
    if (entries) return done();
    var script = document.createElement("script");
    script.src = root.getAttribute("data-root") + "assets/search-" + root.getAttribute("data-locale") + ".js";
    script.onload = function () {
      entries = (window.SEARCH_INDEX || []).map(function (entry) {
        return { entry: entry, title: fold(entry.t), headings: fold(entry.h.join(" \n ")), text: fold(entry.x) };
      });
      done();
    };
    document.head.appendChild(script);
  }

  function marked(text, words) {
    // Build the line from text nodes, wrapping each matched word in <mark>.
    var holder = document.createDocumentFragment();
    var folded = fold(text), at = 0;
    if (folded.length !== text.length) words = [];
    while (at < text.length) {
      var next = -1, length = 0;
      words.forEach(function (word) {
        var found = folded.indexOf(word, at);
        if (found >= 0 && (next < 0 || found < next)) { next = found; length = word.length; }
      });
      if (next < 0) break;
      holder.appendChild(document.createTextNode(text.slice(at, next)));
      holder.appendChild(element("mark", "", text.slice(next, next + length)));
      at = next + length;
    }
    holder.appendChild(document.createTextNode(text.slice(at)));
    return holder;
  }

  function runSearch() {
    var query = fold(input.value.trim());
    var words = query.split(/\s+/).filter(Boolean);
    results.textContent = "";
    selected = 0;
    if (!words.length) {
      results.appendChild(element("li", "search-empty", labels["Type to search"]));
      return;
    }
    var found = [];
    entries.forEach(function (item) {
      var score = 0;
      for (var i = 0; i < words.length; i++) {
        var word = words[i];
        if (item.title.indexOf(word) >= 0) score += 10;
        else if (item.headings.indexOf(word) >= 0) score += 4;
        else if (item.text.indexOf(word) >= 0) score += 1;
        else return;
      }
      if (item.title === query) score += 20;
      found.push({ score: score, item: item });
    });
    found.sort(function (a, b) { return b.score - a.score; });
    if (!found.length) {
      results.appendChild(element("li", "search-empty", labels["No results for"] + " “" + input.value.trim() + "”"));
      return;
    }
    found.slice(0, 20).forEach(function (hit, index) {
      var entry = hit.item.entry;
      var link = element("a");
      link.href = root.getAttribute("data-locale-root") + entry.u;
      link.setAttribute("aria-selected", String(index === 0));
      var title = element("div", "search-result-title");
      title.appendChild(marked(entry.t, words));
      link.appendChild(title);
      if (entry.g) link.appendChild(element("div", "search-result-path", entry.g));
      var position = hit.item.text.indexOf(words[0]);
      if (position >= 0 && hit.item.text.length === entry.x.length) {
        var snippet = element("div", "search-result-text");
        var start = Math.max(0, position - 40);
        snippet.appendChild(marked((start ? "…" : "") + entry.x.slice(start, start + 140), words));
        link.appendChild(snippet);
      }
      var row = element("li");
      row.appendChild(link);
      results.appendChild(row);
    });
  }

  function moveSelection(step) {
    var links = results.querySelectorAll("a");
    if (!links.length) return;
    links[selected].setAttribute("aria-selected", "false");
    selected = (selected + step + links.length) % links.length;
    links[selected].setAttribute("aria-selected", "true");
    links[selected].scrollIntoView({ block: "nearest" });
  }

  function buildSearch() {
    overlay = element("div", "search-overlay");
    var box = element("div", "search-box");
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.setAttribute("aria-label", labels["Search the lessons"]);
    var row = element("div", "search-input-row");
    row.innerHTML = '<svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="8.5" cy="8.5" r="6"/><path d="M13 13l5 5"/></svg>';
    input = element("input", "search-input");
    input.type = "search";
    input.placeholder = labels["Search the lessons"];
    input.setAttribute("aria-label", labels["Search the lessons"]);
    input.autocomplete = "off";
    row.appendChild(input);
    results = element("ul", "search-results");
    var help = element("div", "search-help");
    [["↵", "to select"], ["↑↓", "to navigate"], ["esc", "to close"]].forEach(function (pair) {
      var hint = element("span");
      hint.appendChild(element("kbd", "", pair[0]));
      hint.appendChild(document.createTextNode(labels[pair[1]]));
      help.appendChild(hint);
    });
    box.appendChild(row);
    box.appendChild(results);
    box.appendChild(help);
    overlay.appendChild(box);
    document.body.appendChild(overlay);

    overlay.addEventListener("mousedown", function (event) {
      if (event.target === overlay) closeSearch();
    });
    input.addEventListener("input", function () { loadIndex(runSearch); });
    input.addEventListener("keydown", function (event) {
      if (event.key === "ArrowDown") { event.preventDefault(); moveSelection(1); }
      else if (event.key === "ArrowUp") { event.preventDefault(); moveSelection(-1); }
      else if (event.key === "Enter") {
        var link = results.querySelectorAll("a")[selected];
        if (link) window.location.href = link.href;
      }
    });
  }

  function openSearch() {
    if (!overlay) buildSearch();
    overlay.classList.add("open");
    document.body.classList.add("no-scroll");
    input.value = "";
    loadIndex(runSearch);
    input.focus();
  }

  function closeSearch() {
    overlay.classList.remove("open");
    document.body.classList.remove("no-scroll");
    if (searchButton) searchButton.focus();
  }

  if (searchButton) {
    searchButton.addEventListener("click", openSearch);
    if (!/Mac|iPhone|iPad/.test(navigator.platform)) {
      var keys = searchButton.querySelectorAll("kbd");
      if (keys.length) keys[0].textContent = "Ctrl";
    }
  }

  document.addEventListener("keydown", function (event) {
    var searchOpen = overlay && overlay.classList.contains("open");
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      if (searchOpen) closeSearch(); else openSearch();
    } else if (event.key === "Escape") {
      if (searchOpen) closeSearch();
      else if (document.body.classList.contains("drawer-open")) closeDrawer();
    }
  });
})();
