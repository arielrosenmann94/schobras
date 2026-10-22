/* SCHOBRAS.CL panel: evita el doble envío (un doble clic creaba proyectos o fotos
   repetidos). Al enviar un formulario se deshabilitan sus botones; sin JS el panel
   funciona igual. */
(function () {
  "use strict";

  var buttons = function (scope) {
    return scope.querySelectorAll('button[type="submit"], input[type="submit"]');
  };

  document.addEventListener("submit", function (event) {
    if (event.defaultPrevented) return;
    Array.prototype.forEach.call(buttons(event.target), function (button) {
      button.disabled = true;
    });
  });

  /* Al volver con "atrás" el navegador puede restaurar la página con los botones
     deshabilitados (bfcache): se reactivan. */
  window.addEventListener("pageshow", function (event) {
    if (!event.persisted) return;
    Array.prototype.forEach.call(buttons(document), function (button) {
      button.disabled = false;
    });
  });
})();
