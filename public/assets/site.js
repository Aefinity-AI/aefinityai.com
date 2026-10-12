/* AEFINITY AI INC. — site behaviour. Vanilla JS, no dependencies. */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function $(s, c) { return (c || doc).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); }

  /* ---------- theme toggle (persists via try/catch localStorage) ---------- */
  function currentTheme() {
    var t = root.getAttribute("data-theme");
    if (t === "light" || t === "dark") return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function labelToggles() {
    var next = currentTheme() === "dark" ? "light" : "dark";
    $$("[data-theme-toggle]").forEach(function (b) { b.setAttribute("aria-label", "Switch to " + next + " theme"); });
  }
  $$("[data-theme-toggle]").forEach(function (b) {
    b.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("aefinity-theme", next); } catch (e) {}
      labelToggles();
    });
  });
  labelToggles();

  /* ---------- header shadow on scroll ---------- */
  var header = $(".site-header");
  function onScrollHeader() { if (header) header.classList.toggle("scrolled", window.scrollY > 8); }
  window.addEventListener("scroll", onScrollHeader, { passive: true });
  onScrollHeader();

  /* ---------- mobile menu ---------- */
  var menuBtn = $(".menu-btn"), menu = $("#mobile-menu");
  function setMenu(open, focusBtn) {
    if (!menuBtn || !menu) return;
    menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    if (open) { menu.hidden = false; var first = $("a", menu); if (first) first.focus(); }
    else { menu.hidden = true; if (focusBtn) menuBtn.focus(); }
  }
  if (menuBtn && menu) {
    menuBtn.addEventListener("click", function () { setMenu(menuBtn.getAttribute("aria-expanded") !== "true"); });
    $$("a", menu).forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
    doc.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menuBtn.getAttribute("aria-expanded") === "true") setMenu(false, true);
    });
    window.addEventListener("resize", function () { if (window.innerWidth >= 1180 && !menu.hidden) setMenu(false); });
  }

  /* ---------- smooth in-page scrolling (respects reduced motion) ---------- */
  $$('a[href^="#"]').forEach(function (a) {
    a.addEventListener("click", function (e) {
      var id = a.getAttribute("href").slice(1);
      if (!id) return;
      var t = doc.getElementById(id);
      if (!t) return;
      e.preventDefault();
      t.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
      if (history.replaceState) history.replaceState(null, "", "#" + id);
      if (!t.hasAttribute("tabindex")) t.setAttribute("tabindex", "-1");
      try { t.focus({ preventScroll: true }); } catch (err) { t.focus(); }
    });
  });

  /* ---------- scroll spy (aria-current on desktop + mobile links) ---------- */
  var spyLinks = $$("[data-spy] a");
  var ids = [];
  spyLinks.forEach(function (a) { var h = a.getAttribute("href"); if (h && h.charAt(0) === "#" && ids.indexOf(h.slice(1)) < 0) ids.push(h.slice(1)); });
  var sections = ids.map(function (id) { return doc.getElementById(id); }).filter(Boolean);
  function spy() {
    if (!sections.length) return;
    var y = window.scrollY + (window.innerHeight * 0.32);
    var active = null;
    sections.forEach(function (s) { if (s.offsetTop <= y) active = s.id; });
    if ((window.innerHeight + window.scrollY) >= (doc.documentElement.scrollHeight - 4)) active = sections[sections.length - 1].id;
    if (window.scrollY < sections[0].offsetTop - window.innerHeight * 0.5) active = null;
    spyLinks.forEach(function (a) {
      if (a.getAttribute("href") === "#" + active) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
  }
  var spyTick = false;
  window.addEventListener("scroll", function () {
    if (spyTick) return; spyTick = true;
    requestAnimationFrame(function () { spy(); spyTick = false; });
  }, { passive: true });
  window.addEventListener("resize", spy);
  spy();

  /* ---------- reveal on scroll (never hides first-viewport content) ---------- */
  var reveals = $$(".reveal");
  function showAll() { reveals.forEach(function (el) { el.classList.add("in"); }); }
  if (!root.classList.contains("motion-ok") || !("IntersectionObserver" in window)) {
    showAll();
  } else {
    var vh = window.innerHeight || 800;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.01 });
    reveals.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < vh) el.classList.add("in"); else io.observe(el);
    });
    window.addEventListener("beforeprint", showAll);
    /* safety net: nothing stays hidden if the observer never fires */
    setTimeout(function () {
      reveals.forEach(function (el) { if (el.getBoundingClientRect().top < window.innerHeight) el.classList.add("in"); });
    }, 1500);
  }
  /* reveal is wired up; the head script's fallback may now stand down */
  window.__siteReady = true;

  /* ---------- copy to clipboard (Clipboard API + execCommand fallback) ---------- */
  function fallbackCopy(text) {
    var ta = doc.createElement("textarea");
    ta.value = text; ta.setAttribute("readonly", "");
    ta.style.position = "fixed"; ta.style.top = "-1000px"; ta.style.opacity = "0";
    doc.body.appendChild(ta); ta.select();
    var ok = false;
    try { ok = doc.execCommand("copy"); } catch (e) { ok = false; }
    doc.body.removeChild(ta);
    return ok;
  }
  $$("[data-copy]").forEach(function (btn) {
    var label = $(".copy-label", btn);
    btn.addEventListener("click", function () {
      var src = doc.getElementById(btn.getAttribute("data-copy"));
      if (!src) return;
      var text = src.textContent.trim();
      function done(ok) {
        btn.classList.toggle("copied", ok);
        if (label) label.textContent = ok ? "Copied" : "Press Ctrl+C";
        var live = $("#copy-live"); if (live) live.textContent = ok ? "Command copied to clipboard." : "Copy failed. Select the command and copy it manually.";
        if (!ok) { var r = doc.createRange(); r.selectNodeContents(src); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); }
        clearTimeout(btn._t);
        btn._t = setTimeout(function () { btn.classList.remove("copied"); if (label) label.textContent = "Copy"; }, 2000);
      }
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(fallbackCopy(text)); });
      } else { done(fallbackCopy(text)); }
    });
  });

  /* ---------- SHA-256 (pure JS, so the demo works without Web Crypto) ---------- */
  var K = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  function utf8(str) {
    if (window.TextEncoder) return new TextEncoder().encode(str);
    var s = unescape(encodeURIComponent(str)), a = new Uint8Array(s.length);
    for (var i = 0; i < s.length; i++) a[i] = s.charCodeAt(i);
    return a;
  }
  function sha256hex(str) {
    var msg = utf8(str), l = msg.length, bitLen = l * 8;
    var n = ((l + 9 + 63) >> 6) << 6, m = new Uint8Array(n);
    m.set(msg); m[l] = 0x80;
    var dv = new DataView(m.buffer);
    dv.setUint32(n - 4, bitLen >>> 0); dv.setUint32(n - 8, Math.floor(bitLen / 4294967296));
    var H = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    var W = new Array(64);
    for (var off = 0; off < n; off += 64) {
      for (var t = 0; t < 16; t++) W[t] = dv.getUint32(off + t * 4);
      for (t = 16; t < 64; t++) {
        var x = W[t - 15], y = W[t - 2];
        var s0 = ((x >>> 7) | (x << 25)) ^ ((x >>> 18) | (x << 14)) ^ (x >>> 3);
        var s1 = ((y >>> 17) | (y << 15)) ^ ((y >>> 19) | (y << 13)) ^ (y >>> 10);
        W[t] = (W[t - 16] + s0 + W[t - 7] + s1) | 0;
      }
      var a = H[0], b = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
      for (t = 0; t < 64; t++) {
        var S1 = ((e >>> 6) | (e << 26)) ^ ((e >>> 11) | (e << 21)) ^ ((e >>> 25) | (e << 7));
        var ch = (e & f) ^ (~e & g);
        var t1 = (h + S1 + ch + K[t] + W[t]) | 0;
        var S0 = ((a >>> 2) | (a << 30)) ^ ((a >>> 13) | (a << 19)) ^ ((a >>> 22) | (a << 10));
        var mj = (a & b) ^ (a & c) ^ (b & c);
        var t2 = (S0 + mj) | 0;
        h = g; g = f; f = e; e = (d + t1) | 0; d = c; c = b; b = a; a = (t1 + t2) | 0;
      }
      H[0] = (H[0] + a) | 0; H[1] = (H[1] + b) | 0; H[2] = (H[2] + c) | 0; H[3] = (H[3] + d) | 0;
      H[4] = (H[4] + e) | 0; H[5] = (H[5] + f) | 0; H[6] = (H[6] + g) | 0; H[7] = (H[7] + h) | 0;
    }
    return H.map(function (v) { return ("00000000" + (v >>> 0).toString(16)).slice(-8); }).join("");
  }

  /* ---------- digest demo (illustration, not the CIS-2 verifier) ---------- */
  var demo = $("#demo");
  if (demo) {
    var ta = $("#demo-a"), tb = $("#demo-b"), oa = $("#digest-a"), ob = $("#digest-b");
    var status = $("#demo-status-text"), meter = $("#demo-meter"), meterLabel = $("#demo-meter-label"), mark = $("#demo-char");
    var original = ta.value;
    ta.removeAttribute("readonly"); tb.removeAttribute("readonly");
    function render(out, hex, other) {
      var html = "";
      for (var g = 0; g < 8; g++) {
        html += '<span class="g">';
        for (var i = g * 8; i < g * 8 + 8; i++) {
          var ch = hex.charAt(i);
          html += (other && other.charAt(i) !== ch) ? '<span class="x">' + ch + "</span>" : ch;
        }
        html += "</span>";
      }
      out.innerHTML = html;
    }
    function update() {
      var ha = sha256hex(ta.value), hb = sha256hex(tb.value), diff = 0;
      for (var i = 0; i < 64; i++) if (ha.charAt(i) !== hb.charAt(i)) diff++;
      render(oa, ha, null);
      render(ob, hb, ha);
      var same = diff === 0;
      demo.classList.toggle("differs", !same);
      status.textContent = same ? "Digests match." : "Digests differ.";
      meter.style.width = (diff / 64 * 100).toFixed(1) + "%";
      meterLabel.textContent = diff + " of 64 hex characters differ";
      if (same && mark) mark.textContent = "";
    }
    function flip() {
      var s = tb.value;
      if (!s.length) { tb.value = original; update(); return; }
      var idx = Math.floor(Math.random() * s.length);
      var code = s.charCodeAt(idx);
      // one-bit XOR flip; skip characters whose flip is not printable
      for (var tries = 0; tries < 40 && (code < 33 || code > 126 || (code ^ 1) < 33 || (code ^ 1) > 126); tries++) {
        idx = Math.floor(Math.random() * s.length); code = s.charCodeAt(idx);
      }
      var nc = String.fromCharCode(code ^ 1);
      tb.value = s.slice(0, idx) + nc + s.slice(idx + 1);
      update();
      if (mark) mark.innerHTML = "Flipped one bit of character " + (idx + 1) + ": <code>" + esc(s.charAt(idx)) + "</code> &rarr; <code>" + esc(nc) + "</code>";
    }
    function esc(c) { return c.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
    ta.addEventListener("input", function () { if (mark) mark.textContent = ""; update(); });
    tb.addEventListener("input", function () { if (mark) mark.textContent = ""; update(); });
    $("#demo-flip").addEventListener("click", flip);
    $("#demo-reset").addEventListener("click", function () { ta.value = original; tb.value = original; if (mark) mark.textContent = ""; update(); });
    update();
  }

  /* ---------- hero instrument: finished MATCH state is the static frame;
       a gentle re-verify pass animates on top, then settles back ---------- */
  var inst = $("[data-instrument]");
  if (inst && !reduce) {
    var rows = $$(".stream li", inst);
    var stat = $(".cmp-status", inst), statTxt = $(".cmp-status .s", inst);
    var hexes = $$(".cmp-row .hex", inst);
    var finals = hexes.map(function (h) { return h.innerHTML; });
    var running = false, visible = false, timer = null;
    function scramble(el, finalHTML, ms) {
      var groups = $$("span", el), orig = groups.map(function (g) { return g.textContent; });
      var t0 = performance.now();
      (function step(now) {
        var p = Math.min(1, (now - t0) / ms);
        groups.forEach(function (g, gi) {
          var settle = (gi + 1) / groups.length;
          if (p >= settle) { g.textContent = orig[gi]; return; }
          var s = ""; for (var i = 0; i < orig[gi].length; i++) s += "0123456789abcdef".charAt(Math.floor(Math.random() * 16));
          g.textContent = s;
        });
        if (p < 1) requestAnimationFrame(step); else el.innerHTML = finalHTML;
      })(t0);
    }
    function run() {
      if (running || !visible || doc.hidden) return;
      running = true;
      stat.classList.add("busy"); statTxt.textContent = "re-verifying";
      var i = 0;
      (function next() {
        rows.forEach(function (r) { r.classList.remove("scan"); });
        if (i < rows.length / 2) {
          rows[i].classList.add("scan"); rows[i + rows.length / 2].classList.add("scan");
          i++; setTimeout(next, 170);
        } else {
          hexes.forEach(function (h, k) { scramble(h, finals[k], 900); });
          setTimeout(function () {
            stat.classList.remove("busy"); statTxt.textContent = "match";
            running = false;
          }, 1000);
        }
      })();
    }
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { visible = en[0].isIntersecting; }, { threshold: 0.4 }).observe(inst);
    } else { visible = true; }
    setTimeout(function () { run(); timer = setInterval(run, 11000); }, 4500);
  }

})();
