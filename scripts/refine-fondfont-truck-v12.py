"""Precision cab, glass and wheel assembly from the preserved imagegen truck board."""
from pathlib import Path
import bpy,bmesh,math,json,runpy
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
silver=mat('satin aluminum','#c1c7cb',.25,.85);chrome=mat('polished edges','#d4d9dc',.21,.88);graphite=mat('graphite gate','#3c3b40',.55,.14);rubber=mat('soft tire rubber','#17191c',.78);gasket=mat('window rubber','#25262a',.68);glass=mat('smoked glazing','#81979f',.15,0,.33);lamp=mat('headlamp reflector','#eceee9',.2,.38);amber=mat('amber indicator','#ffad3e',.27);seat=mat('woven graphite seats','#46464b',.88);inside=mat('dark interior','#29292e',.8)
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
  if min(v.x for v in coords)>.78 and min(v.z for v in coords)>.18:
   discard.extend(component)
 removed+=len(discard);bmesh.ops.delete(bm,geom=discard,context='VERTS');bm.to_mesh(o.data);bm.free()
# Rebuild the automotive shell as an explicit editable subdivision cage.
cab_tools=runpy.run_path(str(ROOT/'scripts/fondfont-truck-cab-v12.py'))
red=mat('clean automotive vermilion','#df2536',.235,.12)
paint=red.node_tree.nodes.get('Principled BSDF');paint.inputs['Coat Weight'].default_value=.42;paint.inputs['Coat Roughness'].default_value=.16
cab,cage,shell=cab_tools['build_cab'](mesh,red,truck)
front_point=lambda z,h,offset=0:cab_tools['front_point'](shell,z,h,offset)
side_point=lambda x,h,sign,offset=0:cab_tools['side_point'](shell,x,h,sign,offset)
def subtract(cutter):
 bpy.context.view_layer.objects.active=cab;m=cab.modifiers.new('Actual shell aperture','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cutter,do_unlink=True)
side=rounded([(1.015,1.49),(1.035,2.12),(1.12,2.23),(1.90,2.23),(2.045,2.13),(2.175,1.53)],.055)
subtract(extrude('Side window aperture',side,-1.2,1.2,gasket,bevel=0))
front=rounded([(-.715,1.49),(.715,1.49),(.675,2.23),(-.675,2.23)],.065)
n=len(front);verts=[(x,h,z) for x in [1.94,2.60] for z,h in front];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
cut=mesh('Curved windscreen opening',verts,faces,gasket);bm=bmesh.new();bm.from_mesh(cut.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cut.data);bm.free();subtract(cut)
subtract(cyl('True front wheel opening',.495,2.4,(1.62,.435,0),gasket))
bpy.context.view_layer.objects.active=cab;m=cab.modifiers.new('Fine pressed aperture edges','BEVEL');m.width=.005;m.segments=3;m.limit_method='ANGLE'
front_x=lambda h:front_point(0,h)[0]
for sign in [-1,1]:
 z=sign*.804
 cab_tools['glazing'](mesh,'Fitted curved side glazing',side,lambda x,h:side_point(x,h,sign,.002),glass,truck)
 tube('Slim side window gasket',[side_point(x,h,sign,.005) for x,h in side],.013,gasket,closed=True)
 door=rounded([(1.005,1.035),(.965,1.48),(.985,2.14),(1.10,2.29),(1.93,2.29),(2.095,2.16),(2.245,1.48),(2.23,1.06),(2.09,1.015)],.035)
 tube('Continuous fitted closed door reveal',[side_point(x,h,sign,.0008) for x,h in door],.0025,graphite,closed=True)
 box('Recessed door handle',(.075,.15,.022),(1.06,1.35,z+sign*.008),gasket,bevel=.014)
 box('Small satin handle',(.018,.095,.027),(1.06,1.35,z+sign*.022),silver,bevel=.007)
 box('Satin boarding step',(.74,.065,.18),(1.27,.70,sign*.79),silver,bevel=.025)
 for j in range(5):box('Step grip',(.58,.008,.008),(1.27,.736,sign*(.74+j*.02)),rubber,bevel=.003)
 tube('Fine mirror support',[(2.06,1.88,z),(2.17,1.89,sign*1.02),(2.17,1.64,sign*1.02)],.012,gasket)
 box('Rounded mirror housing',(.11,.28,.12),(2.17,1.79,sign*1.055),gasket,bevel=.038)
 box('Mirror inset',(.014,.23,.085),(2.225,1.79,sign*1.055),chrome,bevel=.022)
 # Thin pressed fender lip belongs to the new wheel opening.
 verts=[(1.62+r*math.cos(j*math.pi/64),.435+r*math.sin(j*math.pi/64),sign*z) for z in [.815,.850] for r in [.495,.55] for j in range(65)];faces=[]
 for j in range(64):
  faces.extend([(j,j+1,65+j+1,65+j),(130+j,195+j,195+j+1,130+j+1),(j,130+j,130+j+1,j+1),(65+j,65+j+1,195+j+1,195+j)])
 faces.extend([(0,65,195,130),(64,194,259,129)])
 mesh('Integrated pressed wheel arch',verts,faces,red,bevel=.006)
cab_tools['glazing'](mesh,'Fitted bowed windshield',front,lambda z,h:front_point(z,h,.002),glass,truck)
tube('Front gasket recess',[front_point(z,h,.005) for z,h in front],.014,gasket,closed=True)
for sign in [-1,1]:
 tube('Windshield wiper arm',[front_point(sign*.39,1.53,.015),front_point(sign*.20,1.63,.015)],.008,gasket)
 tube('Fine wiper blade',[front_point(sign*.11,1.62,.018),front_point(sign*.43,1.65,.018)],.009,gasket)
 box('Cloth seat cushion',(.35,.095,.37),(1.32,1.36,sign*.36),seat,bevel=.045)
 box('Seat back',(.12,.48,.37),(1.13,1.62,sign*.36),seat,bevel=.055)
 box('Headrest',(.12,.17,.25),(1.13,1.96,sign*.36),seat,bevel=.045)
box('Dashboard',(.22,.14,1.37),(2.00,1.44,0),inside,bevel=.045)
ring('Steering wheel',.12,.013,(1.84,1.55,-.36),gasket,axis='x')
# Pressed fascia openings have real returns in the cab, with recessed inserts.
def front_cut(name,outline):
 n=len(outline);verts=[(x,h,z) for x in [1.95,2.7] for z,h in outline]
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 cutter=mesh(name,verts,faces,gasket)
 bm=bmesh.new();bm.from_mesh(cutter.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cutter.data);bm.free();subtract(cutter)
 return outline
grille=rounded([(-.415,1.04),(.415,1.04),(.465,1.305),(-.465,1.305)],.025)
front_cut('Actual formed tapered grille aperture',grille)
cab_tools['glazing'](mesh,'Recessed tapered grille backing',grille,lambda z,h:front_point(z,h,-.024),gasket,truck)
tube('Pressed red grille return',[front_point(z,h,-.004) for z,h in grille],.010,red,closed=True)
for h in [1.095,1.18,1.255]:
 width=.415+(h-1.04)*.18
 tube('Grille horizontal satin blade',[front_point(z,h,-.012) for z in [-width,0,width]],.007,silver)
for j in range(19):
 z=(j-9)*.042
 tube('Inset grille cooling vanes',[front_point(z,1.065,-.019),front_point(z,1.28,-.019)],.005,graphite)
for sign in [-1,1]:
 outline=rounded([(sign*.505,.98),(sign*.755,.98),(sign*.745,1.37),(sign*.515,1.335)],.016)
 front_cut('Recessed stacked lamp aperture',outline)
 tube('Integrated lamp gasket',[front_point(z,h,-.002) for z,h in outline],.008,gasket,closed=True)
# Substantial sculpted wraparound bumper with shallow central return.
profile=[(2.355,.70),(2.405,.735),(2.425,.91),(2.385,.975),(2.28,.975),(2.27,.70)]
bumper=extrude('Pressed wraparound red bumper',profile,-.85,.85,red,bevel=.025)
# Separate metal insert sits flush within the surrounding red manufactured part.
insert=rounded([(-.73,.735),(.73,.735),(.73,.935),(-.73,.935)],.045)
verts=[(2.423,h,z) for z,h in insert]
mesh('Fitted satin bumper center',verts,[tuple(range(len(verts)))],silver)
opening=rounded([(-.40,.76),(.40,.76),(.44,.87),(-.44,.87)],.018)
mesh('Inset lower bumper airflow',[(2.427,h,z) for z,h in opening],[tuple(range(len(opening)))],gasket)
for z in [-.64,.64]:
 opening=rounded([(z-.075,.765),(z+.075,.765),(z+.075,.875),(z-.075,.875)],.018)
 mesh('Bumper inset driving lamp',[(2.43,h,zz) for zz,h in opening],[tuple(range(len(opening)))],lamp)
# Roof pressed channels are narrow structural ribs, visible from the hero camera.
for z in [-.46,-.23,0,.23,.46]:
 tube('Shallow roof press rib',[(1.12,2.369,z),(1.45,2.371,z),(1.87,2.368,z)],.0035,red)
box('Cab floor and engine mount',(1.3,.10,1.40),(1.53,1.1,0),inside,bevel=.045)
# Smooth sidewalls and real recessed metal wheel dishes; retain every motion pivot.
wheel_template=None
for steer in [o for o in truck.children if o.name.startswith('Steer_')]:
 spin=steer.children[0]
 for o in list(spin.children_recursive):bpy.data.objects.remove(o,do_unlink=True)
 if wheel_template is not None:
  for original in wheel_template:
   duplicate=original.copy();duplicate.data=original.data.copy();scene_collection=bpy.context.scene.collection;scene_collection.objects.link(duplicate);duplicate.parent=spin
  continue
 runpy.run_path(str(ROOT/'scripts/fondfont-truck-tire.py'))['tire'](mesh,rubber,spin)
 for sign in [-1,1]:
  ring('Fine sidewall molding',.345,.004,(0,0,sign*.116),rubber,spin)
  # Revolved dish profile provides depth and a clean rolled metal lip.
  profile=[(.06,.127),(.10,.127),(.13,.114),(.19,.102),(.22,.117),(.24,.125),(.248,.122),(.248,.112),(.22,.103),(.18,.091),(.12,.101),(.06,.114)]
  verts=[(r*math.cos(j*math.tau/64),r*math.sin(j*math.tau/64),sign*d) for r,d in profile for j in range(64)];faces=[]
  for k in range(len(profile)):
   for j in range(64):a=k*64+j;b=k*64+(j+1)%64;c=((k+1)%len(profile))*64+(j+1)%64;d=((k+1)%len(profile))*64+j;faces.append((a,b,c,d))
  dish=mesh('Recessed satin wheel dish',verts,faces,silver,spin)
  for mod in list(dish.modifiers):dish.modifiers.remove(mod)
  for j in range(8):
   a=j*math.tau/8;cut=cyl('Actual wheel vent cutter',.028,.10,(math.cos(a)*.175,math.sin(a)*.175,sign*.115),gasket,spin,segments=24)
   bpy.context.view_layer.objects.active=dish;mod=dish.modifiers.new('Through ventilation hole','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
  ring('Rolled polished wheel rim',.240,.008,(0,0,sign*.123),chrome,spin)
  cyl('Graphite hub center',.068,.035,(0,0,sign*.133),gasket,spin)
  for j in range(6):
   a=j*math.tau/6
   cyl('Machined six lug nut',.014,.016,(math.cos(a)*.10,math.sin(a)*.10,sign*.137),chrome,spin,segments=6)
 wheel_template=list(spin.children)
# Graphite gate centers with preserved red stakes and exact moving gate owner.
for owner in [truck,bpy.data.objects['LoadingSideGate']]:
 for o in list(owner.children):
  if o.type!='MESH' or o.name.startswith('Precision'):continue
  o.data.materials.append(graphite);material_index=len(o.data.materials)-1
  o.data.materials.append(red);frame_material_index=len(o.data.materials)-1
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
   if hi[0]-lo[0]>3 and 1.37<lo[2] and hi[2]<1.47:
    for f in {f for v in component for f in v.link_faces}:f.material_index=frame_material_index
    if hi[1]-lo[1]>.2:
     center=(lo[1]+hi[1])/2
     inverse=transform.inverted()
     for v in component:
      p=transform@v.co;p.y=center+(p.y-center)*.5;v.co=inverse@p
  bm.to_mesh(o.data);bm.free()
# Invariant: native rig attachment nodes retain their exact local transforms.
for name,record in contract.items():
 o=bpy.data.objects[name];assert (o.parent.name if o.parent else None,list(o.location),list(o.rotation_euler),list(o.scale))==record,name
truck['precision_reference']='truck-precision-reference-v7.png';truck['wheel_radius']=.435
# This paint anchor is static, not an animation pivot. Register it to the new roof.
bpy.data.objects['CabRoofName'].location.z=2.372
# Join only static surfaces sharing a motion owner, after applying their edge modifiers.
for owner in [truck]+[o for o in truck.children_recursive if o.name.startswith('Wheel_')]:
 objects=[o for o in owner.children if o.type=='MESH' and o!=cage]
 for o in objects:
  bpy.context.view_layer.objects.active=o
  for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 if objects:
  bpy.ops.object.select_all(action='DESELECT')
  for o in objects:o.select_set(True)
  bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();objects[0].name='Precision '+owner.name+' surfaces'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'factory-truck-v12-base.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o!=cage:o.select_set(True)
bpy.ops.export_scene.gltf(use_selection=True,filepath=str(OUT/'factory-truck-v12-base-raw.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_animations=False,export_extras=True,export_image_format='WEBP',export_image_quality=92)
print(json.dumps({'removed_cab_vertices':removed,'preserved_motion_nodes':len(contract),'wheel_radius':.435}))
