/* SCHOBRAS.CL /v2/ (sin librerías propias; three.js solo bajo demanda).
   1. Portada 3D: carga v2-hero3d.min.js si hay WebGL, movimiento permitido y alto suficiente.
   2. Proceso: escribe --p (0 → 1, avance por los 6 pasos) y marca el paso en curso.
   Sin JS o con movimiento reducido: el plano SVG en la portada y la obra terminada (--p: 1). */
(function () {
  "use strict";

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── Portada 3D ─────────────────────────────────────────────────────── */
  var hero = document.querySelector("[data-hero3d-module]");
  if (hero) {
    var tall = window.matchMedia("(min-height: 34em)").matches;
    if (reduce || !tall || !window.WebGLRenderingContext) {
      hero.classList.add("no-3d");
    } else {
      import(hero.getAttribute("data-hero3d-module"))
        .then(function (module) {
          if (!module.start(hero)) hero.classList.add("no-3d");
        })
        .catch(function () { hero.classList.add("no-3d"); });
    }
  }

  /* ── Proceso: la obra se levanta ────────────────────────────────────── */
  var build = document.querySelector("[data-build]");
  var list = build && build.querySelector("[data-build-steps]");
  var stage = build && build.querySelector(".v2-stage");
  if (!list || !stage || reduce) return;

  var steps = list.children;
  var queued = false;

  var update = function () {
    queued = false;
    var rect = list.getBoundingClientRect();
    var stickTop = parseFloat(getComputedStyle(stage).top) || 0;
    var stageHeight = stage.offsetHeight;
    /* Lado a lado (computador): arranca cuando el dibujo ya quedó fijo y completo, y
       termina justo antes de que se suelte. Apilado (celular): arranca cuando el
       primer paso asoma bajo el dibujo y termina con el último paso aún a la vista.
       El dibujo fijo cambia su posición vertical: el lado a lado se lee en horizontal. */
    var sideBySide = stage.getBoundingClientRect().left >= rect.right;
    var start = sideBySide ? stickTop : stickTop + stageHeight;
    var end = sideBySide ? stickTop + stageHeight : window.innerHeight * 0.85;
    var travel = rect.height - (end - start);
    var p = travel > 0 ? Math.min(1, Math.max(0, (start - rect.top) / travel)) : 1;
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
