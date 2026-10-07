"""Native sculpted pets and articulated butterflies, from imagegen reference v1.
The image is a construction guide only; no raster textures are used on these meshes.
"""
import bpy, bmesh, math, random
from mathutils import Vector

def build_garden_life(parent):
    def P(v):return (v[0],-v[2],v[1])
    def group(name,par,at=(0,0,0)):
        o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=par;o.location=P(at);return o
    def material(name,color,rough=.75):
        m=bpy.data.materials.new('Garden life '+name);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF')
        c=[int(color[i:i+2],16)/255 for i in (1,3,5)];c=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c]
        s.inputs['Base Color'].default_value=(*c,1);s.inputs['Roughness'].default_value=rough;return m
    def paint(obj,coat,ivory,cat,face=False):
        def smooth(a,b,x):
            t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
        base=tuple(coat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value)
        light=tuple(ivory.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value)
        m=coat.copy();m.name='Sculpted '+obj.name+' coat';n=m.node_tree.nodes.new('ShaderNodeVertexColor');n.layer_name='Coat'
        m.node_tree.links.new(n.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
        obj.data.materials.clear();obj.data.materials.append(m)
        layer=obj.data.color_attributes.new(name='Coat',type='FLOAT_COLOR',domain='CORNER')
        for loop in obj.data.loops:
            p=obj.matrix_local@obj.data.vertices[loop.vertex_index].co
            cream=smooth(.07,.14,p.x)*(1-smooth(.005,.075,p.z)) if face else (0 if cat else smooth(.11,.22,p.x)*(1-smooth(.03,.14,p.z)))
            stripe=(smooth(.35,.85,math.sin((p.x+.3)*39+p.y*8))*smooth(.055,.095,abs(p.y)) if not face else smooth(.2,.8,math.cos(p.y*65+p.x*12))*smooth(.075,.12,p.z)) if cat else 0
            layer.data[loop.index].color=tuple((base[i]*(1-cream)+light[i]*cream)*(1-.38*stripe) for i in range(3))+(1,)
        for poly in obj.data.polygons:poly.material_index=0
    def groom(obj,par,cat,face=False):
        """Short closed tapered fur clumps; native geometry, never alpha cards."""
        rng=random.Random(517 if cat else 219);verts=[];faces=[];colors=[]
        obj.data.calc_loop_triangles();triangles=list(obj.data.loop_triangles)
        layer=obj.data.color_attributes['Coat'];normal_matrix=obj.matrix_local.to_3x3()
        for i in range(6000 if not cat else 5000):
            tri=rng.choice(triangles);a,b,c=[obj.data.vertices[j] for j in tri.vertices]
            u=math.sqrt(rng.random());v=rng.random();w=(1-u,u*(1-v),u*v)
            point=obj.matrix_local@(a.co*w[0]+b.co*w[1]+c.co*w[2])
            if not face and point.z<-.005:continue
            if face and (point.x>.14 or (abs(point.y)>.09 and point.x>.055 and point.z>.025)):continue
            n=(normal_matrix@(a.normal*w[0]+b.normal*w[1]+c.normal*w[2])).normalized()
            tangent=Vector((-.8,0,-.2 if face else 0));tangent=(tangent-n*tangent.dot(n)).normalized()
            bitangent=n.cross(tangent).normalized();length=(.006 if cat else .009)*rng.uniform(.75,1.25);width=.00032 if cat else .00038
            base=len(verts);color=tuple(sum(layer.data[j].color[k] for j in tri.loops)/3*rng.uniform(.96,1.04) for k in range(3))+(1,)
            for ring in range(2):
                center=point+n*(length*.08*ring)+tangent*(length*.32*ring)
                for j in range(4):
                    q=center+(tangent*math.cos(j*math.tau/4)+bitangent*math.sin(j*math.tau/4))*width*(1-.4*ring)
                    verts.append(tuple(q));colors.append(color)
            verts.append(tuple(point+n*(length*.12)+tangent*length));colors.append(color)
            faces.append((base+3,base+2,base+1,base))
            for j in range(4):
                faces.append((base+j,base+(j+1)%4,base+4+(j+1)%4,base+4+j));faces.append((base+4+j,base+4+(j+1)%4,base+8))
        me=bpy.data.meshes.new('Groomed closed fur geometry');me.from_pydata(verts,[],faces);me.update();me.materials.append(obj.data.materials[0])
        fur=bpy.data.objects.new(('Cat' if cat else 'Dog')+' fine sculpted fur',me);bpy.context.collection.objects.link(fur);fur.parent=par
        color_layer=me.color_attributes.new(name='Coat',type='FLOAT_COLOR',domain='CORNER')
        for loop in me.loops:color_layer.data[loop.index].color=colors[loop.vertex_index]
        for poly in me.polygons:poly.use_smooth=True
    cream=material('puppy cream','#cba66b');ivory=material('soft ivory','#eadbc0');gray=material('kitten gray','#8c8e91');dark=material('charcoal detail','#423b35');pink=material('ear blush','#c89c9b');eye=material('eyes','#211e1a',.22)
    ear_coat=material('puppy ears','#b98f5d');iris=material('kitten muted green iris','#959d75',.32)
    gold=material('butterfly warm ivory','#e5cc82');wingEdge=material('butterfly umber border','#6b5b42');wingDot=material('butterfly golden spots','#b9954d')
    def ellipsoid(name,par,at,scale,mat):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=28,ring_count=16,location=P(at))
        o=bpy.context.object;o.name=name;o.scale=(scale[0],scale[2],scale[1]);o.parent=par;o.data.materials.append(mat)
        for poly in o.data.polygons:poly.use_smooth=True
        bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        return o
    def curve(name,par,points,radius,mat,radii=None):
        data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=12;data.bevel_depth=radius;data.bevel_resolution=3;data.use_fill_caps=True
        path=data.splines.new('BEZIER');path.bezier_points.add(len(points)-1)
        for i,(point,value) in enumerate(zip(path.bezier_points,points)):
            point.co=P(value);point.handle_left_type='AUTO';point.handle_right_type='AUTO'
            if radii:point.radius=radii[i]
        o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.parent=par;data.materials.append(mat)
        bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o
    def sculpt(name,par,parts,mat,voxel=.014):
        objects=[ellipsoid(name,par,at,scale,mat) for at,scale in parts]
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=objects[0];o.name=name
        mod=o.modifiers.new('Continuous sculpted anatomy','REMESH');mod.mode='VOXEL';mod.voxel_size=voxel;mod.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=mod.name)
        mod=o.modifiers.new('Soft anatomical transitions','SMOOTH');mod.factor=1.0;mod.iterations=3;bpy.ops.object.modifier_apply(modifier=mod.name)
        o.select_set(False);return o
    def ear(name,par,at,cat,side,mat):
        if not cat:
            o=ellipsoid(name,par,at,(.075,.125,.038),mat)
            for v in o.data.vertices:
                t=(v.co.z+.125)/.25;v.co.x+=.026*(1-t)**2;v.co.y+=side*.016*(1-t)
            o.rotation_euler[1]=side*.10;return o
        o=ellipsoid(name,par,at,(.065,.085,.032),mat)
        for vertex in o.data.vertices:
            t=(vertex.co.z+.085)/.17
            vertex.co.x*=1-.75*t;vertex.co.y+=.018*t*t;vertex.co.z+=.035*t*t
        return o
    for species,coat in [('Dog',cream),('Cat',gray)]:
        cat=species=='Cat';root=group('Pet'+species,parent);root['native_garden_life']=True;root['reference']='pet-sculpt-reference-v3.png'
        body=group('Pet'+species+'Body',root,at=(0,.29,0))
        torso=sculpt('Connected '+species+' torso',body,[((-.08,.065,0),(.255,.105 if cat else .145,.10 if cat else .145)),((.115,.095,0),(.135,.125 if cat else .175,.10 if cat else .145)),((-.23,.06,0),(.135,.12 if cat else .145,.105 if cat else .135))],coat,.009)
        core=[torso]
        if cat:
            stripe=material('kitten tabby fur','#54575b');torso.data.materials.append(stripe)
            for poly in torso.data.polygons:
                p=torso.matrix_local@poly.center
                if abs(p.y)>.06 and p.z>.07 and math.sin((p.x+.3)*39+p.y*8)>.65:poly.material_index=len(torso.data.materials)-1
        head=group('Pet'+species+'Head',body,at=(.215,.175,0))
        face=sculpt('Connected '+species+' face',head,[((.018,.025,0),(.135 if cat else .14,.125 if cat else .13,.128 if cat else .137)),((.105,-.012,0),(.074 if cat else .095,.055 if cat else .067,.078 if cat else .095)),((.084,-.020,-.052),(.061,.054,.059)),((.084,-.020,.052),(.061,.054,.059))],coat,.006)
        face.data.materials.append(ivory)
        if cat:face.data.materials.append(stripe)
        for poly in face.data.polygons:
            p=face.matrix_local@poly.center
            if p.x>.095 and p.z<.035:poly.material_index=1
            elif cat and p.z>.10 and math.cos(p.y*65+p.x*12)>.35:poly.material_index=2
        paint(face,coat,ivory,cat,True)
        groom(face,head,cat,True)
        nose=ellipsoid(species+' nose',head,(.174 if cat else .20,-.005,0),(.020 if cat else .03,.015 if cat else .023,.023 if cat else .036),pink if cat else dark)
        curve(species+' soft mouth',head,[(.17 if cat else .197,-.022,-.035),(.18 if cat else .207,-.037,0),(.17 if cat else .197,-.022,.035)],.0023,dark)
        for side in [-1,1]:
            ez=.103 if cat else .119
            ellipsoid(species+' soft eyelid',head,(.083,.065,side*ez),(.025,.027,.017),dark)
            ellipsoid(species+' eye',head,(.087,.066,side*(ez+.008)),(.021,.023,.012),iris if cat else eye)
            if cat:ellipsoid(species+' slit pupil',head,(.096,.067,side*(ez+.018)),(.009,.020,.005),eye)
            ellipsoid(species+' eye catchlight',head,(.098,.076,side*(ez+.021)),(.005,.006,.003),ivory)
            ear(species+' ear',head,(-.015,.12 if cat else .015,side*.09 if cat else side*.137),cat,side,coat if cat else ear_coat)
            if cat:
                ear(species+' inner ear',head,(-.004,.13,side*.096),True,side,pink).scale=(.58,.6,.70)
                for j in range(3):curve(species+' whisker',head,[(.12,-.02,side*.05),(.16+j*.01,-.01+j*.013,side*.12),(.18+j*.01,-.03+j*.025,side*.18)],.0013,ivory)
        tail=group('Pet'+species+'Tail',body,at=(-.29,.08,0))
        if cat:curve(species+' softly curved tail',tail,[(0,0,0),(-.10,.09,0),(-.17,.23,.012),(-.15,.34,.02),(-.08,.37,.02)],.026,coat,[1,1,.85,.55,.06])
        else:
            mid=group('PetDogTailMid',tail,at=(-.10,.04,0));group('PetDogTailTip',mid,at=(-.11,.05,0))
            tailmesh=curve('Dog softly feathered tail',tail,[(0,0,0),(-.10,.04,0),(-.19,.09,.008),(-.28,.16,.012),(-.31,.20,.012)],.047,coat,[1,1.08,1,.62,.03]);tailmesh['native_tail']=True
            for side in [-1,1]:
                for j in range(5):
                    x=-.07-j*.038;y=.03+j*.023
                    tuft=curve('Dog tail soft feather',tail,[(x,y,side*.018),(x-.035,y-.02,side*.032),(x-.06,y-.035,side*.015)],.010,ivory if j%3==0 else coat,[1,.7,.02]);tuft['native_tail']=True
        for front,x in [('F',.17),('B',-.22)]:
            for side,z in [('L',-.10),('R',.10)]:
                leg=group('Pet'+species+'Hip'+front+side,root,at=(x,.29 if front=='F' else .31,z));leg['length']=.13
                lower=.13 if front=='F' else .14
                ankle=math.hypot(.008,.028) if front=='F' else math.hypot(.03,.045)
                knee=group('Pet'+species+'Knee'+front+side,leg,at=(0,-.13,0));knee['length']=lower
                hock=group('Pet'+species+'Hock'+front+side,knee,at=(0,-lower,0));hock['length']=ankle
                paw=group('Pet'+species+'Paw'+front+side,hock,at=(0,-ankle,0))
                # Shoulder/thigh volume merges into the torso; lower limbs taper.
                width=(.045 if cat else .064) if front=='F' else (.063 if cat else .083)
                core.append(sculpt(species+' shoulder' if front=='F' else species+' thigh',leg,[((0,.015,0),(width,.095,width*.85)),((0,-.06,0),(width*.76,.075,width*.70)),((0,-.12,0),(.029,.036,.030))],coat,.006))
                core.append(sculpt(species+' tapered lower limb',knee,[((0,-.025,0),(.029 if cat else .037,.048,.030)),((0,-lower*.65,0),(.025 if cat else .030,.055,.028)),((0,-lower,0),(.026,.029,.030))],coat,.005))
                core.append(sculpt(species+' wrist' if front=='F' else species+' metatarsal',hock,[((0,-ankle*.35,0),(.022,ankle*.6,.025)),((.008,-ankle*.85,0),(.026,ankle*.35,.029))],coat,.004))
                core.append(ellipsoid(species+' paw pad volume',paw,(.018,0,0),(.041 if cat else .047,.027,.034 if cat else .041),coat))
                for toe in range(4):
                    core.append(ellipsoid(species+' subtle toe',paw,(.045,-.004,(toe-1.5)*(.014 if cat else .017)),(.018,.016,.010 if cat else .012),coat))
        # One continuous surface across body, thighs, elbows, wrists and toes.
        bpy.ops.object.select_all(action='DESELECT')
        for o in core:o.select_set(True)
        bpy.context.view_layer.objects.active=torso;bpy.ops.object.join()
        mod=torso.modifiers.new('Continuous torso and limb skin','REMESH');mod.mode='VOXEL';mod.voxel_size=.0055;mod.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=mod.name)
        mod=torso.modifiers.new('Smooth shoulder elbow hock transitions','SMOOTH');mod.factor=.65;mod.iterations=3;bpy.ops.object.modifier_apply(modifier=mod.name)
        paint(torso,coat,ivory,cat)
        groom(torso,body,cat)
        torso['continuous_pet_core']=True;torso.select_set(False)
    butterfly=group('Butterfly',parent);butterfly['native_garden_life']=True
    ellipsoid('Butterfly body',butterfly,(0,0,0),(.019,.018,.10),dark)
    ellipsoid('Butterfly head',butterfly,(0,.005,-.095),(.027,.023,.025),dark)
    for side in [-1,1]:
        curve('Butterfly antenna',butterfly,[(side*.012,.015,-.1),(side*.03,.04,-.14),(side*.05,.055,-.17)],.0025,dark)
        wing=group('ButterflyWing'+('L' if side<0 else 'R'),butterfly)
        # Two pairs of thin, closed, curved lobes; border and spots are geometry.
        for z0,rx,rz in [(-.04,.17,.13),(.095,.13,.10)]:
            verts=[];faces=[];rings,sides=7,28
            for layer in [0,1]:
                for i in range(rings+1):
                    r=i/rings
                    for j in range(sides):
                        a=j*math.tau/sides;x=side*(.02+rx+rx*r*math.cos(a));z=z0+rz*r*math.sin(a);y=.045*math.sin(r*math.pi/2)-.003*layer
                        verts.append((x,y,z))
                for i in range(rings):
                    for j in range(sides):k=layer*(rings+1)*sides+i*sides+j;l=layer*(rings+1)*sides+i*sides+(j+1)%sides;faces.append((k,l,l+sides,k+sides))
            for j in range(sides):a=rings*sides+j;b=rings*sides+(j+1)%sides;faces.append((a,b,b+(rings+1)*sides,a+(rings+1)*sides))
            me=bpy.data.meshes.new('Curved butterfly wing');me.from_pydata([P(v) for v in verts],[],faces);me.update();me.materials.append(gold);me.materials.append(wingEdge)
            bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
            for poly in me.polygons:poly.use_smooth=True;poly.material_index=0
            # Narrow border is a real swept tube around the wing perimeter.
            points=[(side*(.02+rx+rx*math.cos(j*math.tau/28)),.047,z0+rz*math.sin(j*math.tau/28)) for j in range(29)]
            o=bpy.data.objects.new('Dimensional butterfly membrane',me);bpy.context.collection.objects.link(o);o.parent=wing
            curve('Fine wing border',wing,points,.004,wingEdge)
            for j in range(8):
                a=j*math.tau/8;ellipsoid('Golden wing spot',wing,(side*(.02+rx+rx*.86*math.cos(a)),.05,z0+rz*.86*math.sin(a)),(.007,.003,.009),wingDot)
    return {'pets':['PetDog','PetCat'],'butterfly':'Butterfly','native':True}
