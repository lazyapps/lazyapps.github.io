"""Give imagegen architecture physical loading bays and closed shadow volumes.
Original image files and the integrated forklift/pet rigs are preserved.
"""
from pathlib import Path
import bpy, bmesh, math, json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'scripts/assets/fondfont/blender-v2'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'factory-forklift-v4.blend'))
def P(v):return(v[0],-v[2],v[1])
def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=.94
    return m
floor_mat=material('Loading bay stone',(.16,.135,.105));wall_mat=material('Loading bay shaded walls',(.11,.085,.064))
volume_mat=material('Architecture physical volume',(.3,.28,.25))
joint_mat=material('Loading bay floor joints',(.075,.062,.048))
def mesh(name,verts,faces,parent,mat,role=None,uv=None):
    me=bpy.data.meshes.new(name);me.from_pydata([P(v) for v in verts],[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.parent=parent;me.materials.append(mat)
    if role:o['architecture_role']=role
    if uv:
        layer=me.uv_layers.new()
        for loop in me.loops:layer.data[loop.index].uv=uv[loop.vertex_index]
    return o
# Coordinate arguments below are in world-aligned Y-up building space.
def prism(name,profile,z0,z1,parent,role='caster'):
    n=len(profile);verts=[(x,y,z+1.25) for z in [z0,z1] for x,y in profile]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,verts,faces,parent,volume_mat,role)
s=19/math.hypot(19,29.5);c=29.5/math.hypot(19,29.5)
for spec in json.loads((OUT/'industrial-projection.json').read_text()):
    parent=bpy.data.objects[spec['root']];art=next(o for o in parent.children_recursive if o.type=='MESH' and o.get('projection_source')==spec['file'])
    art['architecture_role']='artwork'
    W,H=spec['size'];xmin,ymin,xmax,ymax=spec['bounds'];scale=6.6/(xmax-xmin);cx=(xmin+xmax)/2
    left,head,right,floor=spec['portal'];u0,u1=left/W,right/W;v0,v1=1-floor/H,1-head/H
    bm=bmesh.new();bm.from_mesh(art.data);uvlayer=bm.loops.layers.uv.active
    removed=[]
    for face in bm.faces:
        u=sum(loop[uvlayer].uv.x for loop in face.loops)/len(face.loops);v=sum(loop[uvlayer].uv.y for loop in face.loops)/len(face.loops)
        if u0<u<u1 and v0<v<v1:removed.append(face)
    bmesh.ops.delete(bm,geom=removed,context='FACES');bm.to_mesh(art.data);bm.free()
    x0,x1=(left-cx)*scale,(right-cx)*scale
    zfront=spec['door_z'];zback=-4.4;h=spec['door_height'];roofh=(spec['ground']-spec['roof'])*scale/c
    # Continuous physical floor and wall bottoms all meet Y=0.
    mesh(spec['root']+' bay floor',[(x0,0,zfront+1.25),(x1,0,zfront+1.25),(x1,0,zback+1.25),(x0,0,zback+1.25)],[(0,1,2,3)],parent,art.data.materials[0],'interior-art',[(u0,1-floor/H),(u1,1-floor/H),(u1,1-spec['back_floor']/H),(u0,1-spec['back_floor']/H)])
    for index in range(8):
        z=zfront-.12-index*.55
        mesh(spec['root']+' floor joint '+str(index),[(x0,.002,z+1.25),(x1,.002,z+1.25),(x1,.002,z+1.262),(x0,.002,z+1.262)],[(0,1,2,3)],parent,joint_mat,'interior')
    for index in range(1,5):
        x=x0+(x1-x0)*index/5
        mesh(spec['root']+' floor longitudinal joint '+str(index),[(x,.002,zfront+1.25),(x+.008,.002,zfront+1.25),(x+.008,.002,zback+1.25),(x,.002,zback+1.25)],[(0,1,2,3)],parent,joint_mat,'interior')
    mesh(spec['root']+' bay back wall',[(x0,0,zback+1.25),(x1,0,zback+1.25),(x1,h,zback+1.25),(x0,h,zback+1.25)],[(0,1,2,3)],parent,art.data.materials[0],'interior-art',[(u0,1-spec['back_floor']/H),(u1,1-spec['back_floor']/H),(u1,v1),(u0,v1)])
    for x in [x0,x1]:
        mesh(spec['root']+' bay jamb '+str(x),[(x,0,zfront+1.25),(x,0,zback+1.25),(x,h,zback+1.25),(x,h,zfront+1.25)],[(0,1,2,3)],parent,wall_mat,'interior')
    # The ceiling hides vehicles behind the lintel instead of letting them show through the roof.
    mesh(spec['root']+' bay ceiling',[(x0,h,zfront+1.25),(x1,h,zfront+1.25),(x1,h,-1.25+1.25),(x0,h,-1.25+1.25)],[(0,1,2,3)],parent,wall_mat,'interior')
    prism(spec['root']+' lintel',[(x0,h),(x1,h),(x1,roofh),(x0,roofh)],zfront,.52,parent,'occluder')
    # Solid walls leave the door opening clear; they cast rather than the alpha artwork.
    for a,b in [(-3.3,x0),(x1,3.3)]:prism(spec['root']+' solid pier '+str(a),[(a,0),(b,0),(b,roofh),(a,roofh)],-1.8,.55,parent)
    prism(spec['root']+' solid header',[(x0,h),(x1,h),(x1,roofh),(x0,roofh)],-1.8,.55,parent)
    if spec['root']=='Foundry':
        # Profile slopes up to the right, matching all four imagegen northlight bays.
        for index,(a,b) in enumerate([(210,375),(450,630),(695,877),(942,1190)]):
            xa,xb=(a-cx)*scale,(b-cx)*scale
            peak=roofh+.42
            prism('Foundry sawtooth roof '+str(index),[(xa,roofh),(xb,roofh),(xb,peak)],-1.8,.55,parent)
        # An opaque cylinder has a proper volume, unlike the alpha chimney strip.
        chimney_x=(sum(spec['chimney'])/2-cx)*scale
        chimney_top=((spec['ground']-50)*scale+s*(-1.3-.55))/c
        bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.21,depth=chimney_top-roofh,location=P((chimney_x,(chimney_top+roofh)/2,-1.3+1.25)))
        o=bpy.context.object;o.name='Foundry chimney shadow volume';o.parent=parent;o.data.materials.append(volume_mat);o['architecture_role']='caster'
    else:prism('Warehouse solid phone roof',[(-3.3,roofh),(3.3,roofh),(3.3,roofh+.15),(-3.3,roofh+.15)],-1.8,.71,parent)
    parent['physical_loading_bay']=True;parent['loading_bay_floor']=0;parent['loading_bay_back']=zback;parent['loading_bay_portal']=[x0,x1,h,zfront]
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'factory-building-v5.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'factory-building-v5-raw.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_animations=False,export_extras=True,export_image_format='WEBP',export_image_quality=92)
