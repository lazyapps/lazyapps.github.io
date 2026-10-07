"""Mount the unchanged imagegen optic material on solid, rounded truck lamps."""
from pathlib import Path
import bpy, bmesh, math, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scripts/assets/fondfont/blender-v2'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'factory-truck-v10.blend'))
truck=bpy.data.objects['Truck']
# Retire the old placeholder lenses; keep their solid metal housings.
for o in truck.children:
 if o.type!='MESH':continue
 remove={i for i,m in enumerate(o.data.materials) if m.name in ['Precision truck headlamp reflector','Precision truck amber indicator']}
 if remove:
  bm=bmesh.new();bm.from_mesh(o.data)
  bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index in remove],context='FACES')
  bm.to_mesh(o.data);bm.free()
image=bpy.data.images.load(str(OUT/'truck-headlamp-imagegen-v11.png'),check_existing=True)
image.pack()
m=bpy.data.materials.new('imagegen truck precision lamp optics');m.use_nodes=True
nodes=m.node_tree.nodes;s=nodes.get('Principled BSDF')
s.inputs['Roughness'].default_value=.24;s.inputs['Metallic'].default_value=.25
s.inputs['Coat Weight'].default_value=.4;s.inputs['Coat Roughness'].default_value=.16
tex=nodes.new('ShaderNodeTexImage');tex.image=image;m.node_tree.links.new(tex.outputs['Color'],s.inputs['Base Color'])
# Rounded, subtly bowed native optic surfaces; their metal housings remain solid.
for sign in [-1,1]:
 verts=[];uvs=[];faces=[];N=24
 for row in range(N+1):
  v=row/N;h=1.17+(v-.5)*.287
  for col in range(N+1):
   u=col/N;z=sign*(.59+(u-.5)*.276)
   # A 17mm corner radius controls actual silhouette, rather than an alpha card.
   dh=max(abs(h-1.17)-(.287/2-.017),0)
   dz=max(abs(z-sign*.59)-(.276/2-.017),0)
   if dh and dz:
    excess=max(math.hypot(dh,dz)-.017,0)
    ratio=excess/math.hypot(dh,dz)
    h2=h-math.copysign(dh*ratio,h-1.17);z2=z-math.copysign(dz*ratio,z-sign*.59)
   else:h2,z2=h,z
   x=2.390+.004*(1-(2*u-1)**2)*(1-(2*v-1)**2)
   verts.append((x,-z2,h2));uvs.append((u,v))
 for row in range(N):
  for col in range(N):
   a=row*(N+1)+col;face=(a,a+1,a+N+2,a+N+1)
   faces.append(tuple(reversed(face)) if sign==1 else face)
 d=bpy.data.meshes.new('Native bowed headlight glass');d.from_pydata(verts,[],faces);d.update()
 o=bpy.data.objects.new('Truck imagegen optic '+str(sign),d);bpy.context.collection.objects.link(o);o.parent=truck;d.materials.append(m)
 uv=d.uv_layers.new(name='Whole unchanged imagegen optic')
 for p in d.polygons:
  p.use_smooth=True
  for li in p.loop_indices:uv.data[li].uv=uvs[d.loops[li].vertex_index]
 solid=o.modifiers.new('Solid optic thickness','SOLIDIFY');solid.thickness=.006
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=solid.name)
# Actual under-bed equipment adds depth between the cab and rear axle pair.
def equipment(name,size,at,material,bevel):
 bpy.ops.mesh.primitive_cube_add(size=1)
 o=bpy.context.object;o.name=name;o.parent=truck
 o.location=(at[0],-at[2],at[1]);o.scale=(size[0],size[2],size[1])
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(bpy.data.materials[material])
 mod=o.modifiers.new('Rolled equipment corners','BEVEL');mod.width=bevel;mod.segments=5
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 for face in o.data.polygons:face.use_smooth=True
 mod=o.modifiers.new('Equipment face normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
equipment('Satin under-bed fuel tank',(.72,.33,.30),(.23,.59,-.67),'Precision truck satin aluminum',.055)
for x in [-.02,.48]:equipment('Fuel tank retaining strap',(.035,.345,.315),(x,.59,-.67),'Precision truck window rubber',.008)
equipment('Opposite chassis battery case',(.60,.29,.26),(.23,.58,.67),'Precision truck window rubber',.025)
truck['headlamp_source']='truck-headlamp-imagegen-v11.png'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'factory-truck-v11.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.name!='Cab editable quad cage':o.select_set(True)
bpy.ops.export_scene.gltf(use_selection=True,filepath=str(OUT/'factory-truck-v11-raw.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_animations=False,export_extras=True,export_image_format='WEBP',export_image_quality=90)
print(json.dumps({'model':'factory-truck-v11','source':image.filepath,'unchanged_sha256':hashlib.sha256((OUT/'truck-headlamp-imagegen-v11.png').read_bytes()).hexdigest()}))
