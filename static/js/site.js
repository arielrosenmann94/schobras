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

  /* Visor de fotos (<dialog>): sin soporte, los enlaces abren la imagen. showModal deja
     el resto inerte (foco atrapado) y Esc cierra de forma nativa. */
  var links = document.querySelectorAll("a[data-gallery]");
  if (links.length && typeof HTMLDialogElement === "function" && HTMLDialogElement.prototype.showModal) {
    var dialog = document.createElement("dialog");
    dialog.className = "viewer";
    dialog.setAttribute("aria-label", "Galería de fotos");
    dialog.innerHTML =
      '<img class="viewer__img" alt="">' +
      '<p class="viewer__count" aria-live="polite"></p>' +
      '<button type="button" class="viewer__btn viewer__btn--close" aria-label="Cerrar galería"></button>' +
      '<button type="button" class="viewer__btn viewer__btn--prev" aria-label="Foto anterior"></button>' +
      '<button type="button" class="viewer__btn viewer__btn--next" aria-label="Foto siguiente"></button>';
    document.body.appendChild(dialog);

    var big = dialog.querySelector(".viewer__img");
    var count = dialog.querySelector(".viewer__count");
    var current = 0;
    var startX = null;

    var go = function (index) {
      current = (index + links.length) % links.length;
      var thumb = links[current].querySelector("img");
      big.src = links[current].href;
      big.alt = thumb ? thumb.alt : "";
      count.textContent = (current + 1) + " de " + links.length;
    };

    each(links, function (link, index) {
      link.addEventListener("click", function (event) {
        event.preventDefault();
        go(index);
        dialog.showModal();
      });
    });
    dialog.querySelector(".viewer__btn--close").addEventListener("click", function () { dialog.close(); });
    dialog.querySelector(".viewer__btn--prev").addEventListener("click", function () { go(current - 1); });
    dialog.querySelector(".viewer__btn--next").addEventListener("click", function () { go(current + 1); });
    dialog.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") go(current - 1);
      else if (event.key === "ArrowRight") go(current + 1);
    });
    dialog.addEventListener("touchstart", function (event) { startX = event.changedTouches[0].clientX; }, { passive: true });
    dialog.addEventListener("touchend", function (event) {
      if (startX === null) return;
      var delta = event.changedTouches[0].clientX - startX;
      startX = null;
      if (Math.abs(delta) > 50) go(current + (delta < 0 ? 1 : -1));
    });
    dialog.addEventListener("click", function (event) { if (event.target === dialog) dialog.close(); });
    dialog.addEventListener("close", function () { big.removeAttribute("src"); });
  }

  root.classList.add("js");
})();
