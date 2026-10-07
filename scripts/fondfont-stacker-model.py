"""Volumetric pallet stackers based on imagegen's four-view machinery reference v2."""
def build(api):
    group,box,cylinder,rod,torus,mesh=(api[k] for k in ['group','box','cylinder','rod','torus','mesh'])
    for prefix,x in [('Source',-5.6),('Receiver',5.6)]:
        body=group(prefix+'Stacker',at=(x,0,-.2))
        body['native_forklift_revision']='grounded-tread-and-low-chassis-v4'
        box('Counterweight chassis',1.04,.28,1.25,(0,.24,-.38),'iron',body,.085)
        box('Narrow front axle housing',.64,.19,.38,(0,.25,.40),'iron',body,.055)
        rod('Exposed front drive axle',(-.58,.30,.40),(.58,.30,.40),.055,'steel',body)
        box('Rounded rear ballast',1.08,.58,.54,(0,.61,-.73),'orange',body,.14)
        box('Battery compartment',.96,.28,.65,(0,.46,-.28),'sage',body,.08)
        for side in [-1,1]:
            box('Formed side pod',.15,.22,.65,(side*.49,.56,-.28),'sage',body,.06)
            box('Footwell step',.13,.06,.34,(side*.55,.35,.06),'steel',body,.02)
            box('Rear access seam',.018,.30,.37,(side*.547,.64,-.73),'iron',body,.005)
            box('Counterweight inset lamp',.026,.07,.12,(side*.552,.70,-.83),'lamp',body,.01)
            # A true curved wheel arch leaves the tire sidewall exposed.
            import math
            verts=[]
            for xx in [side*.52,side*.66]:
                for r in [.335,.375]:
                    for j in range(21):
                        a=math.pi*j/20;verts.append((xx,.30+r*math.sin(a),.40+r*math.cos(a)))
            faces=[]
            for j in range(20):
                faces.extend([(j,j+1,22+j,21+j),(42+j,63+j,64+j,43+j),(j,42+j,43+j,j+1),(21+j,22+j,64+j,63+j)])
            faces.extend([(0,21,63,42),(20,62,83,41)])
            mesh('Curved front wheel arch',verts,faces,'sage',body,.006)
            rod('Rear overhead guard pillar',(side*.50,.70,-.80),(side*.50,1.425,-.68),.028,'iron',body)
            rod('Front overhead guard pillar',(side*.50,.52,.28),(side*.50,1.425,.33),.028,'iron',body)
            rod('Protective roof perimeter',(side*.50,1.435,-.68),(side*.50,1.435,.33),.035,'iron',body)
        for zz in [-.68,-.43,-.18,.07,.33]:box('Guard roof cross slat',1.06,.035,.045,(0,1.435,zz),'iron',body,.01)
        box('Contoured seat cushion',.57,.10,.43,(0,.65,-.36),'rubber',body,.07)
        seat=box('Contoured seat back',.55,.38,.075,(0,.89,-.58),'rubber',body,.065)
        for xx in [-.29,.29]:box('Seat armrest',.06,.055,.28,(xx,.82,-.37),'rubber',body,.02)
        rod('Steering column',(0,.51,.22),(0,.94,.03),.036,'iron',body)
        steering=torus('Steering wheel',.15,.018,(0,.96,.02),'black',body,'y')
        steering.rotation_euler[0]=.35
        for xx in [-.055,.055]:rod('Control lever',(xx+.31,.57,.08),(xx+.31,.87,.02),.012,'steel',body)
        cylinder('Amber warning lamp',.049,.06,(.37,1.49,-.53),'lamp',body,'y',24)
        for zz,radius in [(-.75,.24),(.40,.30)]:
            for side in [-1,1]:
                wheel=group(prefix+f'StackerWheel{side}_{zz}',body,(side*.60,radius,zz));wheel['radius']=radius
                # Continuous shoulder rings support the tire at every roll angle;
                # recessed chevron grooves make front-on rolling visible.
                profile=[(-.12,.78),(-.115,.94),(-.09,1),(-.055,1),(.055,1),(.09,1),(.115,.94),(.12,.78)]
                verts=[]
                for k,(xx,rr) in enumerate(profile):
                    for j in range(96):
                        angle=math.tau*j/96
                        groove=.012 if k in [3,4] and (j+(3 if k==4 else 0))%6<2 else 0
                        r=radius*rr-groove
                        verts.append((xx,r*math.cos(angle),r*math.sin(angle)))
                faces=[(k*96+j,k*96+(j+1)%96,(k+1)*96+(j+1)%96,(k+1)*96+j) for k in range(len(profile)-1) for j in range(96)]
                tire=mesh('Rounded solid tire with recessed chevron tread',verts,faces,'rubber',wheel)
                for face in tire.data.polygons:face.use_smooth=True
                for face in [-.122,.122]:
                    cylinder('Forklift ivory wheel dish',radius*.63,.015,(face,0,0),'ivory',wheel,'x',32)
                    cylinder('Forklift hub boss',radius*.27,.023,(face,0,0),'steel',wheel,'x',24)
                    for j in range(6):
                        angle=math.tau*j/6
                        cylinder('Hub lug',.012,.026,(face,radius*.43*math.cos(angle),radius*.43*math.sin(angle)),'iron',wheel,'x',8)
        for side in [-1,1]:
            xx=side*.38
            box('Mast outer channel',.095,1.40,.13,(xx,.78,.55),'mastSteel',body,.009)
            for z in [.49,.61]:box('Mast channel flange',.13,1.40,.025,(xx,.78,z),'mastSteel',body,.006)
        for yy in [.12,1.46]:box('Mast cross tie',.88,.07,.13,(0,yy,.55),'iron',body,.012)
        inner=group(prefix+'InnerMast',body)
        for side in [-1,1]:
            xx=side*.285
            box('Telescoping mast channel',.075,1.34,.085,(xx,.79,.60),'mastSteel',inner,.007)
            rod('Lift chain',(xx,.15,.65),(xx,1.40,.65),.012,'iron',inner)
        box('Inner mast top tie',.63,.055,.10,(0,1.435,.60),'iron',inner,.008)
        cylinder('Hydraulic barrel',.058,.78,(0,.52,.50),'iron',body,'y',24)
        piston=group(prefix+'Piston',body)
        cylinder('Hydraulic piston',.029,.75,(0,.40,.50),'steel',piston,'y',20)
        forks=group(prefix+'Forks',body,(0,.127,0))
        box('Fork carriage crossbar',1.10,.15,.14,(0,.25,.70),'mastSteel',forks,.015)
        for xx in [-.52,.52]:rod('Load backrest upright',(xx,.06,.70),(xx,.45,.70),.024,'mastSteel',forks)
        box('Load backrest top rail',1.08,.055,.07,(0,.45,.70),'mastSteel',forks,.01)
        for xx in [-.26,0,.26]:rod('Load backrest bars',(xx,.08,.70),(xx,.45,.70),.014,'mastSteel',forks)
        reach=group(prefix+'ForkReach',forks)
        reach['extension']=.35
        for xx in [-.34,.34]:
            box('Fork heel',.115,.38,.12,(xx,.19,.69),'forkSteel',forks,.014)
            verts=[(xx+side*.0575,y,z) for side in [-1,1] for z,y in [(.70,0),(1.75,0),(1.75,-.035),(.70,-.055)]]
            faces=[(3,2,1,0),(4,5,6,7)]+[(j,(j+1)%4,(j+1)%4+4,j+4) for j in range(4)]
            mesh('Forged outer fork sleeve',verts,faces,'forkSteel',forks,.008)
            verts=[(xx+side*.045,y,z) for side in [-1,1] for z,y in [(1.10,-.005),(1.75,-.005),(1.75,-.015),(1.55,-.045),(1.10,-.045)]]
            faces=[(4,3,2,1,0),(5,6,7,8,9)]+[(j,(j+1)%5,(j+1)%5+5,j+5) for j in range(5)]
            mesh('Sliding tapered fork tine',verts,faces,'forkSteel',reach,.006)
        for xx in [-.38,.38]:
            cylinder('Carriage guide roller',.055,.055,(xx,.25,.62),'mastSteel',forks,'x',20)
        # Hydraulic hoses have real round sections and connect the mast to its housing.
        rod('Hydraulic supply hose',(-.18,.82,.29),(-.18,.20,.49),.012,'rubber',body)
        rod('Hydraulic return hose',(.18,.82,.29),(.18,.20,.49),.012,'rubber',body)
