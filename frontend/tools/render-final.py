"""Render fotorrealista del final de la portada 3D (Blender 4.5, Cycles).

Toma la casa terminada que exporta tools/export-scene.js (GLB + pose de cámara) y la
renderiza con materiales reales, pasto, follaje, cielo físico y sol, desde la misma
cámara del final de la animación (4:5, campo vertical de 30°). El resultado se convierte
en static/img/portada-render-*.webp (ver docs/06-frontend/v2-direccion-artistica.md).

Uso:
  blender -b -P frontend/tools/render-final.py -- house.glb house.camera.json salida.png [ancho] [muestras] [carpeta]

[carpeta] (opcional) tiene los recursos CC0 de Poly Haven (polyhaven.com, dominio público):
  kloofendal_48d_partly_cloudy_puresky_2k.hdr   cielo real (sol a 48°, como la escena web)
  jacaranda/jacaranda_tree_1k.gltf (+ textures/) árbol escaneado
  grass/leafy_grass_{diff,nor_gl,rough}_2k.jpg   pasto fotográfico
Sin ella, cielo físico de Blender, árboles de racimos y pasto procedural.
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
    color_ramp(nodes, links, noise.outputs["Fac"], (0.035, 0.038, 0.042), (0.11, 0.11, 0.115), bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.95
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


def wood(name, darken=1.0):
    """Madera con veta: bandas onduladas sobre el tono de cada tabla (color del objeto)."""
    mat, nodes, links, bsdf = principled(name)
    info = nodes.new("ShaderNodeObjectInfo")
    wave = nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "Z"
    wave.inputs["Scale"].default_value = 18
    wave.inputs["Distortion"].default_value = 6
    wave.inputs["Detail"].default_value = 3
    mixer = nodes.new("ShaderNodeMix")
    mixer.data_type = "RGBA"
    mixer.blend_type = "MULTIPLY"
    mixer.inputs["Factor"].default_value = 0.35
    links.new(info.outputs["Color"], mixer.inputs["A"])
    links.new(wave.outputs["Color"], mixer.inputs["B"])
    hsv = nodes.new("ShaderNodeHueSaturation")
    hsv.inputs["Value"].default_value = 0.78 * darken
    hsv.inputs["Saturation"].default_value = 0.85
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
    bsdf.inputs["Base Color"].default_value = (0.82, 0.9, 0.92, 1)
    bsdf.inputs["Roughness"].default_value = 0.0
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    bsdf.inputs["IOR"].default_value = 1.45
    return mat


def glow():
    mat, nodes, links, bsdf = principled("glow")
    bsdf.inputs["Base Color"].default_value = (0.9, 0.86, 0.8, 1)
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.78, 0.52, 1)
    bsdf.inputs["Emission Strength"].default_value = 1.6
    return mat


def water():
    mat, nodes, links, bsdf = principled("water")
    coords = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(coords.outputs["Generated"], sep.inputs["Vector"])
    color_ramp(nodes, links, sep.outputs["X"], (0.02, 0.42, 0.62), (0.08, 0.62, 0.78), bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.02
    bsdf.inputs["Coat Weight"].default_value = 1.0
    wave = add_bump(nodes, links, bsdf, 9, 0.12)
    wave.inputs["Detail"].default_value = 2
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
    tint.inputs["Hue"].default_value = 0.55
    tint.inputs["Saturation"].default_value = 1.3
    tint.inputs["Value"].default_value = 0.66
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
    shade.inputs["B"].default_value = (0.75, 0.85, 0.6, 1)
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
    "door-wood": wood("door-wood", 0.8),
    "floor": wood("floor", 1.1),
    "frame": solid("frame", (0.02, 0.022, 0.025), 0.35, 1.0),
    "glass": glass(),
    "glow": glow(),
    "water": water(),
    "leaves": leaves(),
    "trunk": solid("trunk", (0.09, 0.055, 0.03), 0.9),
    "cushion": solid("cushion", (0.85, 0.84, 0.8), 0.8),
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
if ASSETS:
    bpy.ops.import_scene.gltf(filepath=f"{ASSETS}/jacaranda/jacaranda_tree_1k.gltf")
    jacaranda = bpy.context.selected_objects[0]
    source = bpy.data.collections.new("jacaranda")
    for obj in bpy.context.selected_objects:
        for collection in obj.users_collection:
            collection.objects.unlink(obj)
        source.objects.link(obj)
    native_height = jacaranda.dimensions.z
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
        holder = bpy.data.objects.new(f"arbol-{i}", None)
        holder.instance_type = "COLLECTION"
        holder.instance_collection = source
        holder.location = (x, y, 0)
        holder.rotation_euler = (0, 0, (i * 2.399) % (2 * math.pi))
        holder.scale = (height / native_height,) * 3
        scene.collection.objects.link(holder)

if ASSETS:
    random.seed(11)
    for i in range(26):
        while True:
            x = random.uniform(-45, 45)
            y = random.uniform(-12, 45)
            if not (x0 - 3 < x < x1 + 3 and y0 - 3 < y < y1 + 3):
                break
        holder = bpy.data.objects.new(f"vecino-{i}", None)
        holder.instance_type = "COLLECTION"
        holder.instance_collection = source
        holder.location = (x, y, 0)
        holder.rotation_euler = (0, 0, random.uniform(0, 2 * math.pi))
        holder.scale = (random.uniform(6.5, 11) / native_height,) * 3
        scene.collection.objects.link(holder)

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
    background.inputs["Strength"].default_value = 1.0
    world.node_tree.links.new(env.outputs["Color"], background.inputs["Color"])
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
scene.view_settings.look = "AgX - Medium High Contrast" if not ASSETS else "AgX - High Contrast"
scene.view_settings.exposure = 0.0
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
