/* SCHOBRAS.CL /v2/: la obra se levanta con el scroll (sin librerías).
   Escribe --p (0 → 1, avance por los 6 pasos del Proceso) y marca el paso en curso.
   Sin JS o con movimiento reducido el CSS deja --p en 1: el dibujo terminado. */
(function () {
  "use strict";

  var build = document.querySelector("[data-build]");
  var list = build && build.querySelector("[data-build-steps]");
  if (!list) return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var steps = list.children;
  var desktop = window.matchMedia("(min-width: 64em)");
  var queued = false;

  var update = function () {
    queued = false;
    var rect = list.getBoundingClientRect();
    /* En el celular el dibujo ocupa la parte de arriba: el paso se lee más abajo. */
    var anchor = window.innerHeight * (desktop.matches ? 0.5 : 0.72);
    var p = Math.min(1, Math.max(0, (anchor - rect.top) / rect.height));
    var active = Math.min(steps.length - 1, Math.floor(p * steps.length));
    build.style.setProperty("--p", p.toFixed(4));
    for (var i = 0; i < steps.length; i++) {
      steps[i].classList.toggle("is-active", i === active);
    }
  };

  var request = function () {
    if (!queued) {
      queued = true;
      window.requestAnimationFrame(update);
    }
  };

  build.classList.add("is-live");
  window.addEventListener("scroll", request, { passive: true });
  window.addEventListener("resize", request);
  update();
})();
