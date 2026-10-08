"""Build the v3 FondFont campus scene from the v14 vehicles/garden scene.

blender -b --python scripts/build-fondfont-campus-v3.py [-- --preview]

1. Replaces the projected imagegen building artwork and its shadow/occluder
   proxies with modeled buildings (scripts/fondfont-architecture-v3.py).
2. Retextures the loading-bay interiors with the v3 interior backdrops.
3. Removes the legacy native pets (the runtime loads licensed studio pets).
4. Shares identical meshes and simplifies over-tessellated parts so the
   download stays small; every animated node name is preserved.
Writes blender-v3/campus-v3.blend and campus-v3-raw.glb.
"""
from pathlib import Path
import sys, json, math, hashlib, importlib.util
import bpy, bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / 'scripts/assets/fondfont/blender-v2'
V3 = ROOT / 'scripts/assets/fondfont/blender-v3'
spec = importlib.util.spec_from_file_location('arch', ROOT / 'scripts/fondfont-architecture-v3.py')
arch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arch)
spec = importlib.util.spec_from_file_location('truck', ROOT / 'scripts/fondfont-truck-v3.py')
truck_v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(truck_v3)

bpy.ops.wm.open_mainfile(filepath=str(V2 / 'factory-truck-v14.blend'))
collection = bpy.context.scene.collection
report = {'removed': [], 'shared': {}, 'simplified': {}}


def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons) if o.type == 'MESH' else 0


def delete_tree(o):
    for c in list(o.children_recursive) + [o]:
        report['removed'].append(c.name)
        bpy.data.objects.remove(c, do_unlink=True)


# ------------------------------------------------------------ remove legacy
for name in ('PetDog', 'PetCat', 'FoundryArt', 'PhoneRoof'):
    if name in bpy.data.objects:
        delete_tree(bpy.data.objects[name])
for o in list(bpy.data.objects):
    if o.get('architecture_role') in ('caster', 'occluder', 'artwork'):
        delete_tree(o)

# ------------------------------------------------------------ buildings
for name, builder in (('Foundry', arch.build_foundry), ('Warehouse', arch.build_warehouse)):
    root = bpy.data.objects[name]
    left, right, height, portal_z = root['loading_bay_portal']
    door_plane = -portal_z - root.matrix_world.translation.y
    builder(root, (left, right, height, door_plane), collection)
    root['architecture_revision'] = 'modeled-v3'
    root['reference'] = f'blender-v3/imagegen/{name.lower()}-elevations-v1.png'

# Interior backdrops and floors.
def textured(name, image_name, roughness=.85):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    tex = m.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(str(V3 / 'textures' / image_name), check_existing=True)
    m.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = roughness
    return m


def set_uv(o, fn):
    me = o.data
    layer = me.uv_layers.active or me.uv_layers.new()
    for loop in me.loops:
        layer.data[loop.index].uv = fn(me.vertices[loop.vertex_index].co)


for name, image in (('Foundry', 'foundry-interior.png'), ('Warehouse', 'warehouse-interior.png')):
    root = bpy.data.objects[name]
    back = bpy.data.objects[f'{name} bay back wall']
    floor = bpy.data.objects[f'{name} bay floor']
    # From the fixed 33-degree camera the doorhead sight line meets the bay floor about
    # 2.5 m inside, so the 4.4 m back wall is never visible: keep it plain, ship no backdrop.
    back.data.materials.clear()
    back.data.materials.append(bpy.data.materials['Loading bay shaded walls'])
    back['architecture_role'] = 'interior'
    floor.data.materials.clear()
    floor.data.materials.append(arch.palette()['concrete'])
    set_uv(floor, lambda c: (c.x / 1.2, c.y / 1.2))
    floor['architecture_role'] = 'interior'

# ------------------------------------------------------------ truck
truck_v3.build_truck(collection)

# Runtime anchors follow the modeled boards and chimney throat.
bpy.data.objects['FoundrySign'].location.y = arch.FRONT - .047
bpy.data.objects['WarehouseSign'].location.y = arch.FRONT - .047
# Roof glyphs: the anchor sits at the screen centre; the runtime lays glyphs out within these bounds.
roof = arch.WAREHOUSE_ROOF
glyphs = bpy.data.objects['PhoneScreenGlyph']
glyphs.location = (roof['cx'], roof['cy'], arch.WAREHOUSE_EAVE + arch.PHONE_BAND + .026 + .004)
glyphs['screen_half_width'] = roof['screen_hx']
glyphs['screen_half_depth'] = roof['screen_hy']
glyphs['camera_island_right'] = roof['pill_x'] + .14
sign = bpy.data.objects['WarehouseSign']
sign.location.z = arch.SIGN_Z
smoke = bpy.data.objects['ChimneySmoke']
smoke.location = (2.94, .05, 5.08)

# ------------------------------------------------------------ size budget
def signature(o):
    me = o.data
    pts = sorted((round(v.co.x, 4), round(v.co.y, 4), round(v.co.z, 4)) for v in me.vertices)
    mats = tuple(m.name if m else '' for m in me.materials)
    return hashlib.sha1(repr((pts, len(me.polygons), mats)).encode()).hexdigest()


def share_identical(objects, label):
    groups = {}
    for o in objects:
        if o.type == 'MESH' and not o.modifiers:
            groups.setdefault(signature(o), []).append(o)
    saved = 0
    for group in groups.values():
        first = group[0]
        for o in group[1:]:
            if o.data != first.data:
                saved += tris(o)
                old = o.data
                o.data = first.data
                if old.users == 0:
                    bpy.data.meshes.remove(old)
    report['shared'][label] = saved


def simplify(objects, ratio, label, planar=True):
    before = after = 0
    for o in objects:
        if o.type != 'MESH':
            continue
        if o.data.users > 1:
            o.data = o.data.copy()
        before += tris(o)
        bm = bmesh.new()
        bm.from_mesh(o.data)
        if planar:
            bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts, edges=bm.edges,
                                     delimit={'MATERIAL', 'SEAM', 'UV'})
        bm.to_mesh(o.data)
        bm.free()
        if ratio < 1:
            mod = o.modifiers.new('budget', 'DECIMATE')
            mod.ratio = ratio
            mod.use_collapse_triangulate = True
            with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o]):
                bpy.ops.object.modifier_apply(modifier=mod.name)
        after += tris(o)
    report['simplified'][label] = [before, after]


def meshes_under(name):
    root = bpy.data.objects[name]
    return [o for o in root.children_recursive if o.type == 'MESH']


bpy.context.view_layer.update()
# Type sorts: identical columns share data; glyph contours keep their silhouette.
sorts = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('TypeSort')]
simplify(sorts, .45, 'type sorts')
share_identical(sorts, 'type sorts')
# Truck wheels and forklift wheels share per side/radius; lugs and treads are lighter.
# Forklift tyres keep their exact rolling profile (ground-contact checks); hubs and lugs are lightened.
wheels = [o for o in bpy.data.objects if o.type == 'MESH' and 'StackerWheel' in o.name and not o.name.endswith('_rubber')]
simplify(wheels, .3, 'wheels')
share_identical(wheels, 'wheels')
drains = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('Road drain')]
share_identical(drains, 'drains')
stackers = meshes_under('SourceStacker') + meshes_under('ReceiverStacker')
share_identical([o for o in stackers if 'Wheel' not in o.name], 'forklift bodies')
butterfly = meshes_under('Butterfly')
simplify(butterfly, .12, 'butterfly')
share_identical(butterfly, 'butterfly wings')
garden = meshes_under('Garden')
simplify(garden, .4, 'garden')

# ------------------------------------------------------------ texture budget
def drop_normal_maps(material):
    nodes = material.node_tree.nodes
    for n in list(nodes):
        if n.type == 'TEX_IMAGE' and n.image and n.image.name.endswith('-normal.png'):
            nodes.remove(n)
    for n in list(nodes):
        if n.type == 'NORMAL_MAP':
            nodes.remove(n)


def downscale(material, size):
    for n in material.node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image and n.image.size[0] > size:
            n.image.scale(size, size)
    report.setdefault('downscaled', []).append([material.name, size])


mats = bpy.data.materials
for name, size in (('imagegen limestone trim', 256), ('imagegen oak', 512),
                   ('imagegen FondFont red enamel', 256), ('imagegen plum enamel', 256)):
    drop_normal_maps(mats[name])
    downscale(mats[name], size)
# The road uses the seamless v3 asphalt tile in world-scale UVs instead of one stretched painting.
road_mat = mats['imagegen quiet asphalt']
for n in road_mat.node_tree.nodes:
    if n.type == 'TEX_IMAGE':
        n.image = bpy.data.images.load(str(V3 / 'textures/asphalt.png'), check_existing=True)
road_mat.name = 'v3 asphalt'
set_uv(bpy.data.objects['Architecture_imagegen quiet asphalt'], lambda c: (c.x / 2.4, c.y / 2.4))
for name in ('industrial-foundry-v1.png', 'industrial-warehouse-blank-v2.png', 'quiet-road.png', 'oak-normal.png', 'stone-normal.png'):
    image = bpy.data.images.get(name)
    if image and image.users == 0:
        bpy.data.images.remove(image)

# ------------------------------------------------------------ save + export
bpy.ops.wm.save_as_mainfile(filepath=str(V3 / 'campus-v3.blend'))
bpy.ops.export_scene.gltf(filepath=str(V3 / 'campus-v3-raw.glb'), export_format='GLB', export_apply=True,
                          export_cameras=False, export_lights=False, export_animations=False, export_extras=True,
                          export_image_format='WEBP', export_image_quality=86)
total = sum(tris(o) for o in bpy.data.objects)
report['triangles'] = total
(V3 / 'campus-v3-build.json').write_text(json.dumps(report, indent=2) + '\n')
print('TRIANGLES', total)
print(json.dumps({k: v for k, v in report.items() if k != 'removed'}, indent=1))
