from pathlib import Path
import sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v11'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/('scripts/assets/fondfont/blender-v2/factory-truck-'+version+'.blend')))
t=bpy.data.objects['Truck'];keep={t,*t.children_recursive}
for o in list(bpy.data.objects):
 if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
t.location=(0,0,0)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('Truck studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.8,.8,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;m=bpy.data.materials.new('Warm paper');m.diffuse_color=(.87,.87,.84,1);floor.data.materials.append(m)
for pos,power,size in [((3,-4,7),1000,6),((-4,3,5),800,5)]:
 d=bpy.data.lights.new('Softbox','AREA');d.energy=power;d.size=size;o=bpy.data.objects.new('Softbox',d);bpy.context.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Truck studio camera');cam=bpy.data.objects.new('Truck studio camera',d);bpy.context.collection.objects.link(cam);d.type='ORTHO';d.ortho_scale=7.2;s.camera=cam;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
for name,pos in [('three-quarter',(5,7,3.9)),('reference',(6,9,3.9)),('side',(0,-8,2.6))]:
 cam.location=pos;cam.rotation_euler=(Vector((0,0,1.15))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(ROOT/'docs/reviews/fondfont-cute-truck-20261007'/('truck-'+version+'-'+name+'.png'));bpy.ops.render.render(write_still=True)
