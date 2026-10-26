/* Exporta la casa terminada (avance 1) a GLB, con la cámara del final, para renderizarla
   fotorrealista en Blender (tools/render-final.py). Se compila aparte con esbuild y se
   abre en un navegador: window.exportScene() devuelve { glb (base64), camera }.
   No se publica en la web. */
import { Color, Group, Matrix4, Mesh, Vector3 } from "three";
import { GLTFExporter } from "three/examples/jsm/exporters/GLTFExporter.js";
import { applyProgress, buildHouse, cameraPose } from "../src/v2-hero3d.js";

const TOKENS = { anthracite: "#2C3539", bronze: "#B57949", cement: "#A9ABB6", white: "#FFFFFF" };

/* Blender no lee mallas instanciadas: cada pieza visible pasa a ser una malla propia,
   con su color de instancia (tono de madera o de follaje) en userData. */
function expandInstances(root) {
  const instanced = [];
  root.traverse((object) => { if (object.isInstancedMesh) instanced.push(object); });
  const matrix = new Matrix4();
  const scale = new Vector3();
  const color = new Color();
  for (const mesh of instanced) {
    const group = new Group();
    group.name = mesh.material.name;
    for (let i = 0; i < mesh.count; i += 1) {
      mesh.getMatrixAt(i, matrix);
      scale.setFromMatrixScale(matrix);
      if (scale.x * scale.y * scale.z < 1e-6 || !mesh.visible) continue;
      const piece = new Mesh(mesh.geometry, mesh.material);
      piece.applyMatrix4(matrix);
      if (mesh.instanceColor) {
        mesh.getColorAt(i, color);
        piece.userData.tint = `#${color.getHexString()}`;
      }
      group.add(piece);
    }
    mesh.parent.add(group);
    mesh.parent.remove(mesh);
  }
}

window.exportScene = async () => {
  const colors = Object.fromEntries(Object.entries(TOKENS).map(([k, v]) => [k, new Color(v)]));
  const house = buildHouse(colors);
  applyProgress(house, 1);
  const root = new Group();
  root.add(house.footings.mesh.parent, house.slab, house.structure, house.walls, house.doorLeaf, house.roof,
    house.interior, house.glass, house.frames, house.cladding.mesh.parent, house.deck, house.pool,
    house.stones.mesh.parent, house.garden);
  root.updateMatrixWorld(true);
  expandInstances(root);
  const glb = await new GLTFExporter().parseAsync(root, { binary: true, onlyVisible: true });
  const bytes = new Uint8Array(glb);
  let binary = "";
  for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return { glb: btoa(binary), camera: cameraPose(1) };
};
