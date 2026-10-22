/* SCHOBRAS.CL: JS propio mínimo (sin librerías). Sin JS todo el contenido queda visible.
   La clase "js" se agrega AL FINAL: si algo falla antes, .reveal y el menú quedan
   en su versión sin JS (todo visible y navegable). */
(function () {
  "use strict";

  var root = document.documentElement;
  var each = function (list, fn) { Array.prototype.forEach.call(list, fn); };
  var onMediaChange = function (query, fn) {
    if (query.addEventListener) query.addEventListener("change", fn);
    else if (query.addListener) query.addListener(fn);
  };

  /* Revelado al hacer scroll: una sola vez por elemento */
  var items = document.querySelectorAll(".reveal");
  var show = function (el) { el.classList.add("visible"); };
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reduceMotion || !("IntersectionObserver" in window)) {
    each(items, show);
  } else {
    var observer = new IntersectionObserver(function (entries) {
      each(entries, function (entry) {
        if (entry.isIntersecting) {
          show(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    each(items, function (el) { observer.observe(el); });
  }

  /* Menú de pantalla completa (celular y tablet) */
  var toggle = document.querySelector("[data-menu-toggle]");
  var menu = toggle && document.getElementById(toggle.getAttribute("aria-controls"));

  if (menu) {
    var outside = document.querySelectorAll("main, footer, .whatsapp-float");

    var setOpen = function (open, returnFocus) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      root.classList.toggle("menu-open", open);
      each(outside, function (el) { el.inert = open; });
      if (!open && returnFocus) toggle.focus();
    };

    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && root.classList.contains("menu-open")) setOpen(false, true);
    });
    menu.addEventListener("click", function (event) {
      if (event.target.closest && event.target.closest("a")) setOpen(false);
    });
    if (window.matchMedia) {
      onMediaChange(window.matchMedia("(min-width: 64em)"), function (event) {
        if (event.matches) setOpen(false);
      });
    }
  }

  root.classList.add("js");
})();
