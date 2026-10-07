"""Blender-authored, editable miniature for FondFont. Run with Blender --background --python.
Coordinates below are glTF/Three axes: X travel, Y up, Z toward viewer.
Raster surfaces: complete original imagegen maps; original FondFont identity; native lettering.
"""
import bpy, bmesh, math, json, sys, re, importlib.util
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scripts/assets/fondfont/blender-v2'
LEGACY=ROOT/'scripts/assets/fondfont/blender-v1'
PUB=ROOT/'public/v/fondfont/blender-v2'
OUT.mkdir(parents=True,exist_ok=True); PUB.mkdir(parents=True,exist_ok=True)
FRAGMENT='--fragment' in sys.argv
STEM='loading-fragment' if FRAGMENT else 'factory'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)

def P(x,y,z):return (x,-z,y)
def parent(o,p):
    if p:o.parent=p
    return o
def group(name,p=None,at=(0,0,0)):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=P(*at);parent(o,p);return o

def material(name,color,rough=.5,metal=0,texture=None):
    m=bpy.data.materials.new(name);m.use_nodes=True
    s=m.node_tree.nodes.get('Principled BSDF')
    rgb=tuple(int(color[i:i+2],16)/255 for i in (1,3,5));rgb=tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in rgb)
    s.inputs['Base Color'].default_value=(*rgb,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal
    m.diffuse_color=(*rgb,1)
    if texture:
        t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(OUT/texture if (OUT/texture).exists() else LEGACY/texture),check_existing=True);t.image.pack()
        m.node_tree.links.new(t.outputs['Color'],s.inputs['Base Color'])
        normal_path=LEGACY/('brick-normal.png' if texture=='brick-refined.png' else Path(texture).stem+'-normal.png')
        if normal_path.exists():
            nt=m.node_tree.nodes.new('ShaderNodeTexImage');nt.image=bpy.data.images.load(str(normal_path),check_existing=True);nt.image.colorspace_settings.name='Non-Color';nt.image.pack()
            nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.18 if Path(texture).stem=='stone' else .3
            m.node_tree.links.new(nt.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],s.inputs['Normal'])
    return m
M={}
for name,c,r,met in [('porcelain','#e5e3d8',.65,0),('ivory','#eeeadd',.48,0),('trim','#d3d3c1',.57,0),('mortar','#9c8a73',.95,0),('orange','#ff293c',.26,.22),('orangeLight','#ff3549',.24,.18),('burnt','#981e35',.4,.18),('sage','#737e6b',.45,.45),('iron','#302937',.37,.65),('steel','#bcc0c4',.28,.82),('brass','#b29a57',.3,.78),('rubber','#282d29',.87,0),('glass','#293140',.2,.4),('glassLight','#727985',.24,.3),('black','#201d29',.5,0),('wood','#a07b4c',.72,0),('darkWood','#654f35',.74,0),('lamp','#f3dfb4',.23,.12),('red','#a84a35',.34,.1),('asphalt','#a9ada0',.95,0),('paint','#e6dfc4',.7,0)]:M[name]=material(name,c,r,met)
M['forkSteel']=material('Forged graphite forks','#48464b',.68,.24)
M['mastSteel']=material('Matte graphite mast','#353039',.64,.22)
M['brick']=material('imagegen warm brick','#ffffff',.88,0,'brick-refined.png')
M['woodGrain']=material('imagegen oak','#ffffff',.8,0,'oak.png')
M['sage']=material('imagegen plum enamel','#ffffff',.30,.08,'plum-enamel.png')
M['orange']=material('imagegen FondFont red enamel','#ffffff',.24,.06,'red-enamel.png')
for name in ['sage','orange']:
    bsdf=M[name].node_tree.nodes.get('Principled BSDF');bsdf.inputs['Coat Weight'].default_value=.35;bsdf.inputs['Coat Roughness'].default_value=.22
M['orangeLight']=M['orange']
M['porcelain']=material('imagegen limestone plinth','#ffffff',.72,0,'stone.png')
M['ivory']=material('imagegen limestone trim','#ffffff',.6,0,'stone.png')
M['asphalt']=material('imagegen quiet asphalt','#ffffff',.88,0,'quiet-road.png')
# All stylization survives glTF: bevel geometry, supported Principled materials, UV images.

def finish(o,name,mat,p=None,bevel=0,smooth=False):
    o.name=name
    if mat:o.data.materials.append(M[mat] if isinstance(mat,str) else mat)
    if bevel:
        mod=o.modifiers.new('Manufactured edge highlights','BEVEL');mod.width=bevel;mod.segments=3
        mod.affect='EDGES'
        mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=40
    if smooth:
        for f in o.data.polygons:f.use_smooth=True
    parent(o,p)
    if mat in ['sage','porcelain','ivory','asphalt']:uv_box(o,.35)
    return o

def box(name,w,h,d,at,mat,p=None,b=.025):
    x=y=z=0
    verts=[(x+sx*w/2,y+sy*h/2,z+sz*d/2) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    o=mesh(name,verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,p,b);o.location=P(*at);return o

def mesh(name,verts,faces,mat,p=None,bevel=0):
    me=bpy.data.meshes.new(name);me.from_pydata([P(*v) for v in verts],[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);finish(o,name,mat,p,bevel)
    return o

def cylinder(name,r,length,at,mat,p=None,axis='y',vertices=32,r2=None):
    data=bpy.data.meshes.new(name);bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=vertices,radius1=r,radius2=r if r2 is None else r2,depth=length);bm.to_mesh(data);bm.free()
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=P(*at)
    if axis=='x':o.rotation_euler[1]=math.pi/2
    if axis=='z':o.rotation_euler[0]=math.pi/2
    return finish(o,name,mat,p,.008,True)

def torus(name,r,tube,at,mat,p=None,axis='z'):
    verts=[((r+tube*math.cos(j*math.tau/8))*math.cos(i*math.tau/48),(r+tube*math.cos(j*math.tau/8))*math.sin(i*math.tau/48),tube*math.sin(j*math.tau/8)) for i in range(48) for j in range(8)]
    faces=[(i*8+j,((i+1)%48)*8+j,((i+1)%48)*8+(j+1)%8,i*8+(j+1)%8) for i in range(48) for j in range(8)]
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=P(*at)
    if axis=='z':o.rotation_euler[0]=math.pi/2
    if axis=='x':o.rotation_euler[1]=math.pi/2
    return finish(o,name,mat,p,0,True)

def rod(name,a,b,r,mat,p=None):
    a=Vector(P(*a));b=Vector(P(*b));center=(a+b)/2
    o=cylinder(name,r,(b-a).length,(0,0,0),mat,p,vertices=12);o.location=center;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.modifiers.clear();return o

def polygon_extrusion(name,profile,z0,z1,mat,p=None,bevel=.02):
    n=len(profile);verts=[(x,y,z) for z in (z0,z1) for x,y in profile]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,verts,faces,mat,p,bevel)

def plane(name,points,mat,p=None):return mesh(name,points,[(0,1,2,3)],mat,p)

def arch_profile(width,height,bottom,z):
    radius=width/2;spring=bottom+height-radius
    return [(z+radius,bottom),(z+radius,spring)]+[(z+radius*math.cos(i*math.pi/20),spring+radius*math.sin(i*math.pi/20)) for i in range(1,21)]+[(z-radius,bottom)]

def side_profile(name,profile,x0,x1,mat,building):
    n=len(profile);verts=[(x,y,z) for x in [x0,x1] for z,y in profile]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,verts,faces,mat,building,0)

def opening(wall,cutter):
    bpy.context.view_layer.objects.active=wall
    for mod in list(wall.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=wall.modifiers.new('Actual recessed opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)

def arch_ring(name,outer,inner,x0,x1,building):
    n=len(outer);verts=[(x,y,z) for x in [x0,x1] for profile in [outer,inner] for z,y in profile];faces=[]
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    return mesh(name,verts,faces,'ivory',building,.012)

def rounded_shell(name,low,high,building,portal=False):
    rings=[]
    for w,d,r in [(6.18,2.90,.37),(5.62,2.34,.09)]:
        ring=[]
        for k,(cx,cz,a0) in enumerate([(w/2-r,d/2-r,0),(-w/2+r,d/2-r,math.pi/2),(-w/2+r,-d/2+r,math.pi),(w/2-r,-d/2+r,math.pi*1.5)]):
            for j in range(9):
                a=a0+j*math.pi/16;ring.append((cx+r*math.cos(a),cz+r*math.sin(a)+.35))
            if k==0:ring.extend([(1.95,d/2+.35),(-1.95,d/2+.35)])
        rings.append(ring)
    n=len(rings[0]);verts=[(x,y,z) for y in [low,high] for ring in rings for x,z in ring];faces=[]
    for i in range(n):
        j=(i+1)%n;a,b=rings[0][i],rings[0][j]
        if portal and abs(a[1]-1.8)<.001 and abs(b[1]-1.8)<.001 and max(abs(a[0]),abs(b[0]))<=1.951:continue
        faces.extend([(i,j,2*n+j,2*n+i),(n+i,3*n+i,3*n+j,n+j),(i,n+i,n+j,j),(2*n+i,2*n+j,3*n+j,3*n+i)])
    if portal:
        for i,(x,z) in enumerate(rings[0]):
            if abs(abs(x)-1.95)<.001 and abs(z-1.8)<.001:faces.append((i,2*n+i,3*n+i,n+i))
    return mesh(name,verts,faces,'ivory',building,.012)

def uv_box(o,scale=.8):
    # Box projection in physical world units; imagegen supplies surface pixels.
    me=o.data
    if not me.uv_layers:me.uv_layers.new()
    uv=me.uv_layers.active.data
    for face in me.polygons:
        n=face.normal;axis=max(range(3),key=lambda i:abs(n[i]));coords=[i for i in range(3) if i!=axis]
        for li in face.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            uv[li].uv=(v[coords[0]]*scale,v[coords[1]]*scale)

truck=group('Truck',at=(-4.85,0,4))
# Ladder frame and separate leaf springs beneath the visible oak bed.
for z in [-.57,.57]:box('Ladder chassis',4.55,.18,.13,(-.15,.69,z),'iron',truck,.025)
for x in [-2.12,-1.3,-.35,.7,1.65]:box('Chassis crossmember',.12,.13,1.43,(x,.7,0),'iron',truck,.018)
for x in [-1.82,-.75,1.62]:
    cylinder('Axle',.075,1.78,(x,.44,0),'iron',truck,'z',16)
    for z in [-.57,.57]:
        for j in range(3):box('Leaf spring',.72-j*.12,.025,.1,(x,.57+j*.027,z),'steel',truck,.01)
# Flatbed deliberately thin, sided at low enough level that cargo remains clearly visible.
box('Bed perimeter',3.22,.13,1.78,(-.81,.91,0),'iron',truck,.025)
for i in range(9):
    o=box('Oak deck plank',3.1,.095,.18,(-.81,1.022,(i-4)*.19),'woodGrain',truck,.012);uv_box(o,.7)
for z in [-.925,.925]:
    gate=group('LoadingSideGate',truck,(0,1.02,z-.085)) if z<0 else truck
    by=1.02 if z<0 else 0
    bz=z-.085 if z<0 else 0
    box('Side panel',3.22,.38,.07,(-.81,1.23-by,z-bz),'orange',gate,.03)
    box('Side panel lower seam',3.16,.025,.08,(-.81,1.075-by,z-bz),'burnt',gate,.009)
    box('Cream pinstripe',3.15,.012,.075,(-.81,1.389-by,z-bz),'paint',gate,.004)
    box('Flatbed upper name rail',3.18,.045,.08 if z<0 else .30,(-.81,1.435-by,z-bz),'iron',gate,.025)
    for x in [-2.36,-1.3,-.25,.73]:
        box('Stake',.055,.42,.09,(x,1.23-by,z-bz),'orangeLight',gate,.012)
        for y in [1.09,1.37]:cylinder('Stake rivet',.015,.018,(x,y-by,z-bz+(.05 if z>0 else -.05)),'brass',gate,'z',12)
box('Tailgate',.075,.39,1.83,(-2.43,1.23,0),'orange',truck,.035)
for z in [-.63,.63]:
    box('Rear bumper',.11,.14,.54,(-2.57,.65,z),'steel',truck,.02)
    box('Tail lamp',.035,.1,.18,(-2.49,.83,z),'red',truck,.01)
    box('Mud flap',.045,.33,.3,(-2.3,.37,z),'rubber',truck,.01)
# Rounded cabover profile: raked front glazing, nose, roof and footwell are one silhouette.
profile=[(.83,.79),(.83,1.78),(.96,2.16),(1.17,2.24),(1.94,2.24),(2.17,2.06),(2.3,1.47),(2.3,.89),(2.17,.79)]
polygon_extrusion('Cab shell',profile,-.79,.79,'orange',truck,.075)
box('Roof cap',1.22,.105,1.69,(1.58,2.25,0),'orangeLight',truck,.065)
# Side windows lie in inset, framed openings; no see-through transmission cost.
sideWindow=[(1.0,1.57),(1.04,2.02),(1.2,2.12),(1.91,2.12),(2.09,1.99),(2.17,1.57)]
for z in [-.803,.803]:
    polygon_extrusion('Window gasket',sideWindow,z-.014,z+.014,'rubber',truck,.025)
    inset=[(1.05,1.62),(1.09,2.0),(1.22,2.065),(1.89,2.065),(2.04,1.96),(2.11,1.62)]
    polygon_extrusion('Side glazing',inset,z-.018,z+.018,'glass',truck,.02)
    box('Window divider',.038,.43,.043,(1.37,1.84,z+(.025 if z>0 else -.025)),'iron',truck,.008)
    box('Window highlight',.16,.025,.045,(1.19,2.015,z+(.03 if z>0 else -.03)),'glassLight',truck,.007)
    # Door pressed outline, handle, stepped sill.
    rod('Door rear seam',(.94,.87,z),(.94,1.52,z),.009,'burnt',truck)
    rod('Door bottom seam',(.96,.88,z),(1.76,.88,z),.009,'burnt',truck)
    box('Door handle',.15,.035,.04,(1.08,1.43,z+(.04 if z>0 else -.04)),'steel',truck,.012)
    box('Cab step',.95,.08,.22,(1.3,.72,z),'steel',truck,.024)
    box('Non slip step',.71,.014,.14,(1.31,.768,z),'rubber',truck,.005)
    rod('Mirror arm',(2.04,1.73,z),(2.2,1.78,z*1.3),.017,'iron',truck)
    box('Mirror body',.09,.24,.15,(2.21,1.8,z*1.34),'iron',truck,.03)
# Broad split windscreen plane follows the actual slope of the custom cab shell.
for a,b in [(-.68,-.035),(.035,.68)]:
    plane('Front windscreen gasket',[(2.303,1.53,a-.025),(2.303,1.53,b+.025),(2.195,2.015,b+.025),(2.195,2.015,a-.025)],'rubber',truck)
    plane('Front windscreen',[(2.303,1.58,a),(2.303,1.58,b),(2.207,1.98,b),(2.207,1.98,a)],'glass',truck)
    rod('Wiper',(2.313,1.59,(a+b)/2-.12),(2.28,1.73,(a+b)/2+.12),.009,'iron',truck)
box('Nose inset grille',.035,.28,.74,(2.337,1.17,0),'black',truck,.035)
for j in range(5):box('Grille slat',.05,.014,.69,(2.36,1.07+j*.045,0),'steel',truck,.005)
box('Nose badge',.03,.07,.11,(2.365,1.36,0),'brass',truck,.018)
box('Chrome bumper',.15,.15,1.81,(2.35,.87,0),'steel',truck,.055)
for z in [-.59,.59]:
    cylinder('Headlight bezel',.14,.055,(2.31,1.2,z),'steel',truck,'x',32)
    cylinder('Headlight glass',.11,.061,(2.33,1.2,z),'lamp',truck,'x',32)
    cylinder('Indicator',.055,.045,(2.31,1.44,z),'orangeLight',truck,'x',20)
for z in [-.49,.49]:cylinder('Roof marker',.04,.055,(1.96,2.324,z),'lamp',truck,'y',16)
# Curved wheel arches: real silhouettes, not black discs pasted over a cuboid.
for x in [-1.82,-.75,1.62]:
    for side in [-1,1]:
        verts=[]
        for z in [side*.72,side*1.03]:
            for r in [.485,.545]:
                for i in range(25):
                    a=math.pi*i/24;verts.append((x+math.cos(a)*r,.44+math.sin(a)*r,z))
        faces=[]
        for k in range(24):
            faces += [(k,k+1,25+k+1,25+k),(50+k,75+k,75+k+1,50+k+1),(k,50+k,50+k+1,k+1),(25+k,25+k+1,75+k+1,75+k)]
        mesh('Pressed wheel arch',verts,faces,'orange' if x>0 else 'iron',truck,.008)
        steer=group(f'Steer_{x}_{side}',truck,(x,.435,side*.88));spin=group(f'Wheel_{x}_{side}',steer)
        torus('Tire',.335,.098,(0,0,0),'rubber',spin)
        cylinder('Tire body',.4,.235,(0,0,0),'rubber',spin,'z',40)
        for zz in [-.124,.124]:
            torus('Raised sidewall',.32,.018,(0,0,zz),'rubber',spin)
            cylinder('Steel wheel dish',.235,.023,(0,0,zz),'ivory',spin,'z',32)
            torus('Wheel lip',.225,.014,(0,0,zz*1.12),'steel',spin)
            cylinder('Hub cap',.088,.07,(0,0,zz),'brass',spin,'z',24)
            for j in range(6):
                a=j*math.tau/6;xx=math.cos(a)*.146;yy=math.sin(a)*.146
                cylinder('Hub vent',.034,.029,(xx,yy,zz*1.16),'black',spin,'z',12)
                cylinder('Lug nut',.017,.04,(math.cos(a)*.102,math.sin(a)*.102,zz*1.3),'steel',spin,'z',6)
        for j in range(32):
            a=j*math.tau/32
            o=box('Tread',.065,.025,.205,(math.cos(a)*.422,math.sin(a)*.422,0),'rubber',spin,.004)
            o.rotation_euler[1]=a-math.pi/2
# Cargo anchor and paint anchors export as explicit empties for browser typesetting.
group('TruckCargo',truck,(-.75,1.07,0))
group('FleetFront',truck,(-.8,1.24,.973));group('FleetBack',truck,(-.8,1.24,-.973))
group('CabRoofName',truck,(1.58,2.309,0))
group('FlatbedName',truck,(-.81,1.076,0))
group('RailNameFront',truck,(-.81,1.461,.925))
for side in [-1,1]:group('CabBadge'+str(side),truck,(1.6,1.31,side*.813))

# Only a final-quality loading-bay fragment is exported first. Full site follows its browser gate.
world=group('Architecture')
box('Fragment floor',13,.2,10,(-3,-.14,.2),'porcelain',world,.15)
box('Road fragment',13,.025,2.7,(-3,.005,4),'asphalt',world,.08)
for x in range(-9,4):box('Lane dash',.45,.008,.05,(x,.024,4),'paint',world,.004)
foundry=group('Foundry',world,(-5.6,0,-1.25))
group('FoundrySign',foundry,(0,3.1,1.812))
# Pallet is a rigid physical carrier; the exact type contours are original font geometry.
cargo=group('Cargo',at=(-5.6,0,1.4))
for x in [-.8,.8]:box('Pallet foot',.22,.13,1.12,(x,.065,0),'darkWood',cargo,.015)
for j in range(5):
    o=box('Oak pallet board',2.05,.085,.19,(0,.17,(j-2)*.225),'woodGrain',cargo,.014);uv_box(o,1)
def glyph_curve(g,name,at,height,p,top=False,mat='brass'):
    tokens=re.findall(r'[MLHVQCZ]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',g['path'])
    loops=[];points=[];i=0;cur=(0,0);cmd='M'
    while i<len(tokens):
        if tokens[i].isalpha():cmd=tokens[i];i+=1
        elif cmd=='M':cmd='L'
        if cmd=='Z':
            loops.append(points);points=[];continue
        counts={'M':2,'L':2,'H':1,'V':1,'Q':4,'C':6};n=counts[cmd];v=list(map(float,tokens[i:i+n]));i+=n
        if cmd=='M':cur=tuple(v);points=[{'p':cur,'left':cur,'right':cur}]
        else:
            end=tuple(v[-2:]) if cmd not in ['H','V'] else (v[0],cur[1]) if cmd=='H' else (cur[0],v[0])
            if cmd=='Q':
                ctrl=tuple(v[:2]);points[-1]['right']=tuple(cur[k]+2/3*(ctrl[k]-cur[k]) for k in range(2));left=tuple(end[k]+2/3*(ctrl[k]-end[k]) for k in range(2))
            elif cmd=='C':points[-1]['right']=tuple(v[:2]);left=tuple(v[2:4])
            else:left=end
            if end==points[0]['p']:points[0]['left']=left
            else:points.append({'p':end,'left':left,'right':end})
            cur=end
    if points:loops.append(points)
    coords=[v['p'] for loop in loops for v in loop];lo=[min(v[k] for v in coords) for k in range(2)];hi=[max(v[k] for v in coords) for k in range(2)]
    scale=min(height/(hi[1]-lo[1]),.56/(hi[0]-lo[0]));center=[(lo[k]+hi[k])/2 for k in range(2)]
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='2D';data.resolution_u=6;data.fill_mode='BOTH';data.extrude=min(.025,height*.05);data.bevel_depth=min(.002,height*.01);data.bevel_resolution=1
    for loop in loops:
        if len(loop)<2:continue
        spl=data.splines.new('BEZIER');spl.bezier_points.add(len(loop)-1);spl.use_cyclic_u=True
        for point,info in zip(spl.bezier_points,loop):
            def co(v):return ((v[0]-center[0])*scale,-(v[1]-center[1])*scale,0)
            point.co=co(info['p']);point.handle_left_type='FREE';point.handle_right_type='FREE';point.handle_left=co(info['left']);point.handle_right=co(info['right'])
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=P(*at);o.rotation_euler[0]=0 if top else math.pi/2;parent(o,p);data.materials.append(M[mat])
    bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
# Three stacked open type trays follow imagegen's exposed metal freight reference.
glyphs=json.loads((ROOT/'src/lib/fondfont/glyphs.json').read_text())
for row in range(3):
    tray=group(f'TypeTray{row}',cargo,(0,.225+row*.27,0))
    box('Oak type tray base',1.94,.035,1.02,(0,.018,0),'woodGrain',tray,.008)
    for xx in [-.955,.955]:
        box('Type tray dovetail end',.035,.235,1.02,(xx,.1175,0),'woodGrain',tray,.009)
        for zz in [-.49,.49]:box('Bronze corner fitting',.044,.055,.045,(xx,.19,zz),'brass',tray,.007)
    for zz in [-.50,.50]:box('Low type tray lip',1.88,.045,.025,(0,.055,zz),'woodGrain',tray,.006)
    for col in range(6):
        xx=(col-2.5)*.30
        for depth in range(3):
            zz=.33-depth*.33
            block=group(f'TypeSort{row}_{col}_{depth}',tray,(xx,0,zz))
            box('Lead type sort',.278,.215,.302,(0,.145,0),'steel',block,.009)
            glyph=glyphs[(col+row*2)%len(glyphs)]
            glyph_curve(glyph,'Raised printing face',(0,.151,.156),.174,block,False,'black')
            if row==2:glyph_curve(glyph,'Top type contour',(0,.259,0),.18,block,True,'black')
for x in [-.92,.92]:
    for z in [-.525,.525]:box('Cargo securing strap',.035,.84,.018,(x,.61,z),'sage',cargo,.004)
    box('Cargo top strap',.035,.018,1.06,(x,1.035,0),'sage',cargo,.004)

if not FRAGMENT:
    # A continuous, metrically registered stadium road: rear axle follows the center line.
    for o in list(bpy.context.scene.objects):
        if o.name.startswith(('Fragment floor','Road fragment','Lane dash')):bpy.data.objects.remove(o,do_unlink=True)
    box('Limestone diorama',30.8,.22,15.1,(0,-.13,-.8),'porcelain',world,.18)
    R=4.8;TX=7.4;ROAD=4;L=4*TX+math.tau*R
    def track(d,offset=0):
        d=d%L
        if d<=2*TX:return(-TX+d,ROAD+offset,0)
        d-=2*TX
        if d<=math.pi*R:
            a=d/R;return(TX+(R+offset)*math.sin(a),ROAD-R+(R+offset)*math.cos(a),a)
        d-=math.pi*R
        if d<=2*TX:return(TX-d,ROAD-2*R-offset,math.pi)
        d-=2*TX;a=math.pi+d/R
        return(-TX+(R+offset)*math.sin(a),ROAD-R+(R+offset)*math.cos(a),a)
    def ribbon(name,inner,outer,y,mat):
        verts=[];n=320
        for i in range(n):
            for offset in [inner,outer]:
                x,z,a=track(L*i/n,offset);verts.append((x,y,z))
        faces=[(2*i,2*i+1,(2*i+3)%(n*2),(2*i+2)%(n*2)) for i in range(n)]
        o=mesh(name,verts,faces,mat,world);uv_box(o,.45)
    ribbon('Complete loop road',-1.8,1.8,.016,'asphalt')
    ribbon('Outer stone gutter',1.82,2.06,.028,'ivory')
    ribbon('Inner stone gutter',-2.06,-1.82,.028,'ivory')
    for offset in [-1.88,1.88]:
        for i in range(94):
            x,z,a=track(L*i/94,offset);o=box('Curb joint',.018,.012,.22,(x,.042,z),'mortar',world,.002);o.rotation_euler[2]=a
    for d in range(0,int(L),2):
        x,z,a=track(d);o=box('Road dash',.6,.008,.055,(x,.026,z),'paint',world,.003);o.rotation_euler[2]=a
    for d in [4,17,28,39,49,57]:
        x,z,a=track(d,1.65)
        drain=group('Road drain',world,(x,.03,z));drain.rotation_euler[2]=a
        box('Drain recess',.7,.018,.24,(0,0,0),'black',drain,.015)
        for j in range(9):box('Drain grating',.025,.018,.22,((j-4)*.073,.015,0),'steel',drain,.004)
    # Imagegen draws the complete library; its unchanged image shares one projection
    # across the native facade, phone roof, recessed interior and loading floor.
    warehouse=group('Warehouse',world,(5.6,0,-1.25))
    group('WarehouseSign',warehouse,(0,3.12,1.812))
    def shutter(name,building,width,height):
        spec=next(s for s in json.loads((OUT/'industrial-projection.json').read_text()) if s['root']==building.name)
        width=spec['door_width'];height=spec['door_height']
        g=group(name,building,(0,height/2,spec['door_z']+1.27));g['height']=height
        box('Rolling steel shutter',width,height,.07,(0,0,0),'sage',g,.01)
        for i in range(int(height/.14)):box('Shutter bead',width-.05,.018,.025,(0,-height/2+.07+i*.14,.047),'steel',g,.004)
        box('Door bottom seal',width,.045,.08,(0,-height/2+.022,0),'rubber',g,.009)
        return g
    shutter('SourceDoor',foundry,3.0,2.65);shutter('ReceiverDoor',warehouse,3.0,2.65)
    stacker_spec=importlib.util.spec_from_file_location('fondfont_stacker',ROOT/'scripts/fondfont-stacker-model.py')
    stacker_module=importlib.util.module_from_spec(stacker_spec);stacker_spec.loader.exec_module(stacker_module)
    stacker_module.build(globals())
# Localized sign placeholder follows the export transform.
# Native model scene axes are converted by glTF exporter; Three owns all moving assemblies.

def apply_and_merge():
    # Merge static surfaces per parent/material. Retain animation roots and attachment nodes.
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    depsgraph=bpy.context.evaluated_depsgraph_get()
    for o in objects:
        if not o.modifiers:continue
        evaluated=o.evaluated_get(depsgraph)
        baked=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=depsgraph)
        o.modifiers.clear();o.data=baked
    bins={}
    for o in objects:
        key=(o.parent.name if o.parent else '',o.data.materials[0].name if o.data.materials else '')
        bins.setdefault(key,[]).append(o)
    for (par,mat),items in bins.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in items:o.select_set(True)
        bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();items[0].name=f'{par}_{mat}'
spec=importlib.util.spec_from_file_location('fondfont_details',ROOT/'scripts/fondfont-model-details.py')
details=importlib.util.module_from_spec(spec);spec.loader.exec_module(details);details.build_details(ROOT)
print('Geometry ready; baking and merging',flush=True)
apply_and_merge()
# Native editable project includes lighting/camera for direct art inspection.
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=32
scene.world.color=(.72,.72,.72)
def area(name,location,power,size,color):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=P(*location);o.rotation_euler=(Vector(P(-3,1,0))-o.location).to_track_quat('-Z','Y').to_euler()
area('Large warm softbox',(-5,12,9),1600,9,(1,.91,.78));area('Cool broad fill',(5,8,-6),1100,8,(.83,.9,1))
data=bpy.data.cameras.new('Hero camera');cam=bpy.data.objects.new('Hero camera',data);bpy.context.collection.objects.link(cam);cam.location=P(8,10,19) if FRAGMENT else P(0,19.25,28.7);cam.rotation_euler=(Vector(P(-3,1.2,.5) if FRAGMENT else P(0,.25,-.8))-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=17 if FRAGMENT else 35.8;scene.camera=cam
scene.render.resolution_x=1600;scene.render.resolution_y=1000 if FRAGMENT else 900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(STEM+'.blend')))
bpy.ops.export_scene.gltf(filepath=str(OUT/(STEM+'-raw.glb')),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_animations=False,export_extras=True,export_image_format='WEBP',export_image_quality=92)
if '--no-render' not in sys.argv:
    scene.render.filepath=str(OUT/(STEM+'.png'));bpy.ops.render.render(write_still=True)
print('FONDFONT_FRAGMENT_DONE',str(PUB/(STEM+'.glb')))
