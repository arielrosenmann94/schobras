/* SCHOBRAS.CL /sch/: "Probar en el encabezado" pone la variante elegida en la marca del
   encabezado fijo de esta página (solo en pantalla; no cambia nada en la web). Un segundo
   clic en la misma opción vuelve a la marca actual. */
(function () {
  "use strict";

  var word = document.querySelector(".site-header .brand__word");
  var buttons = document.querySelectorAll("[data-sch-try]");
  if (!word || !buttons.length) return;

  var original = word.innerHTML;

  var reset = function () {
    word.innerHTML = original;
    word.classList.remove("is-trying");
    for (var i = 0; i < buttons.length; i++) buttons[i].setAttribute("aria-pressed", "false");
  };

  var tryOption = function (button) {
    var wasPressed = button.getAttribute("aria-pressed") === "true";
    reset();
    if (wasPressed) return;
    var sample = button.parentNode.querySelector(".sch-sample--large .wm");
    if (!sample) return;
    word.innerHTML = "";
    word.appendChild(sample.cloneNode(true));
    word.classList.add("is-trying");
    button.setAttribute("aria-pressed", "true");
  };

  for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", function (event) {
      tryOption(event.currentTarget);
    });
  }
})();
