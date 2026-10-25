/* SCHOBRAS.CL, inicio: portada 3D "del plano a la obra" (three.js, compilado con esbuild:
   `npm run build` en frontend/ genera static/js/v2-hero3d.min.js).
   Una casa de un piso en forma de L, como una maqueta de arquitectura: volumen social
   blanco con fachada vidriada, ala de dormitorios revestida en listones de madera,
   terraza, piscina y árboles de maqueta, sobre un tablero. Es distinta de la casa del
   Proceso (dos pisos, en elevación). Arranca vista desde arriba (el plano) y con el
   scroll la cámara baja y la obra avanza por etapas: fundaciones, estructura,
   cerramientos y entrega (terminaciones, jardín y luces encendidas). Cada etapa muestra
   un servicio (lista [data-stages] de la plantilla). La cámara sigue al scroll con
   inercia y, en computador, orbita apenas con el mouse. Los colores salen de los tokens
   de site.css. */
import {
  BoxGeometry,
  BufferGeometry,
  Color,
  CylinderGeometry,
  DirectionalLight,
  Float32BufferAttribute,
  Fog,
  Group,
  HemisphereLight,
  IcosahedronGeometry,
  InstancedMesh,
  LineBasicMaterial,
  LineDashedMaterial,
  LineSegments,
  Mesh,
  MeshStandardMaterial,
  NeutralToneMapping,
  Object3D,
  PCFShadowMap,
  PerspectiveCamera,
  PlaneGeometry,
  PMREMGenerator,
  Scene,
  WebGLRenderer,
} from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";

const BASE = 0.3;      // radier: la casa se apoya 30 cm sobre el terreno
const T = 0.2;         // espesor de muros
const SOCIAL = { x0: -8, x1: 3, z0: -4, z1: 3, h: 3.1 };   // estar, comedor y cocina (11 × 7 m)
const PRIVATE = { x0: 3, x1: 9, z0: -4, z1: 7, h: 2.7 };   // dormitorios (6 × 11 m)
const POOL = { x0: -7, x1: 1, z0: 9, z1: 11.4 };
const DECK = { x0: -8, x1: 3, z0: 3, z1: 7.5 };
const POSTER_ASPECT = 0.8; // imagen fija de la portada: 4:5 (ancho:alto)

const clamp01 = (v) => Math.min(1, Math.max(0, v));
const span = (t, a, b) => clamp01((t - a) / (b - a));
const ease = (x) => x * x * (3 - 2 * x);
const lerp = (a, b, x) => a + (b - a) * x;

function token(name) {
  return new Color(getComputedStyle(document.documentElement).getPropertyValue(name).trim());
}

function mix(a, b, amount) {
  return a.clone().lerp(b, amount);
}

function box(parent, material, size, position, { shadow = true } = {}) {
  const mesh = new Mesh(new BoxGeometry(...size), material);
  mesh.position.set(...position);
  mesh.castShadow = shadow;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

/* Piezas que aparecen una tras otra (listones, pilares, árboles): una sola malla
   instanciada; cada pieza crece desde su base a lo largo de `axis`. */
class Sequence {
  constructor(parent, geometry, material, items, { axis = "y", colors = null, shadow = true } = {}) {
    this.items = items;
    this.axis = axis;
    this.mesh = new InstancedMesh(geometry, material, items.length);
    this.mesh.castShadow = shadow;
    this.mesh.receiveShadow = true;
    if (colors) items.forEach((_, i) => this.mesh.setColorAt(i, colors(i)));
    this.dummy = new Object3D();
    this.last = -1;
    parent.add(this.mesh);
  }

  update(t, a, b, each) {
    if (t === this.last) return;
    this.last = t;
    const n = this.items.length;
    const step = n > 1 ? (b - a - each) / (n - 1) : 0;
    const dummy = this.dummy;
    let shown = false;
    this.items.forEach((item, i) => {
      const k = ease(span(t, a + step * i, a + step * i + each));
      const [w, h, d] = item.size;
      dummy.position.set(...item.position);
      dummy.scale.set(w, h, d);
      if (k <= 0) dummy.scale.set(0, 0, 0); // ni una línea ni una sombra antes de tiempo
      shown = shown || k > 0;
      if (this.axis === "y") {
        dummy.scale.y = Math.max(1e-4, h * k);
        dummy.position.y = item.position[1] - h / 2 + (h * k) / 2;
      } else if (this.axis === "x") {
        dummy.scale.x = Math.max(1e-4, w * k);
        dummy.position.x = item.position[0] - w / 2 + (w * k) / 2;
      } else {
        dummy.scale.multiplyScalar(Math.max(1e-4, k));
      }
      dummy.updateMatrix();
      this.mesh.setMatrixAt(i, dummy.matrix);
    });
    this.mesh.instanceMatrix.needsUpdate = true;
    this.mesh.visible = shown;
  }
}

/* Muro recto con sus vanos (tramos llenos, antepechos y dinteles). Devuelve los vanos
   con su posición, para ponerles vidrio y marco. */
function wall(group, material, { axis, from, to, at, height, openings = [] }) {
  const piece = (a, b, y0, y1) => {
    if (b - a < 0.001 || y1 - y0 < 0.001) return;
    const middle = (a + b) / 2;
    const size = axis === "x" ? [b - a, y1 - y0, T] : [T, y1 - y0, b - a];
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
  return openings.map((opening) => ({ ...opening, axis, at }));
}

/* Vidrio y marco de aluminio antracita en un vano; montantes cada 1,6 m como máximo. */
function glaze(glass, frames, glassMat, frameMat, opening) {
  const { axis, at, a, b, bottom, top } = opening;
  const width = b - a;
  const height = top - bottom;
  const middle = (a + b) / 2;
  const y = (bottom + top) / 2;
  const along = (u, v) => (axis === "x" ? [u, v, at] : [at, v, u]);
  const dims = (alongSize, h, depth) => (axis === "x" ? [alongSize, h, depth] : [depth, h, alongSize]);
  box(glass, glassMat, dims(width, height, 0.03), along(middle, y), { shadow: false });
  const bar = 0.06;
  box(frames, frameMat, dims(width, bar, 0.1), along(middle, bottom + bar / 2));
  box(frames, frameMat, dims(width, bar, 0.1), along(middle, top - bar / 2));
  const panes = Math.max(1, Math.ceil(width / 1.6));
  for (let i = 0; i <= panes; i += 1) {
    box(frames, frameMat, dims(bar, height, 0.1), along(a + (width * i) / panes, y));
  }
}

function lines(points, material) {
  const geometry = new BufferGeometry();
  geometry.setAttribute("position", new Float32BufferAttribute(points, 3));
  const segments = new LineSegments(geometry, material);
  segments.computeLineDistances();
  return segments;
}

function rectangle(x0, z0, x1, z1, y = 0.012) {
  return [x0, y, z0, x1, y, z0, x1, y, z0, x1, y, z1, x1, y, z1, x0, y, z1, x0, y, z1, x0, y, z0];
}

/* Listones verticales de madera en una cara, saltando los vanos. */
function slats(items, { axis, from, to, at, height, skip = [] }) {
  const pitch = 0.15;
  for (let u = from + pitch / 2; u < to; u += pitch) {
    if (skip.some(([a, b]) => u > a - 0.05 && u < b + 0.05)) continue;
    const position = axis === "x" ? [u, BASE + height / 2, at] : [at, BASE + height / 2, u];
    const size = axis === "x" ? [0.075, height, 0.05] : [0.05, height, 0.075];
    items.push({ position, size });
  }
}

function buildHouse(colors) {
  const plaster = new MeshStandardMaterial({ color: colors.white, roughness: 0.92 });
  const concrete = new MeshStandardMaterial({ color: colors.cement, roughness: 0.95 });
  const roofMat = new MeshStandardMaterial({ color: mix(colors.white, colors.cement, 0.14), roughness: 0.95 });
  const wood = new MeshStandardMaterial({ color: colors.white, roughness: 0.62 });
  const deckWood = new MeshStandardMaterial({ color: mix(colors.bronze, colors.white, 0.12), roughness: 0.7 });
  const frameMat = new MeshStandardMaterial({ color: colors.anthracite, roughness: 0.45, metalness: 0.4 });
  const glassMat = new MeshStandardMaterial({
    color: mix(colors.anthracite, colors.cement, 0.35), roughness: 0.04, metalness: 0.6,
    transparent: true, opacity: 0, depthWrite: false,
  });
  const glowMat = new MeshStandardMaterial({
    color: mix(colors.white, colors.cement, 0.25), roughness: 1,
    emissive: mix(colors.bronze, colors.white, 0.45), emissiveIntensity: 0,
  });
  const water = new MeshStandardMaterial({ color: mix(colors.cement, colors.anthracite, 0.6), roughness: 0.03, metalness: 0.7 });
  const canopy = new MeshStandardMaterial({ color: mix(colors.cement, colors.white, 0.5), roughness: 0.85, flatShading: true });
  const trunkMat = new MeshStandardMaterial({ color: colors.anthracite, roughness: 0.8 });
  const planMat = new LineBasicMaterial({ color: colors.anthracite, transparent: true });
  const axisMat = new LineDashedMaterial({ color: colors.cement, dashSize: 0.5, gapSize: 0.35, transparent: true });
  const dimMat = new LineBasicMaterial({ color: colors.bronze, transparent: true });
  // Madera: cada listón con un tono apenas distinto, como tablas reales.
  const woodTone = (i) => mix(colors.bronze, i % 3 ? colors.anthracite : colors.white, ((i * 37) % 11) / 90);

  // ── Plano en el tablero: muros, ejes y cotas ──
  const plan = new Group();
  const wallLines = [];
  for (const v of [SOCIAL, PRIVATE]) {
    wallLines.push(...rectangle(v.x0, v.z0, v.x1, v.z1), ...rectangle(v.x0 + T, v.z0 + T, v.x1 - T, v.z1 - T));
  }
  wallLines.push(...rectangle(DECK.x0, DECK.z1, DECK.x1, DECK.z0), ...rectangle(POOL.x0, POOL.z0, POOL.x1, POOL.z1));
  const axisLines = [];
  for (const x of [-8, -2.5, 3, 9]) axisLines.push(x, 0.01, -7, x, 0.01, 13);
  for (const z of [-4, 3, 7]) axisLines.push(-11, 0.01, z, 12, 0.01, z);
  plan.add(lines(wallLines, planMat), lines(axisLines, axisMat), lines([
    -8, 0.012, -6, 9, 0.012, -6, -8, 0.012, -5.5, -8, 0.012, -6.5, 9, 0.012, -5.5, 9, 0.012, -6.5,
    11, 0.012, -4, 11, 0.012, 7, 10.5, 0.012, -4, 11.5, 0.012, -4, 10.5, 0.012, 7, 11.5, 0.012, 7,
  ], dimMat));

  // ── Fundaciones: cimientos corridos bajo los muros y el radier ──
  const footingItems = [];
  for (const v of [SOCIAL, PRIVATE]) {
    footingItems.push({ position: [(v.x0 + v.x1) / 2, BASE / 2, v.z0 + T / 2], size: [v.x1 - v.x0, BASE, 0.5] });
    footingItems.push({ position: [(v.x0 + v.x1) / 2, BASE / 2, v.z1 - T / 2], size: [v.x1 - v.x0, BASE, 0.5] });
    footingItems.push({ position: [v.x0 + T / 2, BASE / 2, (v.z0 + v.z1) / 2], size: [0.5, BASE, v.z1 - v.z0] });
    footingItems.push({ position: [v.x1 - T / 2, BASE / 2, (v.z0 + v.z1) / 2], size: [0.5, BASE, v.z1 - v.z0] });
  }
  const footings = new Sequence(new Group(), new BoxGeometry(1, 1, 1), concrete, footingItems);
  const slab = new Group();
  box(slab, concrete, [SOCIAL.x1 - SOCIAL.x0, BASE, SOCIAL.z1 - SOCIAL.z0], [(SOCIAL.x0 + SOCIAL.x1) / 2, BASE / 2, (SOCIAL.z0 + SOCIAL.z1) / 2]);
  box(slab, concrete, [PRIVATE.x1 - PRIVATE.x0, BASE, PRIVATE.z1 - PRIVATE.z0], [(PRIVATE.x0 + PRIVATE.x1) / 2, BASE / 2, (PRIVATE.z0 + PRIVATE.z1) / 2]);

  // ── Estructura: pilares que suben uno por uno y las cadenas sobre ellos ──
  const columnItems = [];
  const column = (x, z, h) => columnItems.push({ position: [x, BASE + h / 2, z], size: [0.18, h, 0.18] });
  for (const x of [-7.9, -2.5, 2.9]) for (const z of [-3.9, 2.9]) column(x, z, SOCIAL.h);
  for (const z of [-3.9, 1.5, 6.9]) for (const x of [3.1, 8.9]) column(x, z, PRIVATE.h);
  const structure = new Group();
  const columns = new Sequence(structure, new BoxGeometry(1, 1, 1), concrete, columnItems);
  const beamItems = [];
  for (const v of [SOCIAL, PRIVATE]) {
    const y = BASE + v.h - 0.15;
    beamItems.push({ position: [(v.x0 + v.x1) / 2, y, v.z0 + T / 2], size: [v.x1 - v.x0, 0.3, 0.18] });
    beamItems.push({ position: [(v.x0 + v.x1) / 2, y, v.z1 - T / 2], size: [v.x1 - v.x0, 0.3, 0.18] });
    beamItems.push({ position: [v.x0 + T / 2, y, (v.z0 + v.z1) / 2], size: [0.18, 0.3, v.z1 - v.z0] });
    beamItems.push({ position: [v.x1 - T / 2, y, (v.z0 + v.z1) / 2], size: [0.18, 0.3, v.z1 - v.z0] });
  }
  const beams = new Sequence(structure, new BoxGeometry(1, 1, 1), concrete, beamItems, { axis: "x" });

  // ── Cerramientos: muros con sus vanos ──
  const walls = new Group();
  walls.position.y = BASE;
  const s = SOCIAL;
  const p = PRIVATE;
  const openings = [
    ...wall(walls, plaster, { axis: "x", from: s.x0, to: s.x1, at: s.z0 + T / 2, height: s.h, openings: [{ a: -6, b: -1, bottom: 2.1, top: 2.75 }] }),
    ...wall(walls, plaster, { axis: "x", from: s.x0, to: s.x1, at: s.z1 - T / 2, height: s.h, openings: [{ a: -7.6, b: 2.6, bottom: 0, top: 2.75 }] }),
    ...wall(walls, plaster, { axis: "z", from: s.z0, to: s.z1, at: s.x0 + T / 2, height: s.h, openings: [{ a: -1.55, b: -0.45, bottom: 0, top: 2.3, door: true }, { a: 0.6, b: 2.4, bottom: 0.9, top: 2.3 }] }),
    ...wall(walls, plaster, { axis: "z", from: s.z0, to: s.z1, at: s.x1, height: s.h }),
    ...wall(walls, plaster, { axis: "x", from: p.x0, to: p.x1, at: p.z0 + T / 2, height: p.h }),
    ...wall(walls, plaster, { axis: "z", from: p.z0, to: p.z1, at: p.x1 - T / 2, height: p.h, openings: [{ a: 0, b: 2, bottom: 0.9, top: 2.2 }] }),
    ...wall(walls, plaster, { axis: "x", from: p.x0, to: p.x1, at: p.z1 - T / 2, height: p.h, openings: [{ a: 3.8, b: 8.2, bottom: 0.9, top: 2.2 }] }),
    ...wall(walls, plaster, { axis: "z", from: s.z1, to: p.z1, at: p.x0 + T / 2, height: p.h, openings: [{ a: 3.5, b: 6.5, bottom: 0, top: 2.3 }] }),
  ];
  // Puerta de entrada (madera) en la cara poniente del volumen social.
  const doorLeaf = new Group();
  doorLeaf.position.y = BASE;
  box(doorLeaf, deckWood, [0.08, 2.3, 1.1], [s.x0 + T / 2, 1.15, -1]);

  // Losas de techo con un canto antracita, que bajan al final de los cerramientos.
  const roof = new Group();
  for (const [v, front] of [[SOCIAL, 0.9], [PRIVATE, 0.4]]) {
    const x0 = v.x0 - 0.5;
    const x1 = v === SOCIAL ? v.x1 + 0.2 : v.x1 + 0.4;
    const z0 = v.z0 - 0.4;
    const z1 = v.z1 + front;
    const top = BASE + v.h + 0.3;
    box(roof, roofMat, [x1 - x0, 0.26, z1 - z0], [(x0 + x1) / 2, top - 0.13, (z0 + z1) / 2]);
    box(roof, frameMat, [x1 - x0 + 0.02, 0.05, z1 - z0 + 0.02], [(x0 + x1) / 2, top - 0.27, (z0 + z1) / 2]);
  }

  // ── Entrega: vidrios, madera, terraza, piscina, jardín y luces ──
  const glass = new Group();
  const frames = new Group();
  glass.position.y = BASE;
  frames.position.y = BASE;
  for (const opening of openings) if (!opening.door) glaze(glass, frames, glassMat, frameMat, opening);

  // Interior: un piso de madera y muros del fondo que se encienden (luz cálida).
  const interior = new Group();
  const floorMat = new MeshStandardMaterial({ color: mix(colors.bronze, colors.white, 0.3), roughness: 0.7 });
  box(interior, floorMat, [s.x1 - s.x0 - 2 * T, 0.02, s.z1 - s.z0 - 2 * T], [(s.x0 + s.x1) / 2, BASE + 0.01, (s.z0 + s.z1) / 2], { shadow: false });
  box(interior, floorMat, [p.x1 - p.x0 - 2 * T, 0.02, p.z1 - p.z0 - 2 * T], [(p.x0 + p.x1) / 2, BASE + 0.01, (p.z0 + p.z1) / 2], { shadow: false });
  box(interior, glowMat, [s.x1 - s.x0 - 2 * T - 0.1, s.h - 0.05, 0.02], [(s.x0 + s.x1) / 2, BASE + s.h / 2, s.z0 + T + 0.03], { shadow: false });
  box(interior, glowMat, [0.02, p.h - 0.05, p.z1 - p.z0 - 2 * T - 0.1], [p.x1 - T - 0.03, BASE + p.h / 2, (p.z0 + p.z1) / 2], { shadow: false });
  box(interior, glowMat, [0.02, s.h - 0.05, s.z1 - s.z0 - 2 * T - 0.1], [s.x1 - T / 2 - 0.13, BASE + s.h / 2, (s.z0 + s.z1) / 2], { shadow: false });

  const cladItems = [];
  slats(cladItems, { axis: "z", from: p.z0, to: p.z1, at: p.x0 - 0.03, height: p.h, skip: [[s.z0, s.z1 + 0.05], [3.5, 6.5]] });
  slats(cladItems, { axis: "x", from: p.x0, to: p.x1 + 0.05, at: p.z1 + 0.03, height: p.h, skip: [[3.8, 8.2]] });
  slats(cladItems, { axis: "z", from: p.z0, to: p.z1 + 0.05, at: p.x1 + 0.03, height: p.h, skip: [[0, 2]] });
  slats(cladItems, { axis: "x", from: p.x0, to: p.x1 + 0.05, at: p.z0 - 0.03, height: p.h });
  const cladding = new Sequence(new Group(), new BoxGeometry(1, 1, 1), wood, cladItems, { colors: woodTone });

  const deck = new Group();
  box(deck, concrete, [DECK.x1 - DECK.x0, BASE - 0.06, DECK.z1 - DECK.z0], [(DECK.x0 + DECK.x1) / 2, (BASE - 0.06) / 2, (DECK.z0 + DECK.z1) / 2], { shadow: false });
  const deckItems = [];
  for (let z = DECK.z0 + 0.08; z < DECK.z1; z += 0.16) {
    deckItems.push({ position: [(DECK.x0 + DECK.x1) / 2, BASE - 0.03, z], size: [DECK.x1 - DECK.x0, 0.06, 0.13] });
  }
  const deckBoards = new Sequence(deck, new BoxGeometry(1, 1, 1), wood, deckItems, {
    axis: "x", colors: woodTone,
  });

  const pool = new Group();
  const coping = 0.3;
  box(pool, plaster, [POOL.x1 - POOL.x0 + 2 * coping, 0.14, coping], [(POOL.x0 + POOL.x1) / 2, 0.07, POOL.z0 - coping / 2]);
  box(pool, plaster, [POOL.x1 - POOL.x0 + 2 * coping, 0.14, coping], [(POOL.x0 + POOL.x1) / 2, 0.07, POOL.z1 + coping / 2]);
  box(pool, plaster, [coping, 0.14, POOL.z1 - POOL.z0], [POOL.x0 - coping / 2, 0.07, (POOL.z0 + POOL.z1) / 2]);
  box(pool, plaster, [coping, 0.14, POOL.z1 - POOL.z0], [POOL.x1 + coping / 2, 0.07, (POOL.z0 + POOL.z1) / 2]);
  const waterMesh = box(pool, water, [POOL.x1 - POOL.x0, 0.08, POOL.z1 - POOL.z0], [(POOL.x0 + POOL.x1) / 2, 0.04, (POOL.z0 + POOL.z1) / 2], { shadow: false });
  // Camino de piedras hasta la puerta.
  const stoneItems = [];
  for (let x = -14.2; x < -8.4; x += 1.05) stoneItems.push({ position: [x, 0.03, -1 + ((x * 7) % 2) * 0.08], size: [0.8, 0.06, 0.55] });
  for (let z = 7.9; z < 9; z += 0.95) stoneItems.push({ position: [-2.5, 0.03, z], size: [0.55, 0.06, 0.8] });
  const stones = new Sequence(new Group(), new BoxGeometry(1, 1, 1), concrete, stoneItems, { axis: "all" });

  // Árboles y arbustos de maqueta: copas facetadas sobre troncos finos.
  const treeSpots = [
    [-12, -6.5, 1.6], [-11.6, 8.6, 1.25], [12.8, -6.2, 1.8], [13.2, 9.8, 1.35],
    [6.4, 12.6, 1.05], [-0.8, -7.6, 1.15], [-13.4, 12.8, 0.95], [10.9, 2.8, 0.9],
  ];
  const trunkItems = treeSpots.map(([x, z, r]) => ({ position: [x, r * 0.7, z], size: [1, r * 1.4, 1] }));
  const crownItems = treeSpots.map(([x, z, r]) => ({ position: [x, r * 1.4 + r * 0.75, z], size: [r, r * 1.05, r] }));
  for (const [x, z] of [[-9.1, 4.2], [-9.2, 5.6], [-9.0, 7.0], [4.2, 8.2], [5.6, 8.3], [9.9, -2.6]]) {
    crownItems.push({ position: [x, 0.42, z], size: [0.48, 0.42, 0.48] });
  }
  const garden = new Group();
  const trunks = new Sequence(garden, new CylinderGeometry(0.07, 0.1, 1, 6), trunkMat, trunkItems);
  const crowns = new Sequence(garden, new IcosahedronGeometry(1, 1), canopy, crownItems, { axis: "all" });

  return {
    plan, footings, slab, structure, columns, beams, walls, doorLeaf, roof, glass, frames, interior,
    cladding, deck, deckBoards, pool, waterMesh, stones, garden, trunks, crowns,
    glassMat, glowMat, planMat, axisMat, dimMat,
  };
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
  renderer.toneMapping = NeutralToneMapping;
  host.appendChild(renderer.domElement);

  const colors = {
    anthracite: token("--color-anthracite"),
    bronze: token("--color-bronze"),
    cement: token("--color-cement"),
    white: token("--color-white"),
  };

  const scene = new Scene();
  scene.background = colors.white;
  scene.fog = new Fog(colors.white, 70, 170);
  // Reflejos suaves de un estudio: dan brillo a vidrios, agua y aluminio.
  const pmrem = new PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.4;
  pmrem.dispose();

  // Tablero de la maqueta.
  const boardMat = new MeshStandardMaterial({ color: mix(colors.white, colors.cement, 0.3), roughness: 1 });
  const board = new Mesh(new BoxGeometry(32, 0.8, 27), [
    new MeshStandardMaterial({ color: colors.cement, roughness: 1 }),
    new MeshStandardMaterial({ color: colors.cement, roughness: 1 }),
    boardMat,
    boardMat,
    new MeshStandardMaterial({ color: colors.cement, roughness: 1 }),
    new MeshStandardMaterial({ color: colors.cement, roughness: 1 }),
  ]);
  board.position.set(0.5, -0.4, 3);
  board.receiveShadow = true;
  scene.add(board);
  const floor = new Mesh(new PlaneGeometry(400, 400), new MeshStandardMaterial({ color: colors.white, roughness: 1 }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.8;
  floor.receiveShadow = true;
  scene.add(floor);

  const house = buildHouse(colors);
  scene.add(house.plan, house.footings.mesh.parent, house.slab, house.structure, house.walls, house.doorLeaf,
    house.roof, house.interior, house.glass, house.frames, house.cladding.mesh.parent, house.deck, house.pool,
    house.stones.mesh.parent, house.garden);

  // Luz de tarde desde la derecha: una cara iluminada y otra en sombra, para leer el volumen.
  scene.add(new HemisphereLight(colors.white, colors.cement, 0.45));
  const sun = new DirectionalLight(colors.white, 2.6);
  sun.position.set(20, 28, 16);
  sun.castShadow = true;
  const shadowSize = host.clientWidth > 900 ? 2048 : 1024;
  sun.shadow.mapSize.set(shadowSize, shadowSize);
  Object.assign(sun.shadow.camera, { left: -20, right: 20, top: 20, bottom: -20, near: 1, far: 90 });
  sun.shadow.bias = -0.0005;
  sun.shadow.normalBias = 0.02;
  sun.shadow.radius = 3;
  scene.add(sun);

  const camera = new PerspectiveCamera(30, 1, 1, 400);
  let distance = 60;
  let opening = 60;
  const center = { x: 1.2, z: 3.4 };

  const fit = () => {
    const width = host.clientWidth;
    const height = host.clientHeight;
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    const tan = Math.tan((camera.fov * Math.PI) / 360);
    // Que entren la casa, la piscina y las cotas, también en pantallas angostas.
    distance = Math.max(10 / tan, 12 / (tan * camera.aspect));
    // Primer cuadro (el plano visto desde arriba): mismo encuadre que la imagen fija de
    // la portada (static/img/portada-plano.webp, 4:5, con object-fit: cover), para que el
    // cambio de la imagen a la escena no se note. Ancho visible fijo de 24 m (12 por lado).
    opening = (camera.aspect >= POSTER_ASPECT ? 12 / camera.aspect : 12 / POSTER_ASPECT) / tan;
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
    const phi = lerp(0.04, 1.02, turn) + look.y * 0.05 * turn;
    const theta = lerp(0, -0.62, ease(span(t, 0.06, 0.96))) + look.x * 0.08;
    const r = lerp(opening, distance * 1.1, turn);
    const targetY = lerp(0, 1.4, turn);
    camera.position.set(
      center.x + r * Math.sin(phi) * Math.sin(theta),
      targetY + r * Math.cos(phi),
      center.z + r * Math.sin(phi) * Math.cos(theta),
    );
    camera.lookAt(center.x, targetY, center.z);

    // Fundaciones: cimientos corridos y después el radier.
    house.footings.update(t, 0.08, 0.18, 0.04);
    const slabIn = ease(span(t, 0.15, 0.24));
    house.slab.visible = slabIn > 0;
    house.slab.scale.y = Math.max(0.01, slabIn);
    // Estructura: pilares uno por uno y las cadenas que los amarran.
    house.columns.update(t, 0.22, 0.4, 0.06);
    house.beams.update(t, 0.36, 0.5, 0.06);
    // Cerramientos: muros que se levantan y losas que bajan.
    const wallsIn = ease(span(t, 0.5, 0.66));
    house.walls.visible = wallsIn > 0;
    house.walls.scale.y = Math.max(0.01, wallsIn);
    house.doorLeaf.visible = wallsIn >= 1;
    const roofIn = ease(span(t, 0.62, 0.78));
    house.roof.visible = roofIn > 0;
    house.roof.position.y = (1 - roofIn) * 4;
    // Entrega: vidrios, madera, terraza, piscina, jardín y luces encendidas.
    const framesIn = ease(span(t, 0.76, 0.84));
    house.frames.visible = framesIn > 0;
    house.frames.scale.y = Math.max(0.01, framesIn);
    house.interior.visible = framesIn > 0;
    house.glassMat.opacity = 0.42 * span(t, 0.8, 0.88);
    house.glass.visible = house.glassMat.opacity > 0;
    house.cladding.update(t, 0.78, 0.92, 0.05);
    house.deck.visible = t > 0.8;
    house.deckBoards.update(t, 0.8, 0.9, 0.05);
    house.pool.visible = t > 0.82;
    const fill = ease(span(t, 0.84, 0.92));
    house.waterMesh.scale.y = Math.max(0.01, fill);
    house.waterMesh.position.y = 0.04 * fill;
    house.stones.update(t, 0.84, 0.92, 0.04);
    house.trunks.update(t, 0.86, 0.97, 0.05);
    house.crowns.update(t, 0.87, 0.99, 0.06);
    house.glowMat.emissiveIntensity = 1.4 * ease(span(t, 0.86, 0.97));

    const linesOut = 1 - span(t, 0.55, 0.85);
    house.plan.visible = linesOut > 0;
    house.planMat.opacity = linesOut;
    house.axisMat.opacity = linesOut;
    house.dimMat.opacity = linesOut;

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
