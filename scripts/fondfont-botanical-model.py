"""Real botanical geometry, modeled from the complete imagegen reference v2.
Curved solid petals, connected stems/leaves and dimensional pollen; no image cards.
Coordinates use glTF Y-up until conversion when writing Blender vertices.
"""
import bpy, bmesh, math, random
from mathutils import Vector

def build_botanicals(parent):
    rng=random.Random(47)
    def material(name,color,rough=.65):
        m=bpy.data.materials.new('Botanical '+name);m.use_nodes=True
        bs=m.node_tree.nodes.get('Principled BSDF')
        rgb=[int(color[i:i+2],16)/255 for i in (1,3,5)]
        rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
        bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Roughness'].default_value=rough
        bs.inputs['Subsurface Weight'].default_value=.08
        return m
    mats=[material('sage leaf','#718365'),material('stem','#66704b'),material('ivory petal','#f3ecd6'),material('petal underside','#d5ceb2'),material('blush petal','#c78e99'),material('ochre pollen','#bb8f35'),material('seed head','#a59768')]
    def plant(name,x,z,height,kind,lean,azimuth):
        verts=[];faces=[];slots=[]
        def add(vs,fs,mi):
            k=len(verts);verts.extend(vs);faces.extend([tuple(k+i for i in f) for f in fs]);slots.extend([mi]*len(fs))
        def tube(points,radii,mi,sides=7):
            vs=[];fs=[]
            for i,(point,radius) in enumerate(zip(points,radii)):
                d=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
                u=d.cross(Vector((0,0,1))).normalized();v=d.cross(u).normalized()
                for j in range(sides):vs.append(point+radius*(math.cos(j*math.tau/sides)*u+math.sin(j*math.tau/sides)*v))
            for i in range(len(points)-1):
                for j in range(sides):a=i*sides+j;b=i*sides+(j+1)%sides;fs.append((a,b,b+sides,a+sides))
            fs.extend([tuple(reversed(range(sides))),tuple((len(points)-1)*sides+j for j in range(sides))]);add(vs,fs,mi)
        def blade(center,u,v,n,length,width,cup,mi,under,inner=0):
            # Closed upper/lower surfaces, a raised midrib, swept outline and fine lobes.
            vs=[];fs=[];rows,cols=10,4
            for layer in [0,1]:
                for i in range(rows+1):
                    t=i/rows;shape=math.sin(math.pi*t)**.65
                    for j in range(cols+1):
                        side=j/cols*2-1
                        radial=inner+t*length
                        height=cup*(.7*t*t-.18*math.sin(math.pi*t))+.012*shape*(1-side*side)
                        height+=.002*math.sin(t*math.pi*5)*abs(side)*shape
                        vs.append(center+u*radial+v*(width*shape*side)+n*(height-layer*.0025))
            stride=(rows+1)*(cols+1)
            for layer in [0,1]:
                for i in range(rows):
                    for j in range(cols):
                        k=layer*stride+i*(cols+1)+j;f=(k,k+1,k+cols+2,k+cols+1)
                        fs.append(f if layer==0 else tuple(reversed(f)))
            k0=len(verts);add(vs,fs,mi)
            for fi in range(rows*cols,len(fs)):slots[len(slots)-len(fs)+fi]=under
            boundary=list(range(cols+1))+[i*(cols+1)+cols for i in range(1,rows+1)]+[rows*(cols+1)+j for j in range(cols-1,-1,-1)]+[i*(cols+1) for i in range(rows-1,0,-1)]
            for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.append((k0+a,k0+b,k0+b+stride,k0+a+stride));slots.append(under)
        def sphere(center,radius,mi,sy=1):
            vs=[];fs=[];rings,sides=5,8
            for i in range(rings+1):
                phi=math.pi*i/rings
                for j in range(sides):
                    theta=math.tau*j/sides;vs.append(center+Vector((radius*math.sin(phi)*math.cos(theta),radius*math.cos(phi)*sy,radius*math.sin(phi)*math.sin(theta))))
            for i in range(rings):
                for j in range(sides):a=i*sides+j;b=i*sides+(j+1)%sides;fs.append((a,b,b+sides,a+sides))
            add(vs,fs,mi)
        direction=Vector((math.cos(azimuth),0,math.sin(azimuth)))
        stem=[Vector((0,height*t,0))+direction*(lean*t*t) for t in [i/12 for i in range(13)]]
        tube(stem,[.009*(1-i/24) for i in range(13)],1)
        for j,t in enumerate([.17,.33,.52,.68]):
            center=Vector((0,height*t,0))+direction*(lean*t*t)
            theta=azimuth+j*2.7;u=Vector((math.cos(theta),.38,math.sin(theta))).normalized();v=u.cross(Vector((0,1,0))).normalized();n=v.cross(u).normalized()
            blade(center,u,v,n,.20*(1-.5*t),.035 if kind=='daisy' else .026,-.09,0,0)
        for j in range(4):
            theta=azimuth+j*2.4
            u=Vector((math.cos(theta),.42,math.sin(theta))).normalized();v=u.cross(Vector((0,1,0))).normalized();n=v.cross(u).normalized()
            blade(Vector((0,.012,0)),u,v,n,.23+rng.random()*.08,.042,-.07,0,0)
        if name.endswith(('0','3','6')):
            for j in range(2):
                theta=azimuth+j*1.9
                u=Vector((.34*math.cos(theta),1,.34*math.sin(theta))).normalized();v=u.cross(Vector((0,1,0))).normalized();n=v.cross(u).normalized()
                blade(Vector((.025*j,.002,0)),u,v,n,.33+j*.09,.009,-.12,0,0)
        center=stem[-1];axis=Vector((.14*math.sin(azimuth),1,.22*math.cos(azimuth))).normalized()
        u=Vector((1,-axis.x/axis.y,0)).normalized();v=axis.cross(u).normalized()
        count=18 if kind=='daisy' else 8
        for j in range(count):
            theta=j*math.tau/count+rng.uniform(-.045,.045);radial=u*math.cos(theta)+v*math.sin(theta);side=axis.cross(radial)
            length=(.105 if kind=='daisy' else .11)*rng.uniform(.85,1.08)
            blade(center,radial,side,axis,length,.015 if kind=='daisy' else .042,-.055 if kind=='daisy' else .07,2 if kind=='daisy' else 4,3 if kind=='daisy' else 4,.022)
        # Joined green sepals cup the underside rather than floating below the bloom.
        for j in range(7):
            theta=j*math.tau/7;radial=u*math.cos(theta)+v*math.sin(theta)
            blade(center-axis*.012,radial,axis.cross(radial),axis,.04,.012,-.025,0,0,.006)
        sphere(center+axis*.009,.032,5,.65)
        for j in range(47):
            r=.031*math.sqrt((j+.5)/47);theta=j*2.39996
            pollen=center+u*(r*math.cos(theta))+v*(r*math.sin(theta))+axis*(.011+.019*math.sqrt(max(0,1-(r/.032)**2)))
            sphere(pollen,.0037,5,.85)
        me=bpy.data.meshes.new(name);me.from_pydata([(p.x,-p.z,p.y) for p in verts],[],faces);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        for m in mats:me.materials.append(m)
        for poly,mi in zip(me.polygons,slots):poly.material_index=mi;poly.use_smooth=True
        o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.parent=parent;o.location=(x,-z,.005)
        o['native_botanical']=True;o['reference']='botanical-native-reference-v2.png';o['root_height']=height
        return o
    layout=[(-.64,-.7,.72,'daisy',.07,.3),(-.27,-.84,.90,'daisy',.10,2.1),(.08,-.53,.57,'daisy',.08,4.5),(.40,-.7,.70,'cosmos',.09,1.1),(.70,-.48,.46,'cosmos',.08,3.8),(-.44,-.35,.42,'daisy',.06,5.1),(.22,-.23,.38,'cosmos',.06,2.6),(-.90,-.56,.46,'daisy',.08,1.7),(-.58,-1.02,.62,'cosmos',.06,4.0),(.11,-1.03,.76,'daisy',.08,5.4),(.74,-.88,.59,'cosmos',.07,.6),(-.12,-.31,.49,'daisy',.06,2.8),(.51,-.18,.34,'daisy',.04,5.7),(.98,-.50,.37,'cosmos',.05,3.1)]
    for i,(x,z,h,kind,lean,azimuth) in enumerate(layout):plant('Native '+kind+' '+str(i),x,z,h,kind,lean,azimuth)
    return dict(camera_pitch=math.atan2(19,29.5),max_sway=.006,patches=[dict(kind='native mixed flowers',x=0,y=.005,z=-.55,width=2.7,height=.95)],native=True,plant_count=len(layout),reference='botanical-native-reference-v2.png')
