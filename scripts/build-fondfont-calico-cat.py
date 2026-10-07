"""Export JonasDichelle's CC BY 3.0 cat using its original surfaces and native IK.

Blender --background --disable-autoexec --python scripts/build-fondfont-calico-cat.py
The downloaded source remains untouched. Original textures and combed hair are
retained; triangle frames bind the groom to each evaluated deformation.
"""
from pathlib import Path
import math
import json
import bpy
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'scripts/assets/fondfont/pets/calico-cat'
bpy.ops.wm.open_mainfile(filepath=str(OUT / 'source.blend'), use_scripts=False)
scene = bpy.context.scene
rig = bpy.data.objects['Armature']
body = bpy.data.objects['Cat']
sources = [body, bpy.data.objects['Sphere'], bpy.data.objects['Sphere.001']]
for track in rig.animation_data.nla_tracks:
    track.mute = True
rig.animation_data.action = None
# Old 2.77 rig constraints form feedback loops in current Blender.
for name, kind in [('Tail', 'COPY_ROTATION'), ('Spine', 'PIVOT')]:
    for constraint in list(rig.pose.bones[name].constraints):
        if constraint.type == kind:
            rig.pose.bones[name].constraints.remove(constraint)
for bone in rig.pose.bones:
    bone.matrix_basis = Matrix.Identity(4)
for obj in sources:
    for modifier in obj.modifiers:
        if modifier.type == 'SUBSURF':
            modifier.levels = modifier.render_levels = 1
for system in body.particle_systems:
    system.settings.child_percent = system.settings.rendered_child_count = 0
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()

def coords(obj):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
    values = np.empty(len(mesh.vertices)*3, dtype=np.float32)
    mesh.vertices.foreach_get('co', values)
    matrix = np.array(obj.matrix_world)
    values = values.reshape((-1, 3)) @ matrix[:3, :3].T + matrix[:3, 3]
    evaluated.to_mesh_clear()
    return values

limbs = [('Foot_front_IK_L', 'Foot_front_L', 0),
         ('Foot_front_IK_R', 'Foot_front_R', .5),
         ('Foot_Back_IK_L', 'Foot_Back_L2', .75),
         ('Foot_Back_IK_R', 'Foot_Back_L2.002', .25)]
base = {name: rig.pose.bones[name].matrix.copy() for name, _, _ in limbs}
feet = {name: rig.pose.bones[foot].matrix.translation.copy() for name, foot, _ in limbs}
tail = rig.pose.bones['Tail_controller']
head = rig.pose.bones['Head_controller']
tail_base, head_base = tail.matrix.copy(), head.matrix.copy()

def rotate_at(matrix, origin, angle):
    return Matrix.Translation(origin) @ Matrix.Rotation(angle, 4, 'Z') @ Matrix.Translation(-origin) @ matrix

def solve(name, foot, target, rotation=0):
    control = rig.pose.bones[name]
    if rotation:
        control.matrix = rotate_at(base[name], feet[name], rotation)
        bpy.context.view_layer.update()
    for _ in range(12):
        delta = target - rig.pose.bones[foot].matrix.translation
        if delta.length < .00001:
            break
        matrix = control.matrix.copy()
        matrix.translation += delta
        control.matrix = matrix
        bpy.context.view_layer.update()

# Calibrate each original skin sole, rather than the armature endpoint, to ground.
initial = coords(body)
floor = float(initial[:, 2].min())
for name, foot, _ in limbs:
    p = np.array(feet[name])
    patch = np.where(np.linalg.norm(initial[:, :2]-p[:2], axis=1) < .65)[0]
    assert len(patch) > 3, name
    target = feet[name].copy()
    for _ in range(5):
        sole = float(coords(body)[patch, 2].min())
        target.z += floor-sole
        solve(name, foot, target)
    base[name] = rig.pose.bones[name].matrix.copy()
    feet[name] = rig.pose.bones[foot].matrix.translation.copy()

def reset():
    for name, _, _ in limbs:
        rig.pose.bones[name].matrix = base[name].copy()
    tail.matrix, head.matrix = tail_base.copy(), head_base.copy()
    bpy.context.view_layer.update()

reset()
rest_body = coords(body)
exports = []
for obj, name in zip(sources, ['CalicoCatBody', 'CalicoCatEyeL', 'CalicoCatEyeR']):
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph), preserve_all_data_layers=True, depsgraph=depsgraph)
    mesh.transform(obj.matrix_world)
    copy = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(copy)
    exports.append(copy)

def pbr(name, image, roughness):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value = roughness
    texture = material.node_tree.nodes.new('ShaderNodeTexImage')
    texture.image = image
    material.node_tree.links.new(texture.outputs['Color'], shader.inputs['Base Color'])
    return material

# Use the exact packed coat painting. Native baking evaluates the original eye
# color graph, including its generated-coordinate mapping and RGB curves.
coat = pbr('CalicoCat-original-coat', bpy.data.images['Untitled'], .85)
exports[0].data.materials.clear()
exports[0].data.materials.append(coat)
for face in exports[0].data.polygons:
    face.material_index = 0
scene.render.engine = 'CYCLES'
scene.cycles.samples = 1
scene.render.bake.margin = 4
for obj in exports[1:]:
    material = obj.data.materials[0].copy()
    obj.data.materials.clear()
    obj.data.materials.append(material)
    nodes, links = material.node_tree.nodes, material.node_tree.links
    emission = nodes.new('ShaderNodeEmission')
    links.new(nodes.get('RGB Curves').outputs['Color'], emission.inputs['Color'])
    links.new(emission.outputs[0], nodes.get('Material Output').inputs['Surface'])
    image = bpy.data.images.new(obj.name+'-original-eye', width=512, height=512)
    texture = nodes.new('ShaderNodeTexImage')
    texture.image = image
    nodes.active = texture
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.bake(type='EMIT')
    image.pack()
    obj.data.materials.clear()
    obj.data.materials.append(pbr(obj.name+'-PBR', image, .24))

# Original groom: bind each strand to the full local triangle frame, so it
# rotates and stretches with the native evaluated skin, including head/tail.
evaluated = body.evaluated_get(depsgraph)
mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
mesh.calc_loop_triangles()
triangles = np.array([tuple(t.vertices) for t in mesh.loop_triangles], dtype=np.int32)
uvs = np.zeros((len(rest_body), 2), dtype=np.float32)
for loop in mesh.loops:
    uvs[loop.vertex_index] = mesh.uv_layers.active.data[loop.index].uv
bvh = BVHTree.FromPolygons([Vector(p) for p in rest_body], triangles.tolist(), all_triangles=True)
evaluated.to_mesh_clear()
vertices, faces, fur_uvs, bindings = [], [], [], []
for system in body.evaluated_get(depsgraph).particle_systems:
    for particle in system.particles:
        keys = [body.matrix_world @ key.co for key in particle.hair_keys]
        if len(keys) < 2 or (keys[-1]-keys[0]).length < .0002:
            continue
        root, middle, tip = keys[0], keys[len(keys)//2], keys[-1]
        _, _, index, _ = bvh.find_nearest(root)
        triangle = triangles[index]
        nearest = min(triangle, key=lambda i: (Vector(rest_body[i])-root).length_squared)
        tangent = (tip-root).normalized()
        side = tangent.cross(Vector((0, 0, 1)))
        if side.length < .01:
            side = tangent.cross(Vector((1, 0, 0)))
        side.normalize()
        other = tangent.cross(side).normalized()
        start = len(vertices)
        width = .009 if system.name == 'ParticleSystem' else .006
        for point, radius in [(root, width), (middle, width*.55), (tip, .00025)]:
            for corner in range(3):
                angle = corner*math.tau/3
                vertices.append(tuple(point+radius*(math.cos(angle)*side+math.sin(angle)*other)))
                fur_uvs.append(uvs[nearest])
                bindings.append(triangle)
        for segment in range(2):
            for corner in range(3):
                a, b = start+segment*3+corner, start+segment*3+(corner+1)%3
                faces.append((a, b, b+3, a+3))
fur_mesh = bpy.data.meshes.new('Original calico groom')
fur_mesh.from_pydata(vertices, [], faces)
fur_mesh.update()
fur = bpy.data.objects.new('CalicoCatOriginalGroom', fur_mesh)
scene.collection.objects.link(fur)
fur_mesh.materials.append(coat)
uv = fur_mesh.uv_layers.new()
for loop in fur_mesh.loops:
    uv.data[loop.index].uv = fur_uvs[loop.vertex_index]
exports.append(fur)
fur_rest = np.array(vertices)
bindings = np.array(bindings)

def frames(points):
    tri = points[bindings]
    a, b = tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]
    n = np.cross(a, b)
    n /= np.sqrt(np.maximum(np.linalg.norm(n, axis=1), 1e-10))[:, None]
    return tri[:, 0], np.stack([a, b, n], axis=2)

origins, matrices = frames(rest_body)
fur_local = np.einsum('nij,nj->ni', np.linalg.inv(matrices), fur_rest-origins)

def groom(points):
    origins, matrices = frames(points)
    return origins+np.einsum('nij,nj->ni', matrices, fur_local)

for obj in exports:
    obj.shape_key_add(name='Basis')
stance, stride, turn_angle = .65, 2.45, math.pi/3
phases = sorted({round(i/16, 8) for i in range(16)} | {round((stance-offset)%1, 8) for _, _, offset in limbs})

def gait(phase, turn=0):
    reset()
    for name, foot, offset in limbs:
        q = (phase+offset)%1
        if q < stance:
            travel, lift = q/stance-.5, 0
            theta = -turn*turn_angle*(q-stance/2)
        else:
            t = (q-stance)/(1-stance)
            travel = .5-t*t*(3-2*t)
            lift = .40*math.sin(math.pi*t)**1.5
            h00, h10, h01, h11 = 2*t**3-3*t*t+1, t**3-2*t*t+t, -2*t**3+3*t*t, t**3-t*t
            theta = turn*turn_angle*(-stance/2*h00-(1-stance)*h10+stance/2*h01-(1-stance)*h11)
        target = feet[name].copy()
        if turn:
            origin = Vector((0, .55, 0))
            target = origin+Matrix.Rotation(theta, 3, 'Z')@(target-origin)
        else:
            target.y += stride*travel
        target.z += lift
        solve(name, foot, target, theta if turn else 0)

contact_error = 0
def capture(name):
    values = [coords(obj) for obj in sources]
    values.append(groom(values[0]))
    for obj, points in zip(exports, values):
        obj.shape_key_add(name=name).data.foreach_set('co', points.reshape(-1))
    print('Native cat pose', name, flush=True)

for bank, turn in [('Walk', 0), ('TurnLeft', 1), ('TurnRight', -1)]:
    for i, phase in enumerate(phases):
        gait(phase, turn)
        capture(bank+str(i).zfill(2))
        for name, foot, offset in limbs:
            if (phase+offset)%1 < stance:
                contact_error = max(contact_error, abs(rig.pose.bones[foot].matrix.translation.z-feet[name].z))
for name, angle in [('WagLeft', -.25), ('WagRight', .25)]:
    reset()
    tail.matrix = rotate_at(tail_base, Vector((0, 3, 2.5)), angle)
    bpy.context.view_layer.update()
    capture(name)
head_angle = .32
for name, angle in [('HeadLeft', head_angle), ('HeadRight', -head_angle)]:
    reset()
    head.matrix = rotate_at(head_base, head_base.translation, angle)
    bpy.context.view_layer.update()
    capture(name)
for i, (name, foot, _) in enumerate(limbs):
    for axis in range(3):
        reset()
        target = feet[name].copy()
        target[axis] += .38
        solve(name, foot, target)
        capture('Plant'+str(i)+'XYZ'[axis])
    for suffix, angle in [('Yaw', .6), ('YawRight', -.6)]:
        reset()
        solve(name, foot, feet[name], angle)
        capture('Plant'+str(i)+suffix)
reset()

scale, center_y = .065, .55
def web(p):
    return [-(float(p[1])-center_y)*scale, (float(p[2])-floor)*scale, -float(p[0])*scale]
markers = []
for i, (name, foot, offset) in enumerate(limbs):
    p = np.array(feet[name])
    patch = np.where(np.linalg.norm(rest_body[:, :2]-p[:2], axis=1) < .65)[0]
    lowest = float(rest_body[patch, 2].min())
    patch = patch[rest_body[patch, 2] < lowest+.045]
    toe = int(min(patch, key=lambda j: rest_body[j, 1]))
    heel = int(max(patch, key=lambda j: rest_body[j, 1]))
    edge = rest_body[heel, :2]-rest_body[toe, :2]
    side = int(max(patch, key=lambda j: abs(float(np.cross(edge, rest_body[j, :2]-rest_body[toe, :2])))))
    indices = [toe, heel, side]
    assert len(set(indices)) == 3, (name, indices)
    markers.append({'offset': offset, 'markers': [web(rest_body[j]) for j in indices], 'source_vertices': indices,
                    'correction': ['Plant'+str(i)+a for a in ['X', 'Y', 'Z', 'Yaw', 'YawRight']]})
root = bpy.data.objects.new('PetCat', None)
scene.collection.objects.link(root)
metadata = {'version': 3, 'kind': 'cat', 'body_mesh': 'CalicoCatBody', 'stride': stride/stance*scale,
            'source': 'Rigged and animated Cat by JonasDichelle / CC BY 3.0', 'source_url': 'https://blendswap.com/blend/18519',
            'walk_poses': len(phases), 'phases': phases, 'stance': stance, 'turn_angle': turn_angle,
            'head_angle': head_angle, 'feet': markers, 'groom_strands': len(vertices)//9,
            'groom_binding': 'Evaluated triangle deformation frames',
            'native_paw_contact_error_max': contact_error*scale,
            'animation': 'Original native IK adapted to grounded walk, pivot and world-plant poses; not the unmodified authored Walk action'}
root['studio_pet'] = metadata
for obj in exports:
    obj.parent = root
    obj.rotation_euler.z = math.pi/2
    obj.scale = (scale, scale, scale)
    obj.location = (center_y*scale, 0, -floor*scale)
    for face in obj.data.polygons:
        face.use_smooth = True
    for attribute in list(obj.data.color_attributes):
        obj.data.color_attributes.remove(attribute)
    for key in obj.data.shape_keys.key_blocks:
        key.value = 0
    obj.hide_render = False
bpy.ops.object.select_all(action='DESELECT')
root.select_set(True)
for obj in exports:
    obj.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'cat-web-v1.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT / 'cat-web-v1-raw.glb'), export_format='GLB', use_selection=True,
    export_apply=False, export_cameras=False, export_lights=False, export_animations=False, export_extras=True,
    export_image_format='WEBP', export_image_quality=90, export_morph=True, export_morph_normal=False, export_morph_tangent=False)
(OUT / 'cat-web-v1.json').write_text(json.dumps(metadata, indent=2))
print('CALICO COMPLETE', metadata, flush=True)
