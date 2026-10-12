/* Aefinity AI site v3: theme toggle, mobile menu, lab filters, copy buttons. No dependencies. */
(function () {
  "use strict";
  var root = document.documentElement;
  var KEY = "aefinity-theme";

  function systemDark() {
    return !!(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
  }
  function current() {
    var t = root.getAttribute("data-theme");
    return t === "light" || t === "dark" ? t : (systemDark() ? "dark" : "light");
  }
  function label(btn) {
    btn.setAttribute("aria-label", current() === "dark" ? "Switch to light theme" : "Switch to dark theme");
  }

  document.addEventListener("DOMContentLoaded", function () {
    /* theme */
    var tb = document.querySelector("[data-theme-toggle]");
    if (tb) {
      label(tb);
      tb.addEventListener("click", function () {
        var next = current() === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", next);
        try { localStorage.setItem(KEY, next); } catch (e) { /* storage unavailable */ }
        label(tb);
      });
    }

    /* menu */
    var header = document.querySelector(".site-header");
    var mb = document.querySelector(".menu-btn");
    if (header && mb) {
      var setMenu = function (open) {
        mb.setAttribute("aria-expanded", String(open));
        header.classList.toggle("nav-open", open);
        root.classList.toggle("nav-lock", open);
      };
      mb.addEventListener("click", function () {
        setMenu(mb.getAttribute("aria-expanded") !== "true");
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && header.classList.contains("nav-open")) {
          setMenu(false);
          mb.focus();
        }
      });
      window.addEventListener("resize", function () {
        if (window.innerWidth >= 1024 && header.classList.contains("nav-open")) setMenu(false);
      });
    }

    /* lab filters */
    var list = document.querySelector("[data-labs]");
    if (list) {
      var cards = Array.prototype.slice.call(list.querySelectorAll(".lab-card"));
      var chips = Array.prototype.slice.call(document.querySelectorAll(".chip[data-f]"));
      var count = document.querySelector("[data-count]");
      var empty = document.querySelector("[data-empty]");
      var state = { outcome: "all", q: "all" };
      try {
        var params = new URLSearchParams(window.location.search);
        if (params.get("outcome")) state.outcome = params.get("outcome");
        if (params.get("q")) state.q = params.get("q");
      } catch (e) { /* old browser */ }
      var valid = function (f, v) {
        return chips.some(function (c) { return c.getAttribute("data-f") === f && c.getAttribute("data-v") === v; });
      };
      if (!valid("outcome", state.outcome)) state.outcome = "all";
      if (!valid("q", state.q)) state.q = "all";

      var apply = function (push) {
        var shown = 0;
        cards.forEach(function (c) {
          var okO = state.outcome === "all" || c.getAttribute("data-outcome") === state.outcome;
          var qs = (c.getAttribute("data-q") || "").split(" ");
          var okQ = state.q === "all" || qs.indexOf(state.q) !== -1;
          var show = okO && okQ;
          c.hidden = !show;
          if (show) shown++;
        });
        chips.forEach(function (c) {
          var f = c.getAttribute("data-f");
          c.setAttribute("aria-pressed", String(state[f] === c.getAttribute("data-v")));
        });
        if (count) count.textContent = "Showing " + shown + " of " + cards.length + " labs";
        if (empty) empty.hidden = shown !== 0;
        if (push && window.history && window.history.replaceState) {
          var qs2 = [];
          if (state.outcome !== "all") qs2.push("outcome=" + encodeURIComponent(state.outcome));
          if (state.q !== "all") qs2.push("q=" + encodeURIComponent(state.q));
          window.history.replaceState(null, "", window.location.pathname + (qs2.length ? "?" + qs2.join("&") : ""));
        }
      };
      chips.forEach(function (c) {
        c.addEventListener("click", function () {
          state[c.getAttribute("data-f")] = c.getAttribute("data-v");
          apply(true);
        });
      });
      var reset = document.querySelector("[data-reset]");
      if (reset) reset.addEventListener("click", function () { state.outcome = "all"; state.q = "all"; apply(true); });
      apply(false);
    }

    /* copy buttons */
    Array.prototype.forEach.call(document.querySelectorAll("[data-copy]"), function (btn) {
      btn.addEventListener("click", function () {
        var el = document.getElementById(btn.getAttribute("data-copy"));
        if (!el) return;
        var text = el.textContent;
        var done = function () {
          btn.textContent = "Copied";
          setTimeout(function () { btn.textContent = "Copy"; }, 1600);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done, function () {});
        } else {
          var r = document.createRange();
          r.selectNodeContents(el);
          var s = window.getSelection();
          s.removeAllRanges();
          s.addRange(r);
          try { document.execCommand("copy"); done(); } catch (e) { /* select only */ }
        }
      });
    });
  });
})();
