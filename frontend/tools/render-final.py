"""Render fotorrealista del final de la portada 3D (Blender 4.5, Cycles).

Toma la casa terminada que exporta tools/export-scene.js (GLB + pose de cámara) y la
renderiza con materiales reales, pasto, follaje, cielo físico y sol, desde la misma
cámara del final de la animación (4:5, campo vertical de 30°). El resultado se convierte
en static/img/portada-render-*.webp (ver docs/06-frontend/v2-direccion-artistica.md).

Uso:
  blender -b -P frontend/tools/render-final.py -- house.glb house.camera.json salida.png [ancho] [muestras] [carpeta]

[carpeta] (opcional) tiene los recursos CC0 de Poly Haven (polyhaven.com, dominio público):
  kloofendal_48d_partly_cloudy_puresky_2k.hdr   cielo real (sol a 48°, como la escena web)
  jacaranda/jacaranda_tree_1k.gltf (+ textures/) árbol escaneado (vecinos)
  tree_small_02/tree_small_02_1k.gltf             árbol de copa redonda (los del terreno)
  shrub_02/shrub_02_1k.gltf                       arbusto (jardineras y maceteros)
  grass/leafy_grass_{diff,nor_gl,rough}_2k.jpg   pasto fotográfico
Sin ella, cielo físico de Blender, árboles de racimos y pasto procedural. Los modelos
que falten se omiten (el jacarandá reemplaza al árbol redondo).

Referencia de Ariel (2026-10-25): foto aérea de una casa parecida al atardecer, con luz
dorada, interior amoblado y encendido, jardineras y pasto denso. La cámara y el rumbo
del sol no cambian: el render se funde con la escena 3D y las sombras deben calzar.
"""
import json
import math
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
GLB, CAMERA_JSON, OUT = args[0], args[1], args[2]
WIDTH = int(args[3]) if len(args) > 3 else 1440
SAMPLES = int(args[4]) if len(args) > 4 else 128
ASSETS = args[5] if len(args) > 5 else None
HEIGHT = round(WIDTH * 5 / 4)

# Mismo sol que la escena web (three.js: 20, 28, 16; Y hacia arriba).
SUN_THREE = Vector((20.0, 28.0, 16.0))


def to_blender(v):
    """three.js (Y arriba) → Blender (Z arriba), igual que el importador glTF."""
    return Vector((v[0], -v[2], v[1]))


def hex_rgb(value):
    value = value.lstrip("#")
    srgb = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


# ── Escena limpia ─────────────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=GLB)

# Color de instancia (tono de cada tabla o copa) → color del objeto, que lee el shader.
for obj in scene.objects:
    tint = obj.get("tint")
    if tint:
        obj.color = (*hex_rgb(tint), 1.0)


# ── Materiales ────────────────────────────────────────────────────────────
def principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    return mat, nodes, mat.node_tree.links, bsdf


def add_bump(nodes, links, bsdf, scale, strength, detail=8.0, kind="noise"):
    if kind == "noise":
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = scale
        tex.inputs["Detail"].default_value = detail
        out = tex.outputs["Fac"]
    else:
        tex = nodes.new("ShaderNodeTexVoronoi")
        tex.inputs["Scale"].default_value = scale
        out = tex.outputs["Distance"]
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    links.new(out, bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return tex


def color_ramp(nodes, links, fac, a, b, target):
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*a, 1)
    ramp.color_ramp.elements[1].color = (*b, 1)
    links.new(fac, ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], target)
    return ramp


def plaster():
    mat, nodes, links, bsdf = principled("plaster")
    bsdf.inputs["Base Color"].default_value = (0.86, 0.85, 0.82, 1)
    bsdf.inputs["Roughness"].default_value = 0.85
    add_bump(nodes, links, bsdf, 120, 0.08)
    return mat


def gravel():
    mat, nodes, links, bsdf = principled("roof")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 260
    noise.inputs["Detail"].default_value = 4
    # Mismo color que el techo de la escena web: antracita con 18 % de cemento (#42474F).
    color_ramp(nodes, links, noise.outputs["Fac"], (0.045, 0.052, 0.062), (0.075, 0.085, 0.1), bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    add_bump(nodes, links, bsdf, 300, 0.6, kind="voronoi")
    return mat


def concrete():
    mat, nodes, links, bsdf = principled("concrete")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 40
    color_ramp(nodes, links, noise.outputs["Fac"], (0.33, 0.33, 0.34), (0.47, 0.47, 0.48), bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    add_bump(nodes, links, bsdf, 200, 0.2)
    return mat


def wood(name, darken=1.0, base=None):
    """Madera con veta: bandas onduladas sobre el tono de cada tabla (color del objeto, o
    `base` fijo para las piezas sin tono propio: puerta y piso), sin cambiarle el color."""
    mat, nodes, links, bsdf = principled(name)
    if base:
        tone = nodes.new("ShaderNodeRGB")
        tone.outputs[0].default_value = (*base, 1)
        tone_out = tone.outputs[0]
    else:
        tone_out = nodes.new("ShaderNodeObjectInfo").outputs["Color"]
    wave = nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "Z"
    wave.inputs["Scale"].default_value = 18
    wave.inputs["Distortion"].default_value = 6
    wave.inputs["Detail"].default_value = 3
    mixer = nodes.new("ShaderNodeMix")
    mixer.data_type = "RGBA"
    mixer.blend_type = "MULTIPLY"
    mixer.inputs["Factor"].default_value = 0.18
    links.new(tone_out, mixer.inputs["A"])
    links.new(wave.outputs["Color"], mixer.inputs["B"])
    hsv = nodes.new("ShaderNodeHueSaturation")
    hsv.inputs["Value"].default_value = 1.0 * darken
    hsv.inputs["Saturation"].default_value = 1.0
    links.new(mixer.outputs["Result"], hsv.inputs["Color"])
    links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.6
    add_bump(nodes, links, bsdf, 60, 0.15)
    return mat


def solid(name, rgb, roughness=0.5, metallic=0.0):
    mat, nodes, links, bsdf = principled(name)
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def glass():
    mat, nodes, links, bsdf = principled("glass")
    bsdf.inputs["Base Color"].default_value = (0.94, 0.97, 0.97, 1)
    bsdf.inputs["Roughness"].default_value = 0.0
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    bsdf.inputs["IOR"].default_value = 1.45
    return mat


def glow():
    mat, nodes, links, bsdf = principled("glow")
    bsdf.inputs["Base Color"].default_value = (0.9, 0.86, 0.8, 1)
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.78, 0.52, 1)
    bsdf.inputs["Emission Strength"].default_value = 0.9
    return mat


def water():
    mat, nodes, links, bsdf = principled("water")
    coords = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(coords.outputs["Generated"], sep.inputs["Vector"])
    # Turquesa de piscina al sol: fondo celeste claro y ondas finas (foto de referencia).
    color_ramp(nodes, links, sep.outputs["X"], hex_rgb("#2E9FD0"), hex_rgb("#7FD3EE"), bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.02
    bsdf.inputs["Coat Weight"].default_value = 1.0
    wave = add_bump(nodes, links, bsdf, 22, 0.18)
    wave.inputs["Detail"].default_value = 3
    return mat


def leaves():
    mat, nodes, links, bsdf = principled("leaves")
    info = nodes.new("ShaderNodeObjectInfo")
    ramp = nodes.new("ShaderNodeValToRGB")
    elements = ramp.color_ramp.elements
    elements[0].color = (0.035, 0.11, 0.02, 1)
    elements[1].color = (0.13, 0.26, 0.05, 1)
    mid = elements.new(0.5)
    mid.color = (0.07, 0.19, 0.035, 1)
    links.new(info.outputs["Random"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.7
    bsdf.inputs["Subsurface Weight"].default_value = 0.15
    bsdf.inputs["Subsurface Radius"].default_value = (0.2, 0.4, 0.1)
    add_bump(nodes, links, bsdf, 40, 0.5, kind="voronoi")
    return mat


def lawn():
    """Pasto: franjas de corte suaves a lo largo de la casa, manchas y variación fina."""
    mat, nodes, links, bsdf = principled("lawn")
    coords = nodes.new("ShaderNodeTexCoord")
    wave = nodes.new("ShaderNodeTexWave")
    wave.inputs["Scale"].default_value = 0.22
    wave.wave_profile = "SIN"
    wave.bands_direction = "Y"
    links.new(coords.outputs["Object"], wave.inputs["Vector"])
    patches = nodes.new("ShaderNodeTexNoise")
    patches.inputs["Scale"].default_value = 0.35
    patches.inputs["Detail"].default_value = 6
    links.new(coords.outputs["Object"], patches.inputs["Vector"])
    fine = nodes.new("ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value = 140
    fine.inputs["Detail"].default_value = 12
    links.new(coords.outputs["Object"], fine.inputs["Vector"])
    a = nodes.new("ShaderNodeMath")
    a.operation = "MULTIPLY_ADD"
    a.inputs[1].default_value = 0.12
    links.new(wave.outputs["Fac"], a.inputs[0])
    links.new(patches.outputs["Fac"], a.inputs[2])
    mixf = nodes.new("ShaderNodeMath")
    mixf.operation = "MULTIPLY_ADD"
    mixf.inputs[1].default_value = 0.4
    links.new(fine.outputs["Fac"], mixf.inputs[0])
    links.new(a.outputs["Value"], mixf.inputs[2])
    color_ramp(nodes, links, mixf.outputs["Value"], (0.035, 0.085, 0.016), (0.085, 0.165, 0.03), bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.92
    bsdf.inputs["Sheen Weight"].default_value = 0.4
    add_bump(nodes, links, bsdf, 900, 0.35)
    return mat


def lawn_photo(folder):
    """Pasto fotográfico (Poly Haven, leafy_grass) teñido a verde de prado regado, en losetas
    de 2,5 m con una mancha grande encima para que no se note la repetición."""
    mat, nodes, links, bsdf = principled("lawn")
    coords = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (0.4, 0.4, 0.4)
    links.new(coords.outputs["Object"], mapping.inputs["Vector"])

    def image(name, non_color=False):
        node = nodes.new("ShaderNodeTexImage")
        node.image = bpy.data.images.load(f"{folder}/grass/leafy_grass_{name}_2k.jpg")
        if non_color:
            node.image.colorspace_settings.name = "Non-Color"
        links.new(mapping.outputs["Vector"], node.inputs["Vector"])
        return node

    diffuse = image("diff")
    tint = nodes.new("ShaderNodeHueSaturation")
    tint.inputs["Hue"].default_value = 0.515
    tint.inputs["Saturation"].default_value = 1.7
    tint.inputs["Value"].default_value = 0.62
    links.new(diffuse.outputs["Color"], tint.inputs["Color"])
    patches = nodes.new("ShaderNodeTexNoise")
    patches.inputs["Scale"].default_value = 0.25
    patches.inputs["Detail"].default_value = 4
    links.new(coords.outputs["Object"], patches.inputs["Vector"])
    shade = nodes.new("ShaderNodeMix")
    shade.data_type = "RGBA"
    shade.blend_type = "MULTIPLY"
    links.new(patches.outputs["Fac"], shade.inputs["Factor"])
    links.new(tint.outputs["Color"], shade.inputs["A"])
    shade.inputs["B"].default_value = (0.62, 0.86, 0.5, 1)
    links.new(shade.outputs["Result"], bsdf.inputs["Base Color"])
    rough = image("rough", True)
    links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])
    normal_map = nodes.new("ShaderNodeNormalMap")
    links.new(image("nor_gl", True).outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


MATERIALS = {
    "plaster": plaster(),
    "roof-edge": plaster(),
    "roof": gravel(),
    "concrete": concrete(),
    "wood": wood("wood"),
    "door-wood": wood("door-wood", base=hex_rgb("#BE8960")),  # bronce + 12 % blanco (escena web)
    "floor": wood("floor", base=hex_rgb("#CBA17F")),         # bronce + 30 % blanco (escena web)
    "frame": solid("frame", hex_rgb("#2C3539"), 0.45, 0.4),  # antracita, como los marcos del 3D
    "glass": glass(),
    "glow": glow(),
    "water": water(),
    "leaves": leaves(),
    "trunk": solid("trunk", hex_rgb("#6A4B33"), 0.9),
    "cushion": solid("cushion", (0.85, 0.84, 0.8), 0.8),
    "fabric": solid("fabric", (0.62, 0.58, 0.5), 0.95),
    "linen": solid("linen", (0.9, 0.88, 0.84), 0.9),
    "rug": solid("rug", (0.55, 0.5, 0.42), 1.0),
    "oak": wood("oak", 1.25),
    "pot": solid("pot", (0.72, 0.7, 0.66), 0.8),
}

for obj in scene.objects:
    if obj.type != "MESH":
        continue
    for slot in obj.material_slots:
        if slot.material is None:
            continue
        base = slot.material.name.split(".")[0]
        if base in MATERIALS:
            slot.link = "OBJECT"
            slot.material = MATERIALS[base]

# ── Interior: muebles y luces cálidas, visibles por los ventanales y claraboyas ──
# Recintos (Blender, Z arriba): estar x −7,8…2,8 · y −2,8…3,8 (ventanal al sur, y −2,9);
# dormitorio x 3,2…8,8 · y −6,8…3,8 (ventanal al sur, y −6,9). Piso a z 0,32.
def box(name, center, size, material):
    bpy.ops.mesh.primitive_cube_add(location=center)
    item = bpy.context.active_object
    item.name = name
    item.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    item.data.materials.append(MATERIALS[material])
    return item


Z = 0.32
box("alfombra", (-4.6, -1.3, Z + 0.005), (4.6, 3.0, 0.01), "rug")
box("sofa-asiento", (-4.6, -0.3, Z + 0.22), (3.4, 1.0, 0.44), "fabric")
box("sofa-respaldo", (-4.6, 0.3, Z + 0.45), (3.4, 0.25, 0.9), "fabric")
box("sofa-brazo-o", (-6.4, -0.3, Z + 0.3), (0.25, 1.0, 0.6), "fabric")
box("sofa-brazo-e", (-2.8, -0.3, Z + 0.3), (0.25, 1.0, 0.6), "fabric")
box("mesa-centro", (-4.6, -1.8, Z + 0.19), (1.3, 0.6, 0.06), "oak")
box("mesa-centro-pie", (-4.6, -1.8, Z + 0.08), (1.1, 0.4, 0.16), "frame")
box("comedor", (0.2, -0.9, Z + 0.74), (2.2, 1.0, 0.05), "oak")
for dx in (-0.8, 0.8):
    box("comedor-pata", (0.2 + dx, -0.9, Z + 0.36), (0.08, 0.8, 0.72), "frame")
for sx, sy in ((-0.7, -1.6), (0.0, -1.6), (0.7, -1.6), (-0.7, -0.2), (0.0, -0.2), (0.7, -0.2)):
    box("silla", (0.2 + sx, sy, Z + 0.23), (0.44, 0.44, 0.46), "linen")
    box("silla-respaldo", (0.2 + sx, sy + (0.2 if sy < -0.9 else -0.2), Z + 0.65), (0.44, 0.04, 0.4), "oak")
box("cocina", (1.0, 3.0, Z + 0.45), (3.4, 0.7, 0.9), "linen")
box("cocina-cubierta", (1.0, 3.0, Z + 0.92), (3.5, 0.75, 0.04), "pot")
box("isla", (0.2, 1.6, Z + 0.45), (2.2, 0.9, 0.9), "linen")
box("isla-cubierta", (0.2, 1.6, Z + 0.92), (2.3, 1.0, 0.04), "pot")
box("cama", (5.8, -3.2, Z + 0.25), (2.0, 2.2, 0.5), "linen")
box("cama-cubre", (5.8, -3.0, Z + 0.52), (1.9, 1.6, 0.06), "fabric")
box("cama-respaldo", (5.8, -2.0, Z + 0.55), (2.1, 0.08, 1.1), "oak")
for x, y in ((4.6, -2.2), (7.0, -2.2)):
    box("velador", (x, y, Z + 0.25), (0.5, 0.45, 0.5), "oak")
box("ropero", (7.0, 3.3, Z + 1.1), (3.2, 0.6, 2.2), "oak")

for name, location, energy, size in (
    ("luz-estar-o", (-4.6, 0.3, 3.2), 260, 2.0),
    ("luz-estar-e", (0.2, -0.4, 3.2), 220, 2.0),
    ("luz-cocina", (0.8, 2.6, 3.2), 140, 1.5),
    ("luz-dormitorio", (6.0, -2.0, 3.2), 200, 2.0),
):
    light = bpy.data.lights.new(name, "AREA")
    light.energy = energy
    light.size = size
    light.color = (1.0, 0.78, 0.55)
    holder = bpy.data.objects.new(name, light)
    holder.location = location
    scene.collection.objects.link(holder)

# ── Detalle de techo: dos claraboyas sobre el estar (three.js x −5 y −1, z −1) ──
for x in (-5.0, -1.0):
    bpy.ops.mesh.primitive_cube_add(location=(x, 1.0, 3.75))
    curb = bpy.context.active_object
    curb.scale = (0.75, 0.55, 0.12)
    curb.data.materials.append(MATERIALS["plaster"])
    bpy.ops.mesh.primitive_cube_add(location=(x, 1.0, 3.88))
    pane = bpy.context.active_object
    pane.scale = (0.68, 0.48, 0.02)
    pane.data.materials.append(MATERIALS["glass"])

# ── Entorno: cerco vivo alrededor del terreno y árboles vecinos ─────────────
# El terreno de la maqueta web (three.js): x −15,5 … 16,5; z −10 … 16.
def foliage_block(name, location, size):
    bpy.ops.mesh.primitive_cube_add(location=location)
    block = bpy.context.active_object
    block.name = name
    block.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    block.data.materials.append(MATERIALS["leaves"])
    return block


x0, x1 = -15.5, 16.5
y0, y1 = -16.0, 10.0  # z de three.js → −y de Blender
hedge = 1.3
if not ASSETS:  # con árboles escaneados, el cerco de racimos se ve falso: se omite
    foliage_block("cerco-n", ((x0 + x1) / 2, y1, hedge / 2), (x1 - x0, 0.9, hedge))
    foliage_block("cerco-o", (x0, (y0 + y1) / 2, hedge / 2), (0.9, y1 - y0, hedge))
    foliage_block("cerco-e", (x1, (y0 + y1) / 2, hedge / 2), (0.9, y1 - y0, hedge))

tree_source = next(o for o in scene.objects if o.type == "MESH" and o.material_slots
                    and o.material_slots[0].material == MATERIALS["leaves"] and max(o.dimensions) > 1.2)
trunk_source = next(o for o in scene.objects if o.type == "MESH" and o.material_slots
                    and o.material_slots[0].material == MATERIALS["trunk"])
import random  # noqa: E402

random.seed(11)
for i in range(26):
    while True:
        x = random.uniform(-45, 45)
        y = random.uniform(-12, 45)  # nunca entre la cámara y la casa
        if not (x0 - 3 < x < x1 + 3 and y0 - 3 < y < y1 + 3):
            break
    scale = random.uniform(0.9, 1.9)
    if ASSETS:
        continue  # los vecinos se ponen más abajo, como jacarandás
    crown = tree_source.copy()
    crown.data = tree_source.data
    crown.location = (x, y, 2.6 * scale)
    crown.scale = (1.6 * scale, 1.6 * scale, 1.5 * scale)
    scene.collection.objects.link(crown)
    trunk = trunk_source.copy()
    trunk.location = (x, y, 1.0 * scale)
    trunk.scale = (1.4, 1.4, 1.6 * scale)
    scene.collection.objects.link(trunk)

# ── Árboles escaneados (con la carpeta de recursos) ──────────────────────────
# Cada árbol de la escena (tronco + copa) se cambia por un jacarandá real del mismo alto,
# en el mismo lugar; los árboles vecinos también. Los arbustos bajos quedan.
import os  # noqa: E402


def load_model(name, only=None):
    """Modelo glTF de Poly Haven → colección para instanciar; None si no está en la carpeta.
    `only`: quedarse con una sola malla (los arbustos vienen de a cuatro, en fila) y centrarla."""
    path = f"{ASSETS}/{name}/{name}_1k.gltf"
    if not os.path.exists(path):
        return None
    bpy.ops.import_scene.gltf(filepath=path)
    collection = bpy.data.collections.new(name)
    height = 0.0
    for obj in list(bpy.context.selected_objects):
        for owner in obj.users_collection:
            owner.objects.unlink(obj)
        if only and obj.name != only:
            bpy.data.objects.remove(obj, do_unlink=True)
            continue
        if only:
            obj.location = (0, 0, 0)
        collection.objects.link(obj)
        if obj.type == "MESH":
            height = max(height, (obj.matrix_world @ Vector(obj.bound_box[1])).z)
    collection["height"] = height
    return collection


def place(collection, name, x, y, height, rotation):
    holder = bpy.data.objects.new(name, None)
    holder.instance_type = "COLLECTION"
    holder.instance_collection = collection
    holder.location = (x, y, 0)
    holder.rotation_euler = (0, 0, rotation)
    holder.scale = (height / collection["height"],) * 3
    scene.collection.objects.link(holder)
    return holder


if ASSETS:
    bpy.ops.import_scene.gltf(filepath=f"{ASSETS}/jacaranda/jacaranda_tree_1k.gltf")
    jacaranda = bpy.context.selected_objects[0]
    source = bpy.data.collections.new("jacaranda")
    for obj in bpy.context.selected_objects:
        for collection in obj.users_collection:
            collection.objects.unlink(obj)
        source.objects.link(obj)
    native_height = jacaranda.dimensions.z
    source["height"] = native_height
    round_tree = load_model("tree_small_02") or source  # ralo de cerca: solo para algunos vecinos
    shrub = load_model("shrub_02", only="shrub_02_a")
    trunks = [o for o in scene.objects if o.type == "MESH" and o.material_slots
              and o.material_slots[0].material == MATERIALS["trunk"]]
    spots = []
    for trunk in trunks:
        height = trunk.dimensions.z / 1.4 * 3.4  # alto total del árbol de la escena web
        spots.append((trunk.location.x, trunk.location.y, height))
    # Arbustos bajos (copas sin tronco): jacarandás jóvenes de 1,6 m.
    for obj in scene.objects:
        if (obj.type == "MESH" and obj.material_slots and obj.material_slots[0].material == MATERIALS["leaves"]
                and obj.location.z <= 1.2 and obj.name not in ("leaf-clump",)):
            spots.append((obj.location.x, obj.location.y, 1.6))
    for obj in [o for o in scene.objects if o.type == "MESH" and o.material_slots
                and o.material_slots[0].material in (MATERIALS["trunk"], MATERIALS["leaves"])
                and o.name != "leaf-clump"]:
        bpy.data.objects.remove(obj, do_unlink=True)
    for i, (x, y, height) in enumerate(spots):
        place(source, f"arbol-{i}", x, y, height * 1.15, (i * 2.399) % (2 * math.pi))

    # Jardineras: arbustos al pie de los muros y junto a la piscina, y maceteros en la
    # terraza (foto de referencia). Nunca delante del ventanal del estar.
    if shrub:
        random.seed(7)
        beds = [
            [(x, -8.2) for x in (3.6, 4.4, 5.2, 6.0, 6.8, 7.6, 8.4)],           # frente del dormitorio
            [(10.0, y) for y in (-6.5, -5.4, -4.3, -3.2, -2.1, -1.0, 0.1, 1.2, 2.3, 3.4)],  # costado este
            [(-9.2, y) for y in (-2.4, -1.4, 2.4, 3.4)],                           # costado oeste, sin tapar la puerta
            [(x, -12.6) for x in (-6.5, -5.3, -4.1, -2.9, -1.7, -0.5, 0.7)],       # borde sur de la piscina
            [(2.4, y) for y in (-11.0, -9.8)],                                     # cabecera este de la piscina
        ]
        for b, bed in enumerate(beds):
            for j, (x, y) in enumerate(bed):
                place(shrub, f"arbusto-{b}-{j}", x + random.uniform(-0.2, 0.2), y + random.uniform(-0.2, 0.2),
                      random.uniform(0.8, 1.2), random.uniform(0, 2 * math.pi))
        for j, (x, y) in enumerate(((-7.6, -3.6), (2.5, -3.6), (-3.2, -7.2))):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.5, location=(x, y, 0.55))
            pot = bpy.context.active_object
            pot.name = f"macetero-{j}"
            pot.data.materials.append(MATERIALS["pot"])
            bush = place(shrub, f"macetero-planta-{j}", x, y, 0.9, random.uniform(0, 2 * math.pi))
            bush.location.z = 0.78

if ASSETS:
    random.seed(11)
    for i in range(26):
        while True:
            x = random.uniform(-45, 45)
            y = random.uniform(-12, 45)
            if not (x0 - 3 < x < x1 + 3 and y0 - 3 < y < y1 + 3):
                break
        species = round_tree if random.random() < 0.3 else source
        place(species, f"vecino-{i}", x, y, random.uniform(6.5, 11), random.uniform(0, 2 * math.pi))

# ── Follaje: racimos de hojas sobre cada copa ──────────────────────────────
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1, location=(0, 0, -50))
clump = bpy.context.active_object
clump.name = "leaf-clump"
displace = clump.modifiers.new("relieve", "DISPLACE")
displace.texture = bpy.data.textures.new("hojas", "CLOUDS")
displace.texture.noise_scale = 0.25
displace.strength = 0.35
bpy.ops.object.shade_smooth()
clump.data.materials.append(MATERIALS["leaves"])

for obj in list(scene.objects):
    if obj.type == "MESH" and obj.material_slots and obj.material_slots[0].material == MATERIALS["leaves"] and obj is not clump:
        size = max(obj.dimensions)
        system = obj.modifiers.new("follaje", "PARTICLE_SYSTEM").particle_system
        settings = system.settings
        # Partículas quietas nacidas antes del cuadro 1: quedan pegadas a la copa.
        settings.type = "EMITTER"
        settings.frame_start = 0
        settings.frame_end = 0
        settings.lifetime = 1000
        settings.physics_type = "NO"
        settings.emit_from = "FACE"
        settings.normal_factor = 0.0
        settings.count = int(120 + 220 * size)
        settings.render_type = "OBJECT"
        settings.instance_object = clump
        settings.particle_size = min(0.42, 0.18 + 0.045 * size)
        settings.size_random = 0.45
        settings.use_rotations = True
        settings.rotation_mode = "NOR"
        settings.phase_factor_random = 2.0
        settings.rotation_factor_random = 1.0
        system.seed = hash(obj.name) % 1000

# ── Terreno ───────────────────────────────────────────────────────────────
bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "pasto"
ground.data.materials.append(lawn_photo(ASSETS) if ASSETS else lawn())

# Hebras de pasto (pelo) cerca de la casa: dan el relieve del césped de la referencia.
bpy.ops.mesh.primitive_plane_add(size=260, location=(1, -6, 0.002))
turf = bpy.context.active_object
turf.name = "cesped"
# Verde propio: la textura del suelo, leída por coordenadas de objeto, tiñe mal las hebras.
turf.data.materials.append(solid("hebras", tuple(c * 0.55 for c in hex_rgb("#7DA356")), 0.8))
blades = turf.modifiers.new("hebras", "PARTICLE_SYSTEM").particle_system
blades_settings = blades.settings
blades_settings.type = "HAIR"
blades_settings.count = 1_600_000
blades_settings.hair_length = 0.09
blades_settings.use_advanced_hair = True
blades_settings.root_radius = 0.6
blades_settings.tip_radius = 0.05
blades_settings.child_type = "SIMPLE"
blades_settings.child_percent = 4
blades_settings.rendered_child_count = 4
blades_settings.child_length = 0.9
blades_settings.child_length_threshold = 0.3
blades_settings.clump_factor = 0.3
blades_settings.roughness_2 = 0.08
blades_settings.use_hair_bspline = True
blades.seed = 3

# ── Cielo y sol ───────────────────────────────────────────────────────────
world = bpy.data.worlds.new("cielo")
scene.world = world
world.use_nodes = True
sun_dir = to_blender(SUN_THREE).normalized()
if ASSETS:
    # Cielo real: su sol está a 48° de elevación, igual que el de la escena web; se gira
    # el cielo para que también coincida el rumbo y las sombras calcen con el 3D.
    env = world.node_tree.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(f"{ASSETS}/kloofendal_48d_partly_cloudy_puresky_2k.hdr")
    width, height = env.image.size
    pixels = env.image.pixels[:]
    brightest, sun_u = 0.0, 0.5
    for y in range(height // 2, height, 2):
        for x in range(0, width, 2):
            i = (y * width + x) * 4
            value = pixels[i] + pixels[i + 1] + pixels[i + 2]
            if value > brightest:
                brightest, sun_u = value, x / width
    hdr_azimuth = (sun_u - 0.5) * 2 * math.pi            # Blender: u = atan2(y, −x) / 2π + 0.5
    target_azimuth = math.atan2(sun_dir.y, -sun_dir.x)
    coords = world.node_tree.nodes.new("ShaderNodeTexCoord")
    mapping = world.node_tree.nodes.new("ShaderNodeMapping")
    mapping.inputs["Rotation"].default_value = (0, 0, hdr_azimuth - target_azimuth)
    world.node_tree.links.new(coords.outputs["Generated"], mapping.inputs["Vector"])
    world.node_tree.links.new(mapping.outputs["Vector"], env.inputs["Vector"])
    background = world.node_tree.nodes.get("Background")
    background.inputs["Strength"].default_value = 0.6
    world.node_tree.links.new(env.outputs["Color"], background.inputs["Color"])
    # Sol cálido extra en el mismo rumbo que el del cielo: luz dorada de la referencia sin
    # mover las sombras (el render se funde con la escena 3D).
    gold_data = bpy.data.lights.new("sol-dorado", "SUN")
    gold_data.energy = 2.8
    gold_data.angle = math.radians(1.5)
    gold_data.color = (1.0, 0.95, 0.88)
    gold = bpy.data.objects.new("sol-dorado", gold_data)
    scene.collection.objects.link(gold)
    gold.rotation_euler = (-sun_dir).to_track_quat("-Z", "Y").to_euler()
else:
    sky = world.node_tree.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    sky.sun_elevation = math.asin(sun_dir.z)
    sky.sun_rotation = math.atan2(sun_dir.x, sun_dir.y)
    sky.sun_disc = False
    sky.altitude = 200
    background = world.node_tree.nodes.get("Background")
    background.inputs["Strength"].default_value = 0.18
    world.node_tree.links.new(sky.outputs["Color"], background.inputs["Color"])
    sun_data = bpy.data.lights.new("sol", "SUN")
    sun_data.energy = 5.2
    sun_data.angle = math.radians(0.8)
    sun_data.color = (1.0, 0.93, 0.84)
    sun = bpy.data.objects.new("sol", sun_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (-sun_dir).to_track_quat("-Z", "Y").to_euler()

# ── Cámara: la del final de la animación ───────────────────────────────────
with open(CAMERA_JSON) as handle:
    pose = json.load(handle)
cam_data = bpy.data.cameras.new("camara")
cam_data.sensor_fit = "VERTICAL"
cam_data.angle_y = math.radians(30)
cam_data.clip_end = 1000
camera = bpy.data.objects.new("camara", cam_data)
scene.collection.objects.link(camera)
camera.location = to_blender(pose["position"])
target = to_blender(pose["target"])
camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = camera

# ── Render ────────────────────────────────────────────────────────────────
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 8
scene.render.resolution_x = WIDTH
scene.render.resolution_y = HEIGHT
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = -0.1
# Balance de blancos corrido al frío: la imagen queda cálida, como al atardecer.
scene.view_settings.use_white_balance = False  # los colores deben ser los de la escena 3D
scene.view_settings.white_balance_temperature = 6100
scene.view_settings.white_balance_tint = 2
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
