/* RadScroll spike 1 probe @VERSION@: a stand-in for the viewer, shaped like it (one IIFE, no top-level let/const,
   listeners only on the stack, safe to run twice). It turns every .rs-status badge green and counts its runs. */
(function () {
  "use strict";
  var VERSION = "@VERSION@";

  function show(stack, i) {
    var imgs = stack.querySelectorAll("img");
    var n = imgs.length;
    i = Math.max(0, Math.min(n - 1, i));
    for (var k = 0; k < n; k++) imgs[k].classList.toggle("rs-on", k === i);
    stack.setAttribute("data-rs-at", String(i));
    var tag = stack.querySelector(".rs-at");
    if (tag) tag.textContent = i + 1 + " / " + n;
  }

  function bind(stack) {
    var y0 = null;
    var at0 = 0;
    stack.classList.add("rs-live");
    show(stack, 0);
    stack.addEventListener("wheel", function (e) {
      e.preventDefault();
      show(stack, +stack.getAttribute("data-rs-at") + (e.deltaY > 0 ? 1 : -1));
    }, { passive: false });
    stack.addEventListener("touchstart", function (e) {
      y0 = e.touches[0].clientY;
      at0 = +stack.getAttribute("data-rs-at");
    }, { passive: true });
    stack.addEventListener("touchmove", function (e) {
      if (y0 === null) return;
      e.preventDefault();
      show(stack, at0 + Math.round((e.touches[0].clientY - y0) / 12));
    }, { passive: false });
    stack.addEventListener("touchend", function () { y0 = null; });
  }

  function scan() {
    var stacks = document.querySelectorAll(".ra-board .ra-stack");
    for (var i = 0; i < stacks.length; i++) {
      if (!stacks[i].classList.contains("rs-live")) bind(stacks[i]);
    }
    var badges = document.querySelectorAll(".rs-status");
    for (var j = 0; j < badges.length; j++) {
      var b = badges[j];
      var runs = +(b.getAttribute("data-rs-runs") || 0) + 1;
      b.setAttribute("data-rs-runs", String(runs));
      b.className = "rs-status rs-ok";
      b.textContent = "RAN · " + (b.getAttribute("data-delivery") || "?") + " · probe " + VERSION +
        " · runs " + runs;
    }
  }

  window.RadScrollProbe = { version: VERSION, scan: scan };
  scan();
})();
