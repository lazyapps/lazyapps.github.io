"""Native IK turn/plant corrections for the selected private professional pets.

Extends the saved trial, retaining source meshes, baked UV materials and groom.
No new animal is modeled. Usage: Blender --disable-autoexec --python ... -- dog|cat
"""
from pathlib import Path
import sys,math,json
import bpy,numpy as np
from mathutils import Vector,Matrix
from mathutils.kdtree import KDTree
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scripts/assets/fondfont/pets/trial'
kind=sys.argv[sys.argv.index('--')+1];dog=kind=='dog';scale=1.65
bpy.ops.wm.open_mainfile(filepath=str(OUT/(kind+'-trial.blend')),use_scripts=False)
scene=bpy.context.scene;scene.frame_set(1)
rig=bpy.data.objects['RIG-autumn' if dog else 'Armature.001']
root=bpy.data.objects['PetDog' if dog else 'PetCat']
source_names=['GEO_autumn_body','GEO_autumn_eye.l','GEO_autumn_eye.r','GEO_autumn_scarf','GEO_autumn_scarf.endpiece','GEO_autumn_teeth.lower','GEO_autumn_teeth.upper','GEO_autumn_tongue'] if dog else ['sculpt.001','Eye1']
sources=[bpy.data.objects[n] for n in source_names]
exports=[bpy.data.objects['Studio'+kind.title()+'-'+n] for n in source_names]
fur=bpy.data.objects['Studio'+kind.title()+'-original-groom']
limbs=[('hand_sole_ctrl_L','hand_def_L',0),('hand_sole_ctrl_R','hand_def_R',.5),('sole_ctrl_L','foot_def_L',.75),('sole_ctrl_R','foot_def_R',.25)] if dog else [('paw_control_L','paw3_L',0),('paw_control_R','paw3_R',.5),('leg3_control_L','feet_L',.75),('leg3_control_R','feet_R',.25)]
bpy.context.view_layer.update();depsgraph=bpy.context.evaluated_depsgraph_get()
def coords(o):
 e=o.evaluated_get(depsgraph);m=e.to_mesh(preserve_all_data_layers=True,depsgraph=depsgraph)
 a=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',a);a=a.reshape((-1,3));w=np.array(o.matrix_world,dtype=np.float32);a=a@w[:3,:3].T+w[:3,3];e.to_mesh_clear();return a
def key_coords(o):
 a=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.shape_keys.key_blocks['Basis'].data.foreach_get('co',a);return a.reshape((-1,3))
old_body=key_coords(exports[0]);old_fur=key_coords(fur)
tree=KDTree(len(old_body))
for i,p in enumerate(old_body):tree.insert(Vector(p),i)
tree.balance();attachments=[]
for start in range(0,len(old_fur),9):
 _,i,_=tree.find(Vector(np.mean(old_fur[start:start+3],axis=0)));attachments.extend([i]*9)
attachments=np.array(attachments,dtype=np.int32)
# The downloaded cat was posed for a still: put all four native paw controls at rest.
if not dog:
 for name,_,_ in limbs:rig.pose.bones[name].matrix_basis=Matrix.Identity(4)
 bpy.context.view_layer.update()
base={name:rig.pose.bones[name].matrix.copy() for name,_,_ in limbs}
feet={name:rig.pose.bones[foot].matrix.translation.copy() for name,foot,_ in limbs}
tail=rig.pose.bones['tail_ctrl' if dog else 'tail1'];tail_base=tail.matrix.copy()
head=rig.pose.bones['head_ik_ctrl' if dog else 'Bone.004'];head_base=head.matrix.copy()
rest_body=coords(sources[0]);fur_rest=old_fur+(rest_body-old_body)[attachments]
stride=.10 if dog else .11;stance=.65;angle=math.pi/3;eps=.025;yaw_eps=.12;head_angle=.32
phases=sorted({round(i/16,8) for i in range(16)}|{round((stance-offset)%1,8) for _,_,offset in limbs})
def rotate_at(matrix,origin,theta):return Matrix.Translation(origin)@Matrix.Rotation(theta,4,'Z')@Matrix.Translation(-origin)@matrix
def reset():
 for name,_,_ in limbs:rig.pose.bones[name].matrix=base[name].copy()
 tail.matrix=tail_base.copy();head.matrix=head_base.copy();bpy.context.view_layer.update()
def solve(name,foot,target,rotation=0):
 control=rig.pose.bones[name]
 if rotation:control.matrix=rotate_at(base[name],feet[name],rotation);bpy.context.view_layer.update()
 for _ in range(8):
  delta=target-rig.pose.bones[foot].matrix.translation
  if delta.length<.00001:break
  m=control.matrix.copy();m.translation+=delta;control.matrix=m;bpy.context.view_layer.update()
def gait(phase,turn=0):
 reset()
 for name,foot,offset in limbs:
  q=(phase+offset)%1
  if q<stance:
   travel=q/stance-.5;lift=0;theta=-turn*angle*(q-stance/2)
  else:
   t=(q-stance)/(1-stance);smooth=t*t*(3-2*t)
   travel=.5-smooth;lift=(.022 if dog else .015)*math.sin(math.pi*t)**1.5
   # Cubic Hermite arc preserves the paw's angular velocity at lift/landing.
   h00=2*t**3-3*t*t+1;h10=t**3-2*t*t+t;h01=-2*t**3+3*t*t;h11=t**3-t*t
   theta=turn*angle*(-stance/2*h00-(1-stance)*h10+stance/2*h01-(1-stance)*h11)
  target=feet[name].copy()
  if turn:target=Matrix.Rotation(theta,3,'Z')@target
  else:target.y+=stride*travel
  target.z+=lift;solve(name,foot,target,theta if turn else 0)
all_exports=exports+[fur]
for o in all_exports:
 for key in list(o.data.shape_keys.key_blocks)[1:]:o.shape_key_remove(key)
rest=[coords(o) for o in sources]+[fur_rest]
for o,a in zip(all_exports,rest):
 o.data.vertices.foreach_set('co',a.reshape(-1));o.data.shape_keys.key_blocks['Basis'].data.foreach_set('co',a.reshape(-1))
contact_error=0
baked={}
def capture(name):
 values=[coords(o) for o in sources];values.append(fur_rest+(values[0]-rest_body)[attachments])
 for o,a in zip(all_exports,values):o.shape_key_add(name=name).data.foreach_set('co',a.reshape(-1))
 baked[name]=values[0]
 print('Native pose',kind,name,flush=True)
for bank,turn in [('Walk',0),('TurnLeft',1),('TurnRight',-1)]:
 for i,p in enumerate(phases):
  gait(p,turn);capture(bank+str(i).zfill(2))
  for name,foot,offset in limbs:
   if (p+offset)%1<stance:
    contact_error=max(contact_error,abs(rig.pose.bones[foot].matrix.translation.z-feet[name].z))
for name,w in [('WagLeft',-.4),('WagRight',.4)]:reset();tail.matrix=rotate_at(tail_base,tail_base.translation,w);bpy.context.view_layer.update();capture(name)
for name,w in [('HeadLeft',head_angle),('HeadRight',-head_angle)]:reset();head.matrix=rotate_at(head_base,head_base.translation,w);bpy.context.view_layer.update();capture(name)
for i,(name,foot,offset) in enumerate(limbs):
 for axis in range(3):
  reset();target=feet[name].copy();target[axis]+=eps;solve(name,foot,target);capture('Plant'+str(i)+'XYZ'[axis])
 reset();solve(name,foot,feet[name],yaw_eps);capture('Plant'+str(i)+'Yaw')
reset()
def web(p):return [-float(p[1])*scale,float(p[2])*scale,-float(p[0])*scale]
markers=[]
for i,(name,foot,offset) in enumerate(limbs):
 p=np.array(feet[name]);dist=np.linalg.norm(rest_body[:,:2]-p[:2],axis=1)
 patch=np.where(dist<.055)[0];floor=float(rest_body[patch,2].min());patch=patch[rest_body[patch,2]<floor+.0025]
 # Three noncollinear sole points: toe, heel and a lateral point, from actual skin.
 targets=[p+np.array([0,-.017,0]),p+np.array([0,.014,0]),p+np.array([.012,0,0])]
 indices=[int(min(patch,key=lambda j:np.linalg.norm(rest_body[j,:2]-v[:2]))) for v in targets]
 assert len(set(indices))==3,(kind,name,indices)
 markers.append({'offset':offset,'markers':[web(rest_body[j]) for j in indices],'source_vertices':indices,'correction':['Plant'+str(i)+a for a in ['X','Y','Z','Yaw']]})
metadata=dict(root['studio_pet']);metadata.update({'version':2,'walk_poses':len(phases),'phases':phases,'stance':stance,'turn_angle':angle,'head_angle':head_angle,'feet':markers,'native_paw_contact_error_max':contact_error,'animation':'Native IK walk and pivot poses plus world-plant corrections; original groom retained'})
root['studio_pet']=metadata
for o in all_exports:
 for k in o.data.shape_keys.key_blocks:k.value=0
bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for o in all_exports:o.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(kind+'-turn-v2.blend')))
bpy.ops.export_scene.gltf(filepath=str(OUT/(kind+'-turn-v2-raw.glb')),export_format='GLB',use_selection=True,export_apply=False,export_cameras=False,export_lights=False,export_animations=False,export_extras=True,export_image_format='WEBP',export_image_quality=90,export_morph=True,export_morph_normal=False,export_morph_tangent=False)
(OUT/(kind+'-turn-v2.json')).write_text(json.dumps(metadata,indent=2))
print('TURN TRIAL COMPLETE',kind,'poses',len(baked),'error',contact_error,flush=True)
