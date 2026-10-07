"""Rebuild only native forklifts, reusing the complete original material images."""
from pathlib import Path
import ast
import re
import bpy, bmesh, math, importlib.util
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scripts/assets/fondfont/blender-v2'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'factory.blend'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
names={'sage':'imagegen plum enamel','orange':'imagegen FondFont red enamel','ivory':'imagegen limestone trim','mastSteel':'Matte graphite mast','forkSteel':'Forged graphite forks'}
M={name:bpy.data.materials.get(names.get(name,name)) for name in ['iron','orange','sage','steel','lamp','rubber','ivory','black','mastSteel','forkSteel']}
helpers={'P','parent','group','finish','box','mesh','cylinder','torus','rod','uv_box','apply_and_merge'}
source=ast.parse((ROOT/'scripts/build-fondfont-blender.py').read_text())
functions=ast.Module(body=[node for node in source.body if isinstance(node,ast.FunctionDef) and node.name in helpers],type_ignores=[])
exec(compile(functions,'fondfont-native-model-helpers','exec'),globals())
spec=importlib.util.spec_from_file_location('forklift',ROOT/'scripts/fondfont-stacker-model.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.build(globals())
apply_and_merge()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'forklift-rig-v4.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'forklift-rig-v4-raw.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_animations=False,export_extras=True,export_image_format='WEBP',export_image_quality=92)

# Integrate into a versioned complete scene so the browser downloads no duplicate rigs/textures.
bpy.ops.wm.open_mainfile(filepath=str(OUT/'factory.blend'))
for name in ['SourceStacker','ReceiverStacker']:
    root=bpy.data.objects[name]
    for child in list(root.children_recursive):bpy.data.objects.remove(child,do_unlink=True)
    bpy.data.objects.remove(root,do_unlink=True)
with bpy.data.libraries.load(str(OUT/'forklift-rig-v4.blend'),link=False) as (source,target):
    target.objects=list(source.objects)
for obj in target.objects:
    bpy.context.scene.collection.objects.link(obj)
    if obj.type=='MESH':
        for slot in obj.material_slots:
            original=bpy.data.materials.get(re.sub(r'\.\d{3}$','',slot.material.name))
            if original:slot.material=original
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'factory-forklift-v4.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'factory-forklift-v4-raw.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_animations=False,export_extras=True,export_image_format='WEBP',export_image_quality=92)
