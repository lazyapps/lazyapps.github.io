"""Private real-time trial of the downloaded Autumn and Domestic cat assets.

Evaluate the original rig, including cages/correctives, into morph poses. The
source animal meshes and groom are retained; no replacement animal is modeled.
Usage: Blender -b --disable-autoexec --python this_file.py -- dog|cat
"""
from pathlib import Path
import sys
import math
import json
import bpy
import numpy as np
from mathutils import Vector, Matrix
from mathutils.kdtree import KDTree

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/pets'
KIND = sys.argv[sys.argv.index('--') + 1]
DOG = KIND == 'dog'
OUT = ASSETS / 'trial'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ASSETS / ('autumn/source/autumn/autumn.blend' if DOG else 'domestic-cat/domestic-cat.blend')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE), use_scripts=False)
scene = bpy.context.scene
scene.frame_set(1)
for collection in bpy.data.collections:
    collection.hide_viewport = False
for layer in scene.view_layers:
    def enable(c):
        c.exclude = False
        c.hide_viewport = False
        for child in c.children:
            enable(child)
    enable(layer.layer_collection)
rig = bpy.data.objects['RIG-autumn' if DOG else 'Armature.001']
if DOG:
    names = ['GEO_autumn_body', 'GEO_autumn_eye.l', 'GEO_autumn_eye.r',
             'GEO_autumn_scarf', 'GEO_autumn_scarf.endpiece',
             'GEO_autumn_teeth.lower', 'GEO_autumn_teeth.upper', 'GEO_autumn_tongue']
    emitter = bpy.data.objects['GEO_autumn_body.hair']
    # BlenRig's sole controls translate the planted paw. The similarly named
    # hand/foot_ik_ctrl bones are roll pivots and must not drive translation.
    limbs = [('hand_sole_ctrl_L', 'hand_def_L', 0), ('hand_sole_ctrl_R', 'hand_def_R', .5),
             ('sole_ctrl_L', 'foot_def_L', .75), ('sole_ctrl_R', 'foot_def_R', .25)]
else:
    names = ['sculpt.001', 'Eye1']
    emitter = bpy.data.objects['sculpt.001']
    limbs = [('paw_control_L', 'paw3_L', 0), ('paw_control_R', 'paw3_R', .5),
             ('leg3_control_L', 'feet_L', .75), ('leg3_control_R', 'feet_R', .25)]
sources = [bpy.data.objects[n] for n in names]
body = sources[0]
for obj in bpy.data.objects:
    obj.hide_set(False)
    obj.hide_render = obj not in sources and obj != emitter
    if obj.type == 'MESH':
        for modifier in obj.modifiers:
            if modifier.type == 'SUBSURF':
                modifier.levels = 1
                modifier.render_levels = 1
for system in emitter.particle_systems:
    # Original combed parent strands suffice for a small hero animal.
    system.settings.child_percent = 0
    system.settings.rendered_child_count = 0
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()

def evaluated_mesh(obj):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
    return evaluated, mesh

def coords(obj):
    evaluated, mesh = evaluated_mesh(obj)
    values = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get('co', values)
    values = values.reshape((-1, 3))
    matrix = np.array(obj.matrix_world, dtype=np.float32)
    values = values @ matrix[:3, :3].T + matrix[:3, 3]
    evaluated.to_mesh_clear()
    return values

# Save a clean copy of each evaluated source surface, keeping UVs/material slots.
exports = []
for obj in sources:
    evaluated = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
    mesh.transform(obj.matrix_world)
    copy = bpy.data.objects.new('Studio' + KIND.title() + '-' + obj.name, mesh)
    scene.collection.objects.link(copy)
    exports.append(copy)

# Bake the source material color graph (not lighting) into the original UVs.
# This retains the cat's tabby markings and white paws, and the dog's scarf.
scene.render.engine = 'CYCLES'
scene.cycles.samples = 1
scene.render.bake.use_pass_direct = False
scene.render.bake.use_pass_indirect = False
scene.render.bake.use_pass_color = True
scene.render.bake.margin = 6
for obj in exports:
    if not obj.data.uv_layers:
        continue
    materials = []
    for material in obj.data.materials:
        material = material.copy()
        material.use_nodes = True
        materials.append(material)
    obj.data.materials.clear()
    for material in materials:
        obj.data.materials.append(material)
    image = bpy.data.images.new(obj.name + '-albedo', width=1024 if DOG else 2048, height=1024 if DOG else 2048)
    for material in materials:
        node = material.node_tree.nodes.new('ShaderNodeTexImage')
        node.image = image
        material.node_tree.nodes.active = node
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.bake(type='DIFFUSE')
    image.pack()
    replacement = bpy.data.materials.new(obj.name + '-PBR')
    replacement.use_nodes = True
    nodes = replacement.node_tree.nodes
    shader = nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value = .88 if obj == exports[0] else .55
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = image
    uv_node = nodes.new('ShaderNodeUVMap')
    uv_node.uv_map = obj.data.uv_layers.active.name
    replacement.node_tree.links.new(uv_node.outputs['UV'], tex.inputs['Vector'])
    replacement.node_tree.links.new(tex.outputs['Color'], shader.inputs['Base Color'])
    obj.data.materials.clear()
    obj.data.materials.append(replacement)
    for face in obj.data.polygons:
        face.material_index = 0
    print('Baked source material:', obj.name, flush=True)

# Convert sampled ORIGINAL groom strands into tapered triangular prisms.
# Every root is attached to the evaluated body, so fur follows baked poses.
rest_body = coords(body)
tree = KDTree(len(rest_body))
for index, point in enumerate(rest_body):
    tree.insert(Vector(point), index)
tree.balance()
body_eval, body_mesh = evaluated_mesh(body)
uvs = np.zeros((len(rest_body), 2), dtype=np.float32)
if body_mesh.uv_layers:
    for loop in body_mesh.loops:
        uvs[loop.vertex_index] = body_mesh.uv_layers.active.data[loop.index].uv
body_eval.to_mesh_clear()
fur_vertices, fur_faces, fur_uvs, attachments = [], [], [], []
groom = emitter.evaluated_get(depsgraph)
for system in groom.particle_systems:
    particles = list(system.particles)
    budget = 1700 if DOG else (1300 if system.name == 'BODY' else 260)
    step = max(1, len(particles) // budget)
    for particle in particles[::step][:budget]:
        keys = [emitter.matrix_world @ key.co for key in particle.hair_keys]
        if len(keys) < 2 or (keys[-1] - keys[0]).length < .0002:
            continue
        root, middle, tip = keys[0], keys[len(keys)//2], keys[-1]
        _, index, _ = tree.find(root)
        tangent = (tip-root).normalized()
        side = tangent.cross(Vector((0, 0, 1)))
        if side.length < .01:
            side = tangent.cross(Vector((1, 0, 0)))
        side.normalize()
        other = tangent.cross(side).normalized()
        width = .00065 if DOG else .00038
        start = len(fur_vertices)
        for point, radius in [(root, width), (middle, width*.6), (tip, 0.000015)]:
            for corner in range(3):
                angle = corner * math.tau / 3
                vertex = point + radius*(math.cos(angle)*side+math.sin(angle)*other)
                fur_vertices.append(tuple(vertex))
                fur_uvs.append(uvs[index])
                attachments.append(index)
        for segment in range(2):
            for corner in range(3):
                a = start+segment*3+corner
                b = start+segment*3+(corner+1)%3
                fur_faces.append((a,b,b+3,a+3))
fur_mesh = bpy.data.meshes.new('Original groom geometry')
fur_mesh.from_pydata(fur_vertices, [], fur_faces)
fur_mesh.update()
fur = bpy.data.objects.new('Studio'+KIND.title()+'-original-groom', fur_mesh)
scene.collection.objects.link(fur)
fur_mesh.materials.append(exports[0].data.materials[0])
uv = fur_mesh.uv_layers.new()
for loop in fur_mesh.loops:
    uv.data[loop.index].uv = fur_uvs[loop.vertex_index]
exports.append(fur)
fur_rest = np.array(fur_vertices, dtype=np.float32)
attachments = np.array(attachments, dtype=np.int32)

base_matrices = {name: rig.pose.bones[name].matrix.copy() for name, _, _ in limbs}
foot_origins = {name: rig.pose.bones[foot].matrix.translation.copy() for name, foot, _ in limbs}
tail = rig.pose.bones.get('tail_ctrl' if DOG else 'tail1')
tail_base = tail.matrix.copy()
stride = .10 if DOG else .11
stance = .65

def set_pose(phase=None, wag=0):
    for name, _, _ in limbs:
        rig.pose.bones[name].matrix = base_matrices[name].copy()
    tail.matrix = tail_base.copy()
    if wag:
        origin = tail_base.translation
        tail.matrix = Matrix.Translation(origin) @ Matrix.Rotation(wag, 4, 'Z') @ Matrix.Translation(-origin) @ tail_base
    bpy.context.view_layer.update()
    if phase is None:
        return
    for name, foot, offset in limbs:
        q = (phase+offset) % 1
        if q < stance:
            y, z = stride*(q/stance-.5), 0
        else:
            t = (q-stance)/(1-stance)
            smooth = t*t*(3-2*t)
            y, z = stride*(.5-smooth), (.022 if DOG else .015)*math.sin(math.pi*t)**1.5
        desired = foot_origins[name]+Vector((0,y,z))
        # Native roll pivots affect the endpoint; solve against the evaluated paw.
        for _ in range(5):
            delta = desired-rig.pose.bones[foot].matrix.translation
            if delta.length < .00015:
                break
            control = rig.pose.bones[name]
            matrix = control.matrix.copy()
            matrix.translation += delta
            control.matrix = matrix
            bpy.context.view_layer.update()

for obj in exports:
    obj.shape_key_add(name='Basis')
pose_names = []
contact_errors = []
for frame in range(16):
    phase = frame/16
    set_pose(phase)
    values = [coords(obj) for obj in sources]
    values.append(fur_rest+(values[0]-rest_body)[attachments])
    name = 'Walk%02d' % frame
    pose_names.append(name)
    for obj, points in zip(exports, values):
        key = obj.shape_key_add(name=name)
        key.data.foreach_set('co', points.reshape(-1))
    for control, foot, offset in limbs:
        if (phase+offset)%1 < stance:
            contact_errors.append(abs(rig.pose.bones[foot].matrix.translation.z-foot_origins[control].z))
    print('Baked native walk pose', KIND, frame, flush=True)
for name, wag in [('WagLeft', -.4), ('WagRight', .4)]:
    set_pose(None, wag)
    values = [coords(obj) for obj in sources]
    values.append(fur_rest+(values[0]-rest_body)[attachments])
    pose_names.append(name)
    for obj, points in zip(exports, values):
        key = obj.shape_key_add(name=name)
        key.data.foreach_set('co', points.reshape(-1))
set_pose()

# All trial mesh transforms share one +X forward / Blender Z-up conversion.
root = bpy.data.objects.new('PetDog' if DOG else 'PetCat', None)
scene.collection.objects.link(root)
scale = 1.65
root['studio_pet'] = {'source':str(SOURCE.relative_to(ROOT)), 'kind':KIND,
    'stride':stride/stance*scale, 'walk_poses':16, 'groom_strands':len(fur_vertices)//9,
    'native_paw_contact_error_max':max(contact_errors), 'animation':'Native rig evaluated to morph targets; no cage deformation discarded'}
for obj in exports:
    obj.parent = root
    obj.rotation_euler.z = math.pi/2
    obj.scale = (scale, scale, scale)
    for face in obj.data.polygons:
        face.use_smooth = True
    # Source paint masks have already been evaluated in the baked color graph.
    # glTF vertex colors would multiply these masks into the color a second time.
    for attribute in list(obj.data.color_attributes):
        obj.data.color_attributes.remove(attribute)
    obj.hide_render = False
bpy.ops.object.select_all(action='DESELECT')
root.select_set(True)
for obj in exports:
    obj.select_set(True)
bpy.context.view_layer.objects.active = root
scene.render.image_settings.file_format = 'PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(KIND+'-trial.blend')))
bpy.ops.export_scene.gltf(filepath=str(OUT/(KIND+'-raw.glb')), export_format='GLB', use_selection=True,
    export_apply=False, export_cameras=False, export_lights=False, export_animations=False,
    export_extras=True, export_image_format='WEBP', export_image_quality=90,
    export_morph=True, export_morph_normal=False, export_morph_tangent=False)
(OUT/(KIND+'-conversion.json')).write_text(json.dumps(dict(root['studio_pet']),indent=2))
print('TRIAL COMPLETE', KIND, dict(root['studio_pet']), flush=True)
