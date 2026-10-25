/* SCHOBRAS.CL /v2/: portada 3D "del plano a la obra" (three.js, compilado con esbuild:
   `npm run build` en frontend/ genera static/js/v2-hero3d.min.js).
   Es la casa de la planta SVG de la portada: 12,00 × 8,00 m, ejes A–G cada 2 m.
   Arranca vista desde arriba (el plano) y con el scroll la cámara baja y la obra
   avanza: pilares, muros, techumbre y, al final, las ventanas encendidas. La cámara
   sigue al scroll con inercia y, en computador, orbita apenas con el mouse.
   Los colores salen de los tokens de site.css. */
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

const WALL_H = 2.6;
const RIDGE_H = 5.6;
const OUTER = 0.24;
const INNER = 0.14;

const clamp01 = (v) => Math.min(1, Math.max(0, v));
const span = (t, a, b) => clamp01((t - a) / (b - a));
const ease = (x) => x * x * (3 - 2 * x);
const lerp = (a, b, x) => a + (b - a) * x;

function token(name) {
  return new Color(getComputedStyle(document.documentElement).getPropertyValue(name).trim());
}

/* Un muro recto con sus vanos: tramos llenos, antepechos y dinteles. */
function wall(group, material, { axis, from, to, at, thickness, openings = [] }) {
  const piece = (a, b, y0, y1) => {
    if (b - a < 0.001 || y1 - y0 < 0.001) return;
    const length = b - a;
    const height = y1 - y0;
    const geometry = axis === "x"
      ? new BoxGeometry(length, height, thickness)
      : new BoxGeometry(thickness, height, length);
    const mesh = new Mesh(geometry, material);
    const middle = (a + b) / 2;
    mesh.position.set(axis === "x" ? middle : at, (y0 + y1) / 2, axis === "x" ? at : middle);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    group.add(mesh);
  };
  let cursor = from;
  for (const opening of openings) {
    piece(cursor, opening.a, 0, WALL_H);
    piece(opening.a, opening.b, 0, opening.bottom);
    piece(opening.a, opening.b, opening.top, WALL_H);
    cursor = opening.b;
  }
  piece(cursor, to, 0, WALL_H);
}

function gable(group, material, z) {
  const shape = new Shape();
  shape.moveTo(-6, WALL_H);
  shape.lineTo(6, WALL_H);
  shape.lineTo(0, RIDGE_H);
  shape.closePath();
  const mesh = new Mesh(new ExtrudeGeometry(shape, { depth: OUTER, bevelEnabled: false }), material);
  mesh.position.z = z;
  mesh.castShadow = true;
  group.add(mesh);
}

function glass(group, material, { axis, a, b, at, bottom, top }) {
  const length = b - a;
  const geometry = axis === "x"
    ? new BoxGeometry(length, top - bottom, 0.04)
    : new BoxGeometry(0.04, top - bottom, length);
  const mesh = new Mesh(geometry, material);
  const middle = (a + b) / 2;
  mesh.position.set(axis === "x" ? middle : at, (bottom + top) / 2, axis === "x" ? at : middle);
  group.add(mesh);
}

function buildHouse(colors) {
  const wallMat = new MeshStandardMaterial({ color: colors.anthracite, roughness: 0.85 });
  const roofMat = new MeshStandardMaterial({ color: colors.anthracite, roughness: 0.6 });
  const glassMat = new MeshStandardMaterial({
    color: colors.cement, roughness: 0.15, metalness: 0.1, transparent: true,
    emissive: colors.bronze, emissiveIntensity: 0,
  });
  const pillarMat = new MeshStandardMaterial({ color: colors.bronze, roughness: 0.6 });
  const lineMat = new LineDashedMaterial({ color: colors.cement, dashSize: 0.45, gapSize: 0.25, transparent: true });
  const dimMat = new LineDashedMaterial({ color: colors.bronze, dashSize: 100, gapSize: 0, transparent: true });

  const window = { bottom: 0.9, top: 2.2 };
  const door = { bottom: 0, top: 2.1 };

  // Pilares en los ejes del perímetro: la estructura sube antes que los muros.
  const pillars = new Group();
  const pillarAt = (x, z) => {
    const mesh = new Mesh(new BoxGeometry(0.2, WALL_H, 0.2), pillarMat);
    mesh.position.set(x, WALL_H / 2, z);
    mesh.castShadow = true;
    pillars.add(mesh);
  };
  for (let x = -6; x <= 6; x += 2) {
    pillarAt(Math.max(-5.88, Math.min(5.88, x)), -3.88);
    pillarAt(Math.max(-5.88, Math.min(5.88, x)), 3.88);
  }
  pillarAt(-5.88, 0);
  pillarAt(5.88, 0);

  // Muros: suben juntos (escala vertical del grupo), con sus vanos en proporción.
  const walls = new Group();
  const zBack = -4 + OUTER / 2;
  const zFront = 4 - OUTER / 2;
  wall(walls, wallMat, { axis: "x", from: -6, to: 6, at: zBack, thickness: OUTER, openings: [{ a: 0.4, b: 4.8, ...window }] });
  wall(walls, wallMat, {
    axis: "x", from: -6, to: 6, at: zFront, thickness: OUTER,
    openings: [{ a: -4.8, b: -2.0, ...window }, { a: 2.4, b: 3.6, ...door }],
  });
  wall(walls, wallMat, { axis: "z", from: -3.76, to: 3.76, at: -6 + OUTER / 2, thickness: OUTER, openings: [{ a: -2, b: 1.2, ...window }] });
  wall(walls, wallMat, { axis: "z", from: -3.76, to: 3.76, at: 6 - OUTER / 2, thickness: OUTER });
  wall(walls, wallMat, { axis: "z", from: -3.76, to: 0.8, at: -1.12, thickness: INNER });
  wall(walls, wallMat, { axis: "x", from: -1.05, to: 5.76, at: 0.72, thickness: INNER, openings: [{ a: 3.2, b: 4.2, ...door }] });
  gable(walls, wallMat, -4);
  gable(walls, wallMat, 4 - OUTER);

  // Techumbre a dos aguas con alero de 0,50 m: llega desde arriba al final.
  const roof = new Group();
  const slope = Math.atan2(RIDGE_H - WALL_H, 6);
  const run = 6.5;
  const rise = run * Math.tan(slope);
  const length = Math.hypot(run, rise);
  for (const side of [-1, 1]) {
    const panel = new Mesh(new BoxGeometry(length, 0.18, 8.8), roofMat);
    panel.position.set((side * run) / 2, RIDGE_H - rise / 2 + 0.12, 0);
    panel.rotation.z = -side * slope;
    panel.castShadow = true;
    roof.add(panel);
  }

  // Ventanas
  const glazing = new Group();
  glass(glazing, glassMat, { axis: "x", a: 0.4, b: 4.8, at: zBack, ...window });
  glass(glazing, glassMat, { axis: "x", a: -4.8, b: -2.0, at: zFront, ...window });
  glass(glazing, glassMat, { axis: "z", a: -2, b: 1.2, at: -6 + OUTER / 2, ...window });

  // Losa: blanca arriba (el piso del plano), bronce en el canto (la fundación).
  const floorTop = new MeshStandardMaterial({ color: colors.white, roughness: 1 });
  const floorEdge = new MeshStandardMaterial({ color: colors.bronze, roughness: 0.75 });
  const slab = new Mesh(new BoxGeometry(12.2, 0.2, 8.2), [floorEdge, floorEdge, floorTop, floorTop, floorEdge, floorEdge]);
  slab.position.y = -0.1;
  slab.receiveShadow = true;

  // Ejes A–G y la cota de 12,00 en el suelo, como en el plano.
  const points = [];
  for (let x = -6; x <= 6; x += 2) points.push(x, 0.01, -7.2, x, 0.01, 7.2);
  const axesGeometry = new BufferGeometry();
  axesGeometry.setAttribute("position", new Float32BufferAttribute(points, 3));
  const axes = new LineSegments(axesGeometry, lineMat);
  axes.computeLineDistances();
  const dimGeometry = new BufferGeometry();
  dimGeometry.setAttribute("position", new Float32BufferAttribute([
    -6, 0.01, -5.6, 6, 0.01, -5.6,
    -6, 0.01, -5.1, -6, 0.01, -6.1,
    6, 0.01, -5.1, 6, 0.01, -6.1,
  ], 3));
  const dims = new LineSegments(dimGeometry, dimMat);
  dims.computeLineDistances();

  return { pillars, walls, roof, glazing, slab, axes, dims, glassMat, lineMat, dimMat };
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
  scene.fog = new Fog(colors.white, 45, 95);

  const ground = new Mesh(new PlaneGeometry(240, 240), new MeshStandardMaterial({ color: colors.white, roughness: 1 }));
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.2;
  ground.receiveShadow = true;
  scene.add(ground);

  const house = buildHouse(colors);
  scene.add(house.slab, house.axes, house.dims, house.pillars, house.walls, house.roof, house.glazing);

  // Luz de tarde desde la derecha: una cara iluminada y otra en sombra, para leer el volumen.
  scene.add(new HemisphereLight(colors.white, colors.cement, 1.1));
  const sun = new DirectionalLight(colors.white, 3.4);
  sun.position.set(11, 15, 9);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  sun.shadow.camera.left = -14;
  sun.shadow.camera.right = 14;
  sun.shadow.camera.top = 14;
  sun.shadow.camera.bottom = -14;
  sun.shadow.camera.near = 1;
  sun.shadow.camera.far = 60;
  sun.shadow.bias = -0.0006;
  scene.add(sun);

  const camera = new PerspectiveCamera(30, 1, 0.5, 200);
  let distance = 30;

  const fit = () => {
    const width = host.clientWidth;
    const height = host.clientHeight;
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    const tan = Math.tan((camera.fov * Math.PI) / 360);
    // Que entren la casa, los ejes y la cota, también en pantallas angostas.
    distance = Math.max(7.6 / tan, 8.4 / (tan * camera.aspect));
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
    const phi = lerp(0.06, 1.12, turn) + look.y * 0.05 * turn;
    const theta = lerp(0, -0.62, ease(span(t, 0.06, 0.96))) + look.x * 0.08;
    const r = lerp(distance * 0.86, distance * 1.06, turn);
    const targetY = lerp(0, 1.4, turn);
    camera.position.set(
      r * Math.sin(phi) * Math.sin(theta),
      targetY + r * Math.cos(phi),
      r * Math.sin(phi) * Math.cos(theta),
    );
    camera.lookAt(0, targetY, 0);

    house.pillars.scale.y = lerp(0.02, 1, ease(span(t, 0.1, 0.32)));
    house.walls.scale.y = lerp(0.02, 1, ease(span(t, 0.26, 0.6)));

    // La techumbre baja como una pieza montada, sólida (sin transparencias).
    const roofIn = ease(span(t, 0.58, 0.8));
    house.roof.visible = roofIn > 0;
    house.roof.position.y = (1 - roofIn) * 3;

    // Remate: las ventanas se encienden con un brillo cálido (bronce).
    const glassIn = span(t, 0.76, 0.9);
    house.glazing.visible = glassIn > 0;
    house.glassMat.opacity = lerp(0.55, 0.92, span(t, 0.86, 1)) * glassIn;
    house.glassMat.emissiveIntensity = 0.95 * ease(span(t, 0.86, 1));

    const linesOut = 1 - 0.8 * span(t, 0.6, 0.92);
    house.lineMat.opacity = linesOut;
    house.dimMat.opacity = linesOut;

    renderer.render(scene, camera);
  };

  // Inercia: lo que se dibuja persigue al scroll y al mouse, como una cámara en riel.
  const counter = hero.querySelector("[data-progress]");
  const shown = { t: progress(), x: 0, y: 0 };
  const target = { t: shown.t, x: 0, y: 0 };
  let running = false;

  const frame = () => {
    shown.t += (target.t - shown.t) * 0.14;
    shown.x += (target.x - shown.x) * 0.08;
    shown.y += (target.y - shown.y) * 0.08;
    draw(shown.t, shown);
    if (counter) counter.textContent = String(Math.round(shown.t * 100));
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
  if (counter) counter.textContent = String(Math.round(shown.t * 100));
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
