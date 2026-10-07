"""Use the complete imagegen face on a rounded, rigged puppy head; preserve v5 clips."""
from pathlib import Path
import bpy,bmesh,math,json
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scripts/assets/fondfont/blender-v2'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'garden-life-rig-v5.blend'))
arm=bpy.data.objects['PetDog'];skin=bpy.data.objects['PetDogSkin'];head='PetDogHead'
head_group=skin.vertex_groups[head].index
# The source joins anatomy by material. Remove head surfaces only; retain floppy ears.
remove=set()
for vertex in skin.data.vertices:
    if any(g.group==head_group and g.weight>.99 for g in vertex.groups):remove.add(vertex.index)
bm=bmesh.new();bm.from_mesh(skin.data);bm.verts.ensure_lookup_table()
faces=[f for f in bm.faces if all(v.index in remove for v in f.verts) and 'puppy ears' not in skin.data.materials[f.material_index].name]
bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(skin.data);bm.free()
# A short, plump muzzle belongs to the same smooth head volume.
origin=arm.data.bones[head].matrix_local.translation.copy()
parts=[]
for at,scale in [((.018,.030,0),(.142,.145,.145)),((.119,-.023,0),(.065,.065,.082)),((.105,-.021,-.048),(.058,.060,.059)),((.105,-.021,.048),(.058,.060,.059))]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32,location=origin+Vector((at[0],-at[2],at[1])))
    o=bpy.context.object;o.scale=(scale[0],scale[2],scale[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);parts.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();face=parts[0];face.name='Imagegen puppy rounded face'
remesh=face.modifiers.new('Continuous baby cheeks','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.0035;remesh.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=remesh.name)
smooth=face.modifiers.new('Soft muzzle transitions','SMOOTH');smooth.factor=.85;smooth.iterations=4;bpy.ops.object.modifier_apply(modifier=smooth.name)
# Front surface uses the whole original texture. Side/back occupy its plain fur margin.
image=bpy.data.images.load(str(OUT/'puppy-face-imagegen-v6.png'));image.pack()
mat=bpy.data.materials.new('Imagegen puppy face original v6');mat.use_nodes=True
shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.86
texture=mat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image;texture.extension='EXTEND';mat.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
face.data.materials.append(mat);uv=face.data.uv_layers.new(name='Puppy face front and plain-fur back')
for poly in face.data.polygons:
    front=all((face.matrix_world@face.data.vertices[i].co-origin).x>-.005 for i in poly.vertices)
    for li in poly.loop_indices:
        p=face.matrix_world@face.data.vertices[face.data.loops[li].vertex_index].co-origin
        if front:
            # generated eyes y40%, nose57%, mouth66%; texture V points upwards.
            uv.data[li].uv=(.5-p.y/.34,.5+(p.z-.020)/.32)
        else:uv.data[li].uv=(.035+.035*(p.y/.15+1)/2,.12+.16*(p.z/.15+1)/2)
    poly.use_smooth=True
face.vertex_groups.new(name=head).add(list(range(len(face.data.vertices))),1,'REPLACE')
face.parent=arm;mod=face.modifiers.new('Original head bone','ARMATURE');mod.object=arm
face['imagegen_source']='puppy-face-imagegen-v6.png';face['original_head_bone']=head
# Match the older body without losing the imagegen expression or changing its pixels.
# Ears stay native and keep their original skeleton weighting.
arm['face_texture']='puppy-face-imagegen-v6.png'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'garden-life-rig-v6.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'garden-life-rig-v6-raw.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_animations=True,export_animation_mode='NLA_TRACKS',export_extras=True,export_force_sampling=True,export_image_format='WEBP',export_image_quality=92)
print('Saved imagegen puppy head, preserved',len(arm.animation_data.nla_tracks),'dog clips')
