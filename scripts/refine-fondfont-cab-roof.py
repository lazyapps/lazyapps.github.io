"""Keep the cab roof as plain painted metal with the original symbol at runtime."""
from pathlib import Path
import bpy
import bmesh

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'scripts/assets/fondfont/blender-v2'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE / 'factory-building-v5.blend'))
truck = bpy.data.objects['Truck']
bpy.context.view_layer.update()
to_truck = truck.matrix_world.inverted()
paint = bpy.data.materials.new('Clean cab roof enamel')
paint.use_nodes = True
shader = paint.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value = (.95, .022, .045, 1)
shader.inputs['Roughness'].default_value = .55
shader.inputs['Metallic'].default_value = .06
roof_faces = 0
removed_faces = 0
for obj in truck.children_recursive:
    if obj.type != 'MESH':
        continue
    transform = to_truck @ obj.matrix_world
    if obj.name == 'Truck_lamp':
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        markers = [f for f in bm.faces if all((transform @ v.co).z > 2.29 for v in f.verts)]
        removed_faces += len(markers)
        bmesh.ops.delete(bm, geom=markers, context='FACES')
        bm.to_mesh(obj.data)
        bm.free()
    if obj.name == 'Truck_imagegen FondFont red enamel':
        obj.data.materials.append(paint)
        for face in obj.data.polygons:
            if all((transform @ obj.data.vertices[i].co).z > 2.19 for i in face.vertices):
                face.material_index = len(obj.data.materials) - 1
                roof_faces += 1
assert roof_faces > 0 and removed_faces > 0
print('Plain roof faces:', roof_faces, 'removed marker faces:', removed_faces)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE / 'factory-building-v6.blend'))
bpy.ops.export_scene.gltf(filepath=str(SOURCE / 'factory-building-v6-raw.glb'), export_format='GLB', export_apply=True, export_cameras=False, export_lights=False, export_animations=False, export_extras=True, export_image_format='WEBP', export_image_quality=92)
