/* SCHOBRAS.CL /v2/: portada 3D "del plano a la obra" (three.js, compilado con esbuild:
   `npm run build` en frontend/ genera static/js/v2-hero3d.min.js).
   Una obra industrial: nave de 24,00 × 16,00 m con marcos de acero (ejes A–G cada 4 m)
   y un bloque de oficinas de dos pisos al frente. Arranca vista desde arriba (el plano)
   y con el scroll la cámara baja y la obra avanza por etapas: fundaciones, estructura,
   cerramientos y entrega (las ventanas se encienden). Cada etapa muestra un servicio
   (lista [data-stages] de la plantilla). La cámara sigue al scroll con inercia y, en
   computador, orbita apenas con el mouse. Los colores salen de los tokens de site.css. */
import {
  BoxGeometry,
  BufferGeometry,
  Color,
  DirectionalLight,
  ExtrudeGeometry,
  Float32BufferAttribute,
  Fog,
  Group,
  HemisphereLight,
  LineDashedMaterial,
  LineSegments,
  Mesh,
  MeshStandardMaterial,
  PCFShadowMap,
  PerspectiveCamera,
  PlaneGeometry,
  Scene,
  Shape,
  WebGLRenderer,
} from "three";

const EAVE = 7;        // altura de muros de la nave
const RIDGE = 8.2;     // cumbrera (pendiente 15 %)
const HALF_X = 12;     // nave: x −12 … 12
const HALF_Z = 8;      // nave: z −8 … 8
const FRAMES = [-12, -8, -4, 0, 4, 8, 12];
const FLOOR = 3.6;     // altura de piso de las oficinas

const clamp01 = (v) => Math.min(1, Math.max(0, v));
const span = (t, a, b) => clamp01((t - a) / (b - a));
const ease = (x) => x * x * (3 - 2 * x);
const lerp = (a, b, x) => a + (b - a) * x;
const roofY = (z) => RIDGE - (Math.abs(z) / HALF_Z) * (RIDGE - EAVE);

function token(name) {
  return new Color(getComputedStyle(document.documentElement).getPropertyValue(name).trim());
}

function box(parent, material, size, position, { shadow = true, rotationX = 0 } = {}) {
  const mesh = new Mesh(new BoxGeometry(...size), material);
  mesh.position.set(...position);
  mesh.rotation.x = rotationX;
  mesh.castShadow = shadow;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

/* Un muro recto con sus vanos: tramos llenos, antepechos y dinteles. */
function wall(group, material, { axis, from, to, at, thickness, height, openings = [] }) {
  const piece = (a, b, y0, y1) => {
    if (b - a < 0.001 || y1 - y0 < 0.001) return;
    const middle = (a + b) / 2;
    const size = axis === "x" ? [b - a, y1 - y0, thickness] : [thickness, y1 - y0, b - a];
    const position = axis === "x" ? [middle, (y0 + y1) / 2, at] : [at, (y0 + y1) / 2, middle];
    box(group, material, size, position);
  };
  let cursor = from;
  for (const opening of openings) {
    piece(cursor, opening.a, 0, height);
    piece(opening.a, opening.b, 0, opening.bottom);
    piece(opening.a, opening.b, opening.top, height);
    cursor = opening.b;
  }
  piece(cursor, to, 0, height);
}

/* Frontón de la nave (triángulo sobre el muro de los extremos, en el plano ZY). */
function gable(group, material, x) {
  const shape = new Shape();
  shape.moveTo(-HALF_Z, EAVE);
  shape.lineTo(HALF_Z, EAVE);
  shape.lineTo(0, RIDGE);
  shape.closePath();
  const mesh = new Mesh(new ExtrudeGeometry(shape, { depth: 0.16, bevelEnabled: false }), material);
  mesh.rotation.y = Math.PI / 2;
  mesh.position.x = x;
  mesh.castShadow = true;
  group.add(mesh);
}

function lines(points, material) {
  const geometry = new BufferGeometry();
  geometry.setAttribute("position", new Float32BufferAttribute(points, 3));
  const segments = new LineSegments(geometry, material);
  segments.computeLineDistances();
  return segments;
}

function buildWorks(colors) {
  const steel = new MeshStandardMaterial({ color: colors.bronze, roughness: 0.45, metalness: 0.35 });
  const cladding = new MeshStandardMaterial({ color: colors.anthracite, roughness: 0.8 });
  const roofing = new MeshStandardMaterial({ color: colors.cement, roughness: 0.55, metalness: 0.2 });
  const concrete = new MeshStandardMaterial({ color: colors.white, roughness: 0.95 });
  const glassMat = new MeshStandardMaterial({
    color: colors.cement, roughness: 0.1, metalness: 0.2, transparent: true,
    emissive: colors.bronze, emissiveIntensity: 0,
  });
  const lineMat = new LineDashedMaterial({ color: colors.cement, dashSize: 0.7, gapSize: 0.45, transparent: true });
  const dimMat = new LineDashedMaterial({ color: colors.bronze, dashSize: 100, gapSize: 0, transparent: true });

  // Fundaciones: zapatas bajo cada pilar y el radier.
  const footings = new Group();
  for (const x of FRAMES) {
    for (const z of [-7.75, 7.75]) box(footings, concrete, [1.4, 0.6, 1.4], [x, -0.3, z], { shadow: false });
  }
  const slab = new Group();
  box(slab, concrete, [24.4, 0.25, 16.4], [0, -0.125, 0], { shadow: false });
  box(slab, concrete, [10.4, 0.25, 5.4], [-7, -0.125, 10.85], { shadow: false });

  // Estructura: un marco de acero por eje (pilares + vigas a dos aguas); suben uno por uno.
  const frames = FRAMES.map((x) => {
    const frame = new Group();
    for (const z of [-7.75, 7.75]) box(frame, steel, [0.35, EAVE, 0.5], [x, EAVE / 2, z]);
    const run = 7.75;
    const rise = RIDGE - EAVE;
    const length = Math.hypot(run, rise);
    const slope = Math.atan2(rise, run);
    for (const side of [-1, 1]) {
      box(frame, steel, [0.3, 0.5, length], [x, EAVE + rise / 2 + 0.25, (side * run) / 2], { rotationX: side * slope });
    }
    return frame;
  });
  // Correas: crecen a lo largo de la nave, de un extremo al otro.
  const purlins = new Group();
  purlins.position.x = -HALF_X;
  for (const z of [-7, -4.7, -2.4, 2.4, 4.7, 7]) {
    box(purlins, steel, [24, 0.18, 0.18], [HALF_X, roofY(z) + 0.6, z]);
  }

  // Cerramientos: muros con portón al frente y ventana corrida en el extremo izquierdo.
  const walls = new Group();
  wall(walls, cladding, { axis: "x", from: -HALF_X, to: HALF_X, at: HALF_Z + 0.08, thickness: 0.16, height: EAVE, openings: [{ a: 3, b: 9, bottom: 0, top: 5.5 }] });
  wall(walls, cladding, { axis: "x", from: -HALF_X, to: HALF_X, at: -HALF_Z - 0.08, thickness: 0.16, height: EAVE });
  wall(walls, cladding, { axis: "z", from: -HALF_Z, to: HALF_Z, at: -HALF_X - 0.08, thickness: 0.16, height: EAVE, openings: [{ a: -6, b: 6, bottom: 4.8, top: 6.2 }] });
  wall(walls, cladding, { axis: "z", from: -HALF_Z, to: HALF_Z, at: HALF_X + 0.08, thickness: 0.16, height: EAVE });
  gable(walls, cladding, -HALF_X - 0.16);
  gable(walls, cladding, HALF_X);

  // Cubierta (planchas claras), baja al final de los cerramientos.
  const roof = new Group();
  const roofRun = HALF_Z + 0.6;
  const roofRise = roofRun * ((RIDGE - EAVE) / HALF_Z);
  const roofLength = Math.hypot(roofRun, roofRise);
  for (const side of [-1, 1]) {
    box(roof, roofing, [24.8, 0.14, roofLength], [0, RIDGE + 0.85 - roofRise / 2, (side * roofRun) / 2], { rotationX: side * Math.atan2(roofRise, roofRun) });
  }

  // Oficinas: dos pisos al frente de la nave, con losas y pilares; fachada vidriada al final.
  const office = new Group();
  for (const y of [FLOOR, FLOOR * 2]) box(office, concrete, [10.4, 0.3, 5.4], [-7, y - 0.15, 10.85]);
  for (const x of [-11.8, -7, -2.2]) {
    for (const z of [8.4, 13.3]) box(office, steel, [0.3, FLOOR * 2, 0.3], [x, FLOOR, z]);
  }

  const glazing = new Group();
  box(glazing, glassMat, [9.6, FLOOR * 2 - 0.3, 0.06], [-7, FLOOR - 0.15, 13.35], { shadow: false });
  box(glazing, glassMat, [0.06, FLOOR * 2 - 0.3, 4.9], [-12.05, FLOOR - 0.15, 10.85], { shadow: false });
  box(glazing, glassMat, [0.06, 1.4, 12], [-HALF_X - 0.08, 5.5, 0], { shadow: false });
  box(glazing, glassMat, [6, 5.5, 0.06], [6, 2.75, HALF_Z + 0.2], { shadow: false });

  // Plano en el suelo: ejes A–G y la cota de 24,00.
  const axisPoints = [];
  for (const x of FRAMES) axisPoints.push(x, 0.02, -11, x, 0.02, 15);
  const axes = lines(axisPoints, lineMat);
  const dims = lines([
    -12, 0.02, -10, 12, 0.02, -10,
    -12, 0.02, -9.4, -12, 0.02, -10.6,
    12, 0.02, -9.4, 12, 0.02, -10.6,
  ], dimMat);

  return { footings, slab, frames, purlins, walls, roof, office, glazing, axes, dims, glassMat, lineMat, dimMat };
}

export function start(hero) {
  const host = hero.querySelector("[data-scene]");
  const pin = hero.querySelector(".v2-hero__pin");
  if (!host || !pin) return false;

  let renderer;
  try {
    renderer = new WebGLRenderer({ antialias: true, powerPreference: "low-power" });
  } catch (error) {
    return false;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = PCFShadowMap;
  host.appendChild(renderer.domElement);

  const colors = {
    anthracite: token("--color-anthracite"),
    bronze: token("--color-bronze"),
    cement: token("--color-cement"),
    white: token("--color-white"),
  };

  const scene = new Scene();
  scene.background = colors.white;
  scene.fog = new Fog(colors.white, 90, 190);

  const ground = new Mesh(new PlaneGeometry(400, 400), new MeshStandardMaterial({ color: colors.white, roughness: 1 }));
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.26;
  ground.receiveShadow = true;
  scene.add(ground);

  const works = buildWorks(colors);
  scene.add(works.footings, works.slab, works.axes, works.dims, ...works.frames, works.purlins,
    works.walls, works.roof, works.office, works.glazing);

  // Luz de tarde desde la derecha: una cara iluminada y otra en sombra, para leer el volumen.
  scene.add(new HemisphereLight(colors.white, colors.cement, 1.1));
  const sun = new DirectionalLight(colors.white, 3.4);
  sun.position.set(22, 30, 18);
  sun.castShadow = true;
  const shadowSize = host.clientWidth > 900 ? 2048 : 1024;
  sun.shadow.mapSize.set(shadowSize, shadowSize);
  Object.assign(sun.shadow.camera, { left: -26, right: 26, top: 26, bottom: -26, near: 1, far: 100 });
  sun.shadow.bias = -0.0006;
  scene.add(sun);

  const camera = new PerspectiveCamera(30, 1, 1, 400);
  let distance = 60;
  const center = { x: -1, z: 2.5 };

  const fit = () => {
    const width = host.clientWidth;
    const height = host.clientHeight;
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    const tan = Math.tan((camera.fov * Math.PI) / 360);
    // Que entren la nave, las oficinas, los ejes y la cota, también en pantallas angostas.
    distance = Math.max(14 / tan, 15 / (tan * camera.aspect));
    camera.updateProjectionMatrix();
  };

  const progress = () => {
    const rect = hero.getBoundingClientRect();
    const stickTop = parseFloat(getComputedStyle(pin).top) || 0;
    const travel = rect.height - pin.offsetHeight;
    return travel > 0 ? clamp01((stickTop - rect.top) / travel) : 1;
  };

  const draw = (t, look) => {
    const turn = ease(span(t, 0.06, 0.72));
    const phi = lerp(0.06, 1.08, turn) + look.y * 0.05 * turn;
    const theta = lerp(0, -0.6, ease(span(t, 0.06, 0.96))) + look.x * 0.08;
    const r = lerp(distance * 0.9, distance * 1.02, turn);
    const targetY = lerp(0, 3, turn);
    camera.position.set(
      center.x + r * Math.sin(phi) * Math.sin(theta),
      targetY + r * Math.cos(phi),
      center.z + r * Math.sin(phi) * Math.cos(theta),
    );
    camera.lookAt(center.x, targetY, center.z);

    // Fundaciones
    works.footings.scale.y = lerp(0.05, 1, ease(span(t, 0.08, 0.2)));
    works.slab.scale.y = lerp(0.05, 1, ease(span(t, 0.12, 0.24)));
    // Estructura: los marcos suben uno por uno; después las correas.
    works.frames.forEach((frame, i) => {
      const rise = ease(span(t, 0.22 + i * 0.03, 0.32 + i * 0.03));
      frame.visible = rise > 0; // sin esto, las vigas acostadas se verían en el plano
      frame.scale.y = Math.max(0.02, rise);
    });
    const purlins = ease(span(t, 0.42, 0.52));
    works.purlins.visible = purlins > 0;
    works.purlins.scale.x = Math.max(0.001, purlins);
    works.office.scale.y = lerp(0.02, 1, ease(span(t, 0.36, 0.56)));
    // Cerramientos y cubierta
    works.walls.scale.y = lerp(0.02, 1, ease(span(t, 0.5, 0.68)));
    const roofIn = ease(span(t, 0.64, 0.8));
    works.roof.visible = roofIn > 0;
    works.roof.position.y = (1 - roofIn) * 5;
    // Entrega: fachada vidriada y luces encendidas (bronce cálido).
    const glassIn = span(t, 0.76, 0.88);
    works.glazing.visible = glassIn > 0;
    works.glassMat.opacity = lerp(0.5, 0.85, span(t, 0.84, 1)) * glassIn;
    works.glassMat.emissiveIntensity = 0.5 * ease(span(t, 0.86, 1));

    const linesOut = 1 - 0.8 * span(t, 0.6, 0.92);
    works.lineMat.opacity = linesOut;
    works.dimMat.opacity = linesOut;

    renderer.render(scene, camera);
  };

  // Etapas con su servicio (texto en la plantilla) y avance en %.
  const counter = hero.querySelector("[data-progress]");
  const stages = Array.prototype.slice.call(hero.querySelectorAll("[data-stages] > li"));
  const caption = (t) => {
    if (counter) counter.textContent = String(Math.round(t * 100));
    let active = 0;
    stages.forEach((stage, i) => {
      if (t >= parseFloat(stage.getAttribute("data-at"))) active = i;
    });
    stages.forEach((stage, i) => stage.classList.toggle("is-active", i === active));
  };

  // Inercia: lo que se dibuja persigue al scroll y al mouse, como una cámara en riel.
  const shown = { t: progress(), x: 0, y: 0 };
  const target = { t: shown.t, x: 0, y: 0 };
  let running = false;

  const frame = () => {
    shown.t += (target.t - shown.t) * 0.14;
    shown.x += (target.x - shown.x) * 0.08;
    shown.y += (target.y - shown.y) * 0.08;
    draw(shown.t, shown);
    caption(shown.t);
    const settled = Math.abs(target.t - shown.t) < 0.0005
      && Math.abs(target.x - shown.x) < 0.001
      && Math.abs(target.y - shown.y) < 0.001;
    running = !settled;
    if (running) window.requestAnimationFrame(frame);
  };
  const wake = () => {
    if (!running) {
      running = true;
      window.requestAnimationFrame(frame);
    }
  };

  fit();
  draw(shown.t, shown);
  caption(shown.t);
  hero.classList.add("is-3d");

  window.addEventListener("scroll", () => {
    target.t = progress();
    wake();
  }, { passive: true });

  // Órbita sutil con el mouse, solo con puntero fino (computador) y con la portada a la vista.
  if (window.matchMedia("(pointer: fine)").matches) {
    window.addEventListener("pointermove", (event) => {
      const rect = hero.getBoundingClientRect();
      if (rect.bottom < 0 || rect.top > window.innerHeight) return;
      target.x = (event.clientX / window.innerWidth) * 2 - 1;
      target.y = (event.clientY / window.innerHeight) * 2 - 1;
      wake();
    }, { passive: true });
  }

  const refit = () => { fit(); draw(shown.t, shown); };
  if ("ResizeObserver" in window) {
    new ResizeObserver(refit).observe(host);
  } else {
    window.addEventListener("resize", refit);
  }
  return true;
}
