"""Render the actual editable pet rig at a walking pose, without image editing."""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scripts/assets/fondfont/blender-v2/garden-life-rig-v5.blend'))
for species,x in [('Dog',-.65),('Cat',.65)]:
    arm=bpy.data.objects['Pet'+species];arm.location.x=x
    for track in arm.animation_data.nla_tracks:
        track.mute=track.name!='Pet'+species+'WalkForward'
scene=bpy.context.scene;scene.frame_set(5)
scene.render.engine='CYCLES';scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.world=scene.world or bpy.data.worlds.new('Study world')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.8,.8,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
bpy.ops.mesh.primitive_plane_add(size=200)
floor=bpy.context.object;floor.name='Study floor'
mat=bpy.data.materials.new('Study warm paper');mat.diffuse_color=(.91,.91,.89,1);floor.data.materials.append(mat)
for position,power,size in [((-1,-2,3),350,4),((2,2,2),200,3)]:
    data=bpy.data.lights.new('Study softbox','AREA');data.energy=power;data.shape='DISK';data.size=size
    light=bpy.data.objects.new('Study softbox',data);bpy.context.collection.objects.link(light);light.location=position
    light.rotation_euler=(Vector((0,0,.3))-light.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('Study camera');camera=bpy.data.objects.new('Study camera',data);bpy.context.collection.objects.link(camera)
camera.location=(1.5,-3.8,2.5);camera.rotation_euler=(Vector((0,0,.29))-camera.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=2.65
scene.camera=camera;scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.render.filepath=str(ROOT/'docs/reviews/fondfont-pets-v5-20261007/pet-native-study.png')
bpy.ops.render.render(write_still=True)
