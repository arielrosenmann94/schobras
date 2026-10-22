/* SCHOBRAS.CL: JS propio mínimo (sin librerías). Sin JS todo el contenido queda visible. */
(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("js");

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Menú de pantalla completa (celular y tablet) */
  var toggle = document.querySelector("[data-menu-toggle]");
  var menu = toggle && document.getElementById(toggle.getAttribute("aria-controls"));

  if (menu) {
    var outside = document.querySelectorAll("main, footer, .whatsapp-float");
    var desktop = window.matchMedia("(min-width: 64em)");

    var setOpen = function (open, returnFocus) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      root.classList.toggle("menu-open", open);
      outside.forEach(function (el) { el.inert = open; });
      if (!open && returnFocus) toggle.focus();
    };

    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && root.classList.contains("menu-open")) setOpen(false, true);
    });
    menu.addEventListener("click", function (event) {
      if (event.target.closest("a")) setOpen(false);
    });
    desktop.addEventListener("change", function (event) {
      if (event.matches) setOpen(false);
    });
  }

  /* Revelado al hacer scroll: una sola vez por elemento */
  var items = document.querySelectorAll(".reveal");
  var show = function (el) { el.classList.add("visible"); };

  if (reduceMotion || !("IntersectionObserver" in window)) {
    items.forEach(show);
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          show(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    items.forEach(function (el) { observer.observe(el); });
  }
})();
