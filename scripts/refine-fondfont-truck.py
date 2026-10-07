"""Precision cab, glass and wheel assembly from the preserved imagegen truck board."""
from pathlib import Path
import bpy,bmesh,math,json
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'scripts/assets/fondfont/blender-v2'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'factory-building-v6.blend'))
truck=bpy.data.objects['Truck'];bpy.context.view_layer.update();to_truck=truck.matrix_world.inverted()
contract={o.name:(o.parent.name if o.parent else None,list(o.location),list(o.rotation_euler),list(o.scale)) for o in truck.children_recursive if o.type=='EMPTY'}
def P(v):return (v[0],-v[2],v[1])
def mat(name,color,rough=.4,metal=0,alpha=1):
 m=bpy.data.materials.new('Precision truck '+name);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');rgb=[int(color[i:i+2],16)/255 for i in (1,3,5)];rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb];s.inputs['Base Color'].default_value=(*rgb,alpha);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal
 if alpha<1:
  s.inputs['Alpha'].default_value=alpha;m.surface_render_method='DITHERED'
 return m
red=bpy.data.materials['imagegen FondFont red enamel'].copy();red.name='Precision truck original imagegen red enamel';shader=red.node_tree.nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.28;shader.inputs['Metallic'].default_value=.12;shader.inputs['Coat Weight'].default_value=.28;shader.inputs['Coat Roughness'].default_value=.2
silver=mat('satin aluminum','#aeb4b8',.3,.78);chrome=mat('polished edges','#d4d9dc',.21,.88);graphite=mat('graphite gate','#3c3b40',.55,.14);rubber=mat('soft tire rubber','#26262a',.83);gasket=mat('window rubber','#25262a',.68);glass=mat('smoked glazing','#81979f',.15,0,.33);lamp=mat('headlamp reflector','#eceee9',.2,.38);amber=mat('amber indicator','#ffad3e',.27);seat=mat('woven graphite seats','#46464b',.88);inside=mat('dark interior','#29292e',.8)
def finish(o,name,material,par=truck,bevel=0):
 o.name=name;o.parent=par;o.data.materials.clear();o.data.materials.append(material)
 if bevel:
  m=o.modifiers.new('Machined soft edges','BEVEL');m.width=bevel;m.segments=5
 for p in o.data.polygons:p.use_smooth=True
 m=o.modifiers.new('Manufactured face normals','WEIGHTED_NORMAL');m.keep_sharp=True
 return o
def box(name,size,at,material,par=truck,bevel=.012):
 bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.location=P(at);o.scale=P((size[0],size[1],-size[2]));o.scale=tuple(abs(v) for v in o.scale);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,material,par,bevel)
def mesh(name,verts,faces,material,par=truck,bevel=0):
 d=bpy.data.meshes.new(name);d.from_pydata([P(v) for v in verts],[],faces);d.update();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);return finish(o,name,material,par,bevel)
def extrude(name,profile,lo,hi,material,par=truck,bevel=.025):
 n=len(profile);verts=[(x,h,z) for z in [lo,hi] for x,h in profile];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];o=mesh(name,verts,faces,material,par,bevel)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o
def tube(name,points,r,material,par=truck,closed=False):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=1;d.bevel_depth=r;d.bevel_resolution=4;d.use_fill_caps=True;s=d.splines.new('POLY');s.points.add(len(points)-1)
 for q,p in zip(s.points,points):q.co=(*P(p),1)
 s.use_cyclic_u=closed;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.parent=par;d.materials.append(material);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o
def rounded(poly,r=.04):
 result=[]
 for i,b in enumerate(poly):
  a=Vector(poly[i-1]);b=Vector(b);c=Vector(poly[(i+1)%len(poly)]);u=(a-b).normalized();v=(c-b).normalized();a=b+u*r;c=b+v*r
  for j in range(7):t=j/6;result.append(tuple((1-t)**2*a+2*t*(1-t)*b+t*t*c))
 return result
def cyl(name,r,depth,at,material,par=truck,axis='z',segments=64):
 bpy.ops.mesh.primitive_cylinder_add(vertices=segments,radius=r,depth=depth);o=bpy.context.object;o.location=P(at)
 if axis=='x':o.rotation_euler[1]=math.pi/2
 elif axis=='z':o.rotation_euler[0]=math.pi/2
 return finish(o,name,material,par,.004)
def ring(name,r,minor,at,material,par=truck,axis='z'):
 bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=12,major_radius=r,minor_radius=minor);o=bpy.context.object;o.location=P(at)
 if axis=='z':o.rotation_euler[0]=math.pi/2
 elif axis=='x':o.rotation_euler[1]=math.pi/2
 return finish(o,name,material,par)
# Original joined meshes retain disconnected component boundaries. Select whole components.
removed=0
for o in list(truck.children):
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();transform=to_truck@o.matrix_world;seen=set();discard=[]
 for start in bm.verts:
  if start in seen:continue
  stack=[start];component=[];seen.add(start)
  while stack:
   v=stack.pop();component.append(v)
   for e in v.link_edges:
    q=e.other_vert(v)
    if q not in seen:seen.add(q);stack.append(q)
  coords=[transform@v.co for v in component]
  if min(v.x for v in coords)>.78 and min(v.z for v in coords)>.65:
   discard.extend(component)
 removed+=len(discard);bmesh.ops.delete(bm,geom=discard,context='VERTS');bm.to_mesh(o.data);bm.free()
# Real hollow shell and cut windows, rather than dark planes on a solid box.
profile=[(.83,.80),(.83,2.12),(.94,2.28),(1.14,2.34),(1.94,2.34),(2.12,2.20),(2.31,1.58),(2.34,.88),(2.22,.79)]
cab=extrude('Precision cab continuous shell',profile,-.80,.80,red,bevel=0)
def subtract(cutter):
 bpy.context.view_layer.objects.active=cab;m=cab.modifiers.new('Actual window opening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cutter,do_unlink=True)
subtract(box('Interior cavity',(1.14,.75,1.38),(1.50,1.79,0),inside,bevel=0))
side=rounded([(.99,1.61),(1.02,2.09),(1.14,2.19),(1.89,2.19),(2.03,2.10),(2.16,1.62)])
subtract(extrude('Side window aperture',side,-1.1,1.1,gasket,bevel=0))
front=rounded([(-.69,1.65),(.69,1.65),(.65,2.13),(-.65,2.13)],.045)
def front_x(h):return 2.31-(h-1.58)*(.19/.62)
verts=[(front_x(h)+offset,h,z) for offset in [-.12,.18] for z,h in front];n=len(front);faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
cut=mesh('Front opening',verts,faces,gasket);bm=bmesh.new();bm.from_mesh(cut.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cut.data);bm.free();subtract(cut)
bpy.context.view_layer.objects.active=cab;m=cab.modifiers.new('Rounded pressed cab corners','BEVEL');m.width=.055;m.segments=6;m.affect='EDGES'
# UVs keep the original complete imagegen enamel on the rebuilt body.
uv=cab.data.uv_layers.new(name='Original enamel surface')
for poly in cab.data.polygons:
 for li in poly.loop_indices:
  p=cab.data.vertices[cab.data.loops[li].vertex_index].co;uv.data[li].uv=(p.x*.5,p.z*.5)
# A plain enamel roof keeps the app symbol legible without a texture panel.
cab.data.materials.append(bpy.data.materials['Clean cab roof enamel'])
roof_material_index=len(cab.data.materials)-1
for poly in cab.data.polygons:
 if all(cab.data.vertices[i].co.z>2.27 for i in poly.vertices):poly.material_index=roof_material_index
for sign in [-1,1]:
 z=sign*.804
 mesh('Recessed side glazing',[(x,h,z) for x,h in side],[tuple(range(len(side)))],glass)
 tube('Slim side window gasket',[(x,h,z+sign*.006) for x,h in side],.013,gasket,closed=True)
 tube('Pressed door fine seam',[(.945,.90,z+sign*.003),(.945,1.55,z+sign*.003),(.975,2.10,z+sign*.003),(1.13,2.23,z+sign*.003),(1.93,2.23,z+sign*.003),(2.10,2.11,z+sign*.003),(2.20,1.53,z+sign*.003),(2.17,1.04,z+sign*.003),(1.76,.90,z+sign*.003)],.0045,graphite)
 box('Recessed door handle',(.075,.15,.022),(1.06,1.35,z+sign*.008),gasket,bevel=.014)
 box('Small satin handle',(.018,.095,.027),(1.06,1.35,z+sign*.022),silver,bevel=.007)
 box('Satin boarding step',(.74,.065,.18),(1.27,.70,sign*.79),silver,bevel=.025)
 for j in range(5):box('Step grip',(.58,.008,.008),(1.27,.736,sign*(.74+j*.02)),rubber,bevel=.003)
 tube('Fine mirror support',[(2.06,1.88,z),(2.17,1.89,sign*1.02),(2.17,1.64,sign*1.02)],.012,gasket)
 box('Rounded mirror housing',(.11,.28,.12),(2.17,1.79,sign*1.055),gasket,bevel=.038)
 box('Mirror inset',(.014,.23,.085),(2.225,1.79,sign*1.055),chrome,bevel=.022)
 # Fine front fender contour joins the existing physical wheel arch.
 arc=[(1.62+.55*math.cos(j*math.pi/40),.435+.55*math.sin(j*math.pi/40),sign*.822) for j in range(41)]
 tube('Integrated front arch lip',arc,.016,red)
mesh('Single broad front glazing',[(front_x(h)+.004,h,z) for z,h in front],[tuple(range(n))],glass)
tube('Front gasket recess',[(front_x(h)+.009,h,z) for z,h in front],.014,gasket,closed=True)
for sign in [-1,1]:
 tube('Windshield wiper arm',[(front_x(1.67)+.02,1.67,sign*.39),(front_x(1.80)+.025,1.80,sign*.20)],.008,gasket)
 tube('Fine wiper blade',[(front_x(1.79)+.027,1.79,sign*.11),(front_x(1.82)+.027,1.82,sign*.43)],.009,gasket)
 box('Headlamp satin recess',(.045,.30,.29),(2.335,1.17,sign*.59),silver,bevel=.038)
 box('Headlamp lower lens',(.050,.115,.245),(2.36,1.085,sign*.59),lamp,bevel=.025)
 box('Headlamp upper lens',(.050,.115,.245),(2.36,1.23,sign*.59),lamp,bevel=.025)
 box('Small amber turn lamp',(.055,.045,.075),(2.37,1.23,sign*.675),amber,bevel=.012)
 box('Cloth seat cushion',(.35,.095,.37),(1.32,1.36,sign*.36),seat,bevel=.045)
 box('Seat back',(.12,.48,.37),(1.13,1.62,sign*.36),seat,bevel=.055)
 box('Headrest',(.12,.17,.25),(1.13,1.96,sign*.36),seat,bevel=.045)
box('Dashboard',(.22,.14,1.37),(2.00,1.56,0),inside,bevel=.045)
ring('Steering wheel',.12,.013,(1.84,1.66,-.36),gasket,axis='x')
box('Fine inset grille',(.038,.21,.78),(2.347,1.20,0),gasket,bevel=.025)
for j in range(4):box('Satin grille slat',(.045,.012,.72),(2.372,1.13+j*.043,0),silver,bevel=.005)
box('Slim satin bumper',( .15,.14,1.77),(2.32,.87,0),silver,bevel=.045)
box('Lower air opening',(.018,.075,.72),(2.402,.872,0),gasket,bevel=.018)
# Smooth sidewalls and real recessed metal wheel dishes; retain every motion pivot.
for steer in [o for o in truck.children if o.name.startswith('Steer_')]:
 spin=steer.children[0]
 for o in list(spin.children_recursive):bpy.data.objects.remove(o,do_unlink=True)
 cyl('Continuous tire body',.397,.225,(0,0,0),rubber,spin)
 ring('Rounded tire shoulder',.350,.085,(0,0,0),rubber,spin)
 for sign in [-1,1]:
  ring('Fine sidewall molding',.345,.004,(0,0,sign*.116),rubber,spin)
  # Revolved dish profile provides depth and a clean rolled metal lip.
  profile=[(.06,.127),(.10,.127),(.13,.114),(.19,.102),(.22,.117),(.24,.125),(.248,.122),(.248,.112),(.22,.103),(.18,.091),(.12,.101),(.06,.114)]
  verts=[(r*math.cos(j*math.tau/64),r*math.sin(j*math.tau/64),sign*d) for r,d in profile for j in range(64)];faces=[]
  for k in range(len(profile)):
   for j in range(64):a=k*64+j;b=k*64+(j+1)%64;c=((k+1)%len(profile))*64+(j+1)%64;d=((k+1)%len(profile))*64+j;faces.append((a,b,c,d))
  mesh('Recessed satin wheel dish',verts,faces,silver,spin)
  ring('Rolled polished wheel rim',.240,.008,(0,0,sign*.123),chrome,spin)
  cyl('Graphite hub center',.068,.035,(0,0,sign*.133),gasket,spin)
  for j in range(6):
   a=j*math.tau/6
   cyl('Recessed wheel ventilation',.029,.008,(math.cos(a)*.175,math.sin(a)*.175,sign*.112),gasket,spin,segments=32)
   cyl('Machined six lug nut',.014,.016,(math.cos(a)*.10,math.sin(a)*.10,sign*.137),chrome,spin,segments=6)
# Graphite gate centers with preserved red stakes and exact moving gate owner.
for owner in [truck,bpy.data.objects['LoadingSideGate']]:
 for o in list(owner.children):
  if o.type!='MESH' or o.name.startswith('Precision'):continue
  o.data.materials.append(graphite);material_index=len(o.data.materials)-1
  bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();seen=set();transform=to_truck@o.matrix_world
  for start in bm.verts:
   if start in seen:continue
   stack=[start];component=[];seen.add(start)
   while stack:
    v=stack.pop();component.append(v)
    for e in v.link_edges:
     q=e.other_vert(v)
     if q not in seen:seen.add(q);stack.append(q)
   coords=[transform@v.co for v in component];lo=[min(v[k] for v in coords) for k in range(3)];hi=[max(v[k] for v in coords) for k in range(3)]
   if hi[0]<.81 and lo[2]>1.02 and hi[2]<1.45 and hi[2]-lo[2]>.3 and (hi[0]-lo[0]>3 or hi[1]-lo[1]>1.7):
    for f in {f for v in component for f in v.link_faces}:f.material_index=material_index
  bm.to_mesh(o.data);bm.free()
# Invariant: native rig attachment nodes retain their exact local transforms.
for name,record in contract.items():
 o=bpy.data.objects[name];assert (o.parent.name if o.parent else None,list(o.location),list(o.rotation_euler),list(o.scale))==record,name
truck['precision_reference']='truck-precision-reference-v7.png';truck['wheel_radius']=.435
# This paint anchor is static, not an animation pivot. Register it to the new roof.
bpy.data.objects['CabRoofName'].location.z=2.349
# Join only static surfaces sharing a motion owner, after applying their edge modifiers.
for owner in [truck]+[o for o in truck.children_recursive if o.name.startswith('Wheel_')]:
 objects=[o for o in owner.children if o.type=='MESH']
 for o in objects:
  bpy.context.view_layer.objects.active=o
  for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 if objects:
  bpy.ops.object.select_all(action='DESELECT')
  for o in objects:o.select_set(True)
  bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();objects[0].name='Precision '+owner.name+' surfaces'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'factory-truck-v8.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'factory-truck-v8-raw.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_animations=False,export_extras=True,export_image_format='WEBP',export_image_quality=92)
print(json.dumps({'removed_cab_vertices':removed,'preserved_motion_nodes':len(contract),'wheel_radius':.435}))
