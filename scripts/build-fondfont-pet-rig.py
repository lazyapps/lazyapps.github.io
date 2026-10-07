"""Editable native armatures and planted-paw turn clips; no raster animal assets."""
import bpy, math, json, importlib.util
from pathlib import Path
from mathutils import Vector, Quaternion, Matrix
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scripts/assets/fondfont/blender-v2'
bpy.ops.wm.read_factory_settings(use_empty=True)
spec=importlib.util.spec_from_file_location('garden_model',ROOT/'scripts/fondfont-garden-life-model.py')
garden_model=importlib.util.module_from_spec(spec);spec.loader.exec_module(garden_model)
parent=bpy.data.objects.new('Garden rig source',None);bpy.context.collection.objects.link(parent)
garden_model.build_garden_life(parent)
bpy.context.view_layer.update()
def descendants(o):
    return [o]+[v for child in o.children for v in descendants(child)]
keep=set(descendants(bpy.data.objects['PetDog'])+descendants(bpy.data.objects['PetCat']))
for o in list(bpy.data.objects):
    if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
C=Matrix(((1,0,0),(0,0,-1),(0,1,0)))
def P(v):return C@Vector(v)
def Q(x=0,y=0,z=0):
    rotation=Matrix.Rotation(x,3,'X')@Matrix.Rotation(y,3,'Y')@Matrix.Rotation(z,3,'Z')
    return (C@rotation@C.transposed()).to_quaternion()
def smooth(v):v=max(0,min(1,v));return v*v*(3-2*v)
report={}
for species in ['Dog','Cat']:
    old=bpy.data.objects['Pet'+species];old.parent=None;old.matrix_world=Matrix.Identity(4)
    joint_objects=[o for o in descendants(old) if o.type=='EMPTY']
    original={o.name:(o.matrix_world.translation.copy(),o.parent.name if o.parent and o.parent is not old else None) for o in joint_objects if o is not old}
    meshes=[o for o in descendants(old) if o.type=='MESH']
    arm_data=bpy.data.armatures.new(species+' articulated skeleton')
    arm=bpy.data.objects.new('Pet'+species+'Armature',arm_data);bpy.context.collection.objects.link(arm)
    arm['native_garden_life']=True;arm['leg_reference']='pet-leg-anatomy-reference-v2.png';arm['turn_animation']='Blender planted-paw IK, 12 alternating steps per quarter turn'
    arm['sculpt_reference']='pet-sculpt-reference-v3.png'
    bpy.context.view_layer.objects.active=arm;arm.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    rootbone='Pet'+species+'Root'
    root=arm_data.edit_bones.new(rootbone);root.head=(0,0,0);root.tail=(0,.06,0)
    for name,(location,_) in original.items():
        b=arm_data.edit_bones.new(name);b.head=location;b.tail=location+Vector((0,.05,0));b.use_connect=False
    for name,(_,parent_name) in original.items():arm_data.edit_bones[name].parent=arm_data.edit_bones[parent_name or rootbone]
    bpy.ops.object.mode_set(mode='OBJECT');arm.select_set(False)
    for mesh in meshes:
        joint=mesh.parent.name;world=mesh.matrix_world.copy();mesh.parent=None;mesh.matrix_world=world
        name=joint if joint in original else rootbone
        if mesh.get('native_tail'):
            names=['PetDogTail','PetDogTailMid','PetDogTailTip']
            groups=[mesh.vertex_groups.new(name=n) for n in names]
            base_x=original[names[0]][0].x
            for vertex in mesh.data.vertices:
                t=max(0,min(2,(base_x-(world@vertex.co).x)/.14))
                low=min(1,int(t));fraction=t-low
                groups[low].add([vertex.index],1-fraction,'REPLACE')
                if fraction:groups[low+1].add([vertex.index],fraction,'REPLACE')
        elif not mesh.get('continuous_pet_core'):
            mesh.vertex_groups.new(name=name).add(list(range(len(mesh.data.vertices))),1,'REPLACE')
        else:
            groups={n:mesh.vertex_groups.new(name=n) for n in original}
            for vertex in mesh.data.vertices:
                x,z,y=world@vertex.co;z=-z
                front='F' if abs(x-.17)<abs(x+.22) else 'B';side='L' if z<0 else 'R';suffix=front+side
                hx=.17 if front=='F' else -.22;hz=-.1 if side=='L' else .1
                # Smooth attachment weights at the shoulder/hip, then joint bands.
                attachment=math.exp(-((x-hx)/.085)**4-((z-hz)/.060)**4)
                influence=1 if y<.19 else attachment*smooth((.34-y)/.10)
                lower=.13 if front=='F' else .14;ankle_y=(.29 if front=='F' else .31)-.13-lower
                knee_blend=smooth(((.20 if front=='F' else .22)-y)/.085);hock_blend=smooth((ankle_y+.03-y)/.06)
                paw_blend=smooth((ankle_y+.004-y)/(.018 if front=='F' else .025))
                values={'Body':1-influence,'Hip'+suffix:influence*(1-knee_blend),
                        'Knee'+suffix:influence*knee_blend*(1-hock_blend),
                        'Hock'+suffix:influence*knee_blend*hock_blend*(1-paw_blend),
                        'Paw'+suffix:influence*knee_blend*hock_blend*paw_blend}
                for key,weight in values.items():
                    if weight>1e-5:groups['Pet'+species+key].add([vertex.index],weight,'REPLACE')
    bpy.ops.object.select_all(action='DESELECT')
    for mesh in meshes:mesh.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();skin=bpy.context.object;skin.name='Pet'+species+'Skin';skin.parent=arm
    modifier=skin.modifiers.new('Native joint deformation','ARMATURE');modifier.object=arm
    for o in joint_objects:bpy.data.objects.remove(o,do_unlink=True)
    arm.name='Pet'+species
    arm.animation_data_create()
    duration=2.4;fps=30;frames=round(duration*fps)
    max_reach=0
    for direction in [-1,1]:
        clip='Pet'+species+('TurnLeft' if direction==1 else 'TurnRight')
        action=bpy.data.actions.new(clip);arm.animation_data.action=action
        starts={};ends={}
        order=['FR','BL','FL','BR'] if direction==1 else ['FL','BR','FR','BL']
        placements={side:[] for side in order}
        for j in range(12):
            start=.025+j*.079;end=start+.10
            placements[order[j%4]].append((start,end))
        for frame in range(frames+1):
            p=frame/frames;angle=direction*math.pi/2*p;c=math.cos(angle);s=math.sin(angle)
            for bone in arm.pose.bones:bone.location=(0,0,0);bone.rotation_mode='QUATERNION';bone.rotation_quaternion=(1,0,0,0)
            arm.pose.bones[rootbone].rotation_quaternion=Q(y=angle)
            body=arm.pose.bones['Pet'+species+'Body'];body.location=P((0,-.009*math.sin(math.pi*p)**2,0));body.rotation_quaternion=Q(y=-direction*.07*math.sin(math.pi*p),x=direction*.025*math.sin(math.pi*p))
            arm.pose.bones['Pet'+species+'Head'].rotation_quaternion=Q(y=direction*.28*math.sin(math.pi*p))
            arm.pose.bones['Pet'+species+'Tail'].rotation_quaternion=Q(y=-direction*.10*math.sin(math.pi*p) if species=='Cat' else 0)
            for side in ['FL','FR','BL','BR']:
                hx=.17 if side[0]=='F' else -.22;hz=-.1 if side[1]=='L' else .1
                wx,wz=hx,hz;lift=0
                for start,end in placements[side]:
                    landing_angle=direction*math.pi/2*(1 if start>.64 else min(1,end+.035))
                    target=(math.cos(landing_angle)*hx+math.sin(landing_angle)*hz,-math.sin(landing_angle)*hx+math.cos(landing_angle)*hz)
                    if p>=end:wx,wz=target
                    elif p>=start:
                        u=(p-start)/(end-start);ease=smooth(u);wx=wx+(target[0]-wx)*ease;wz=wz+(target[1]-wz)*ease;lift=math.sin(math.pi*u)*.035;break
                    else:break
                dx=c*wx-s*wz-hx;dz=s*wx+c*wz-hz;dy=.027+lift-(.28 if side[0]=='F' else .30)
                lower=.13 if side[0]=='F' else .14;ax,ay=(.008,.028) if side[0]=='F' else (.03,.045)
                dx-=ax;dy+=ay
                reach=math.sqrt(dx*dx+dy*dy+dz*dz);max_reach=max(max_reach,reach)
                knee=(1 if side[0]=='F' else -1)*math.acos(max(-1,min(1,(reach*reach-.13**2-lower**2)/(2*.13*lower))))
                hip=math.atan2(dx,math.hypot(dy,dz))-math.atan2(lower*math.sin(knee),.13+lower*math.cos(knee));hipx=math.atan2(-dz,-dy)
                b=arm.pose.bones['Pet'+species+'Hip'+side];b.location=P((0,-.01,0));b.rotation_quaternion=Q(hipx,0,hip)
                arm.pose.bones['Pet'+species+'Knee'+side].rotation_quaternion=Q(z=knee)
                foot=Q(z=math.atan2(ax,ay))
                arm.pose.bones['Pet'+species+'Hock'+side].rotation_quaternion=(Q(hipx,0,hip)@Q(z=knee)).inverted()@foot
                arm.pose.bones['Pet'+species+'Paw'+side].rotation_quaternion=foot.inverted()
            for bone in arm.pose.bones:
                bone.keyframe_insert(data_path='location',frame=frame)
                bone.keyframe_insert(data_path='rotation_quaternion',frame=frame)
        track=arm.animation_data.nla_tracks.new();track.name=clip;track.strips.new(clip,0,action)
        arm.animation_data.action=None
    walk_reports={}
    for kind,axis,sign,stride_length,cycle in [('WalkForward','x',1,.30,.85),('WalkBackward','x',-1,.24,1.0),('StepLeft','z',-1,.18,.95),('StepRight','z',1,.18,.95),('Idle','x',0,0,2.8),('Play','x',0,0,2.4),('Sniff','x',0,0,3.2),('UrinateLeft','x',0,0,5.4),('UrinateRight','x',0,0,5.4)]:
        clip='Pet'+species+kind;action=bpy.data.actions.new(clip);arm.animation_data.action=action
        cycle_frames=round(cycle*fps);reach_max=0
        offsets=[0,.5,.25,.75]
        for frame in range(cycle_frames+1):
            t=frame/cycle_frames
            for bone in arm.pose.bones:bone.location=(0,0,0);bone.rotation_mode='QUATERNION';bone.rotation_quaternion=(1,0,0,0)
            bob=(.004*(1-math.cos(t*math.tau*2))) if sign else .0015*math.sin(t*math.tau)
            potty=kind.startswith('Urinate');envelope=smooth(t/.22)*(1-smooth((t-.76)/.24)) if potty else 0
            squat=.065*envelope if potty and species=='Cat' else 0
            sniff=.06*math.sin(t*math.pi)**2 if kind=='Sniff' else 0
            arm.pose.bones[rootbone].location=P((sign*stride_length*t if axis=='x' else 0,0,sign*stride_length*t if axis=='z' else 0))
            body=arm.pose.bones['Pet'+species+'Body'];body.location=P((0,bob-.009-squat-sniff*.3,0));body.rotation_quaternion=Q(z=(-.12*math.sin(t*math.pi)**2 if kind=='Play' and species=='Dog' else .015*math.sin(t*math.tau) if sign else 0),x=.012*math.sin(t*math.tau) if sign else 0)
            arm.pose.bones['Pet'+species+'Head'].rotation_quaternion=Q(z=-sniff*4-.012*math.sin(t*math.tau),y=(.3*envelope if potty and species=='Dog' else .025*math.sin(t*math.tau)))
            arm.pose.bones['Pet'+species+'Tail'].rotation_quaternion=Q(y=.07*math.sin(t*math.tau) if species=='Cat' else 0)
            for i,side in enumerate(['FL','FR','BL','BR']):
                phase=(t+offsets[i])%1;duty=.68
                if phase<duty:delta=stride_length*(duty/2-phase);lift=0
                else:
                    swing=(phase-duty)/(1-duty);delta=stride_length*duty*(smooth(swing)-.5);lift=(.021 if species=='Cat' else .026)*math.sin(math.pi*swing)
                if kind=='Play' and species=='Cat' and side=='FR':lift+=.05*max(0,math.sin(t*math.tau))
                leg_side=-1 if kind=='UrinateLeft' else 1
                raised=potty and species=='Dog' and side==('BL' if leg_side==-1 else 'BR')
                if raised:lift+=.12*envelope
                dx=sign*delta if axis=='x' else 0;dz=(leg_side*.10*envelope if raised else sign*delta if axis=='z' else 0)
                hip_height=(.283 if side[0]=='F' else .303)+bob-squat*(1 if side[0]=='B' else .65)-sniff*(1 if side[0]=='F' else .15)
                dy=.027+lift-hip_height
                lower=.13 if side[0]=='F' else .14;ax,ay=(.008,.028) if side[0]=='F' else (.03,.045)
                dx-=ax;dy+=ay
                reach=math.sqrt(dx*dx+dy*dy+dz*dz);reach_max=max(reach_max,reach)
                knee=(1 if side[0]=='F' else -1)*math.acos(max(-1,min(1,(reach*reach-.13**2-lower**2)/(2*.13*lower))))
                hip=math.atan2(dx,math.hypot(dy,dz))-math.atan2(lower*math.sin(knee),.13+lower*math.cos(knee));hipx=math.atan2(-dz,-dy)
                b=arm.pose.bones['Pet'+species+'Hip'+side];b.location=P((0,hip_height-(.29 if side[0]=='F' else .31),0));b.rotation_quaternion=Q(hipx,0,hip)
                arm.pose.bones['Pet'+species+'Knee'+side].rotation_quaternion=Q(z=knee)
                foot=Q(z=math.atan2(ax,ay))
                arm.pose.bones['Pet'+species+'Hock'+side].rotation_quaternion=(Q(hipx,0,hip)@Q(z=knee)).inverted()@foot
                toe=.16*math.sin(math.pi*(phase-duty)/(1-duty)) if sign and phase>duty else 0
                arm.pose.bones['Pet'+species+'Paw'+side].rotation_quaternion=foot.inverted()@Q(z=toe)
            for bone in arm.pose.bones:
                bone.keyframe_insert(data_path='location',frame=frame);bone.keyframe_insert(data_path='rotation_quaternion',frame=frame)
        track=arm.animation_data.nla_tracks.new();track.name=clip;track.strips.new(clip,0,action);arm.animation_data.action=None
        walk_reports[kind]={'stride':stride_length,'duration':cycle_frames/fps,'max_paw_reach':reach_max,'stance_fraction':.68}
        assert reach_max<.27,walk_reports[kind]
    for bone in arm.pose.bones:bone.location=(0,0,0);bone.rotation_quaternion=(1,0,0,0)
    report[species]={'bones':len(arm.pose.bones),'max_paw_reach':max_reach,'leg_lengths':{'fore':[.13,.13,math.hypot(.008,.028)],'hind':[.13,.14,math.hypot(.03,.045)]},'duration':duration,'clips':['TurnLeft','TurnRight'],'steps_per_quarter_turn':12}
    report[species]['locomotion']=walk_reports;arm['locomotion']=walk_reports
    assert max_reach<.27,report[species]
    # Bind the continuous skin in a natural, bent standing pose. Baking this
    # neutral shape with volume preservation avoids a straight-tube bind that
    # collapses at the stifle/elbow. Runtime clips still use standard glTF LBS.
    tracks=list(arm.animation_data.nla_tracks)
    for track in tracks:track.mute=True
    records=[]
    for track in tracks:
        action=track.strips[0].action;arm.animation_data.action=action
        frames=[]
        for frame in range(round(action.frame_range[1])+1):
            bpy.context.scene.frame_set(frame)
            frames.append({bone.name:bone.matrix.copy() for bone in arm.pose.bones})
        records.append((track.name,frames))
    idle=next(track.strips[0].action for track in tracks if track.name=='Pet'+species+'Idle')
    arm.animation_data.action=idle;bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
    modifier.use_deform_preserve_volume=True
    bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);bpy.context.view_layer.objects.active=skin
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    skin.select_set(False);arm.select_set(True);bpy.context.view_layer.objects.active=arm
    bpy.ops.object.mode_set(mode='POSE');bpy.ops.pose.armature_apply(selected=False);bpy.ops.object.mode_set(mode='OBJECT')
    arm.animation_data.action=None
    for track in tracks:
        track.strips[0].action.name='Previous '+track.name
        arm.animation_data.nla_tracks.remove(track)
    modifier=skin.modifiers.new('Native joint deformation','ARMATURE');modifier.object=arm
    for name,frames in records:
        action=bpy.data.actions.new(name);arm.animation_data.action=action
        for frame,matrices in enumerate(frames):
            for bone in arm.pose.bones:
                options={'parent_matrix':matrices[bone.parent.name],'parent_matrix_local':bone.parent.bone.matrix_local} if bone.parent else {}
                basis=bone.bone.convert_local_to_pose(matrices[bone.name],bone.bone.matrix_local,invert=True,**options)
                bone.location,bone.rotation_quaternion,bone.scale=basis.decompose()
                bone.keyframe_insert(data_path='location',frame=frame);bone.keyframe_insert(data_path='rotation_quaternion',frame=frame)
        track=arm.animation_data.nla_tracks.new();track.name=name;track.strips.new(name,0,action);arm.animation_data.action=None
bpy.context.scene.render.fps=30;bpy.context.scene.frame_start=0;bpy.context.scene.frame_end=72;bpy.context.scene.frame_set(0)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'garden-life-rig-v5.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'garden-life-rig-v5-raw.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_animations=True,export_animation_mode='NLA_TRACKS',export_extras=True,export_force_sampling=True)
(OUT/'garden-life-rig-v5.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
