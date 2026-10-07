import * as THREE from 'three';
import type { sampleGardenLife } from './garden-life.mjs';

type Pose = ReturnType<typeof sampleGardenLife>['dog'];
type FootSpec = { offset:number; markers:number[][]; correction:string[] };
type Specs = { body_mesh?:string; stride:number; phases:number[]; stance:number; turn_angle:number; head_angle:number; feet:FootSpec[] };
const wrap = (angle:number) => Math.atan2(Math.sin(angle),Math.cos(angle));
const yawOf = (v:THREE.Vector3) => Math.atan2(-v.z,v.x);
const ease = (t:number) => t*t*t*(10+t*(-15+6*t));

function inverseMatrix(matrix:number[][]) {
  const n=matrix.length,a=matrix.map((row,i)=>[...row,...Array.from({length:n},(_,j)=>i===j?1:0)]);
  for(let i=0;i<n;i++){
    let pivot=i;for(let j=i+1;j<n;j++)if(Math.abs(a[j][i])>Math.abs(a[pivot][i]))pivot=j;
    [a[i],a[pivot]]=[a[pivot],a[i]];
    if(Math.abs(a[i][i])<1e-12)throw new Error('Native paw pose basis is singular');
    const d=a[i][i];for(let k=0;k<2*n;k++)a[i][k]/=d;
    for(let j=0;j<n;j++)if(j!==i){const f=a[j][i];for(let k=0;k<2*n;k++)a[j][k]-=f*a[i][k];}
  }
  return a.map(row=>row.slice(n));
}

/** Evaluated native poses plus world-space sole planting, without root body tilt. */
export function createStudioLocomotion(root:THREE.Object3D) {
  const specs=root.userData.studio_pet as Specs;
  const meshes:THREE.Mesh[]=[];
  root.traverse(o=>{if(o instanceof THREE.Mesh&&o.morphTargetInfluences)meshes.push(o);});
  const body=meshes.find(m=>specs.body_mesh?m.name===specs.body_mesh:/GEO_autumn_body$/.test(m.name))!;
  root.updateWorldMatrix(true,true);
  const meshToRoot=new THREE.Matrix4().multiplyMatrices(root.matrixWorld.clone().invert(),body.matrixWorld);
  const linear=new THREE.Matrix3().setFromMatrix4(meshToRoot);
  const position=body.geometry.getAttribute('position');
  const point=new THREE.Vector3();
  const basePoint=(index:number)=>new THREE.Vector3().fromBufferAttribute(position,index).applyMatrix4(meshToRoot);
  function delta(name:string,index:number) {
    const attribute=body.geometry.morphAttributes.position[body.morphTargetDictionary![name]];
    const p=new THREE.Vector3().fromBufferAttribute(attribute,index);
    if(!body.geometry.morphTargetsRelative)p.sub(new THREE.Vector3().fromBufferAttribute(position,index));
    return p.applyMatrix3(linear);
  }
  const feet=specs.feet.map(spec=>{
    const indices=spec.markers.map(marker=>{
      const target=new THREE.Vector3(...marker as [number,number,number]);let best=0,distance=Infinity;
      for(let i=0;i<position.count;i++){point.copy(basePoint(i));const d=point.distanceToSquared(target);if(d<distance){distance=d;best=i;}}
      return best;
    });
    const columns=spec.correction.map(name=>indices.flatMap(i=>delta(name,i).toArray()));
    const dot=(a:number[],b:number[])=>a.reduce((sum,v,i)=>sum+v*b[i],0);
    const inverse=inverseMatrix(columns.map(a=>columns.map(b=>dot(a,b))));
    const basePoints=indices.map(basePoint),baseCenter=basePoints.reduce((v,p)=>v.add(p),new THREE.Vector3()).divideScalar(3);
    return {spec,indices,columns,inverse,baseCenter,basePoints,planted:true,anchor:new THREE.Vector3(),anchors:[] as THREE.Vector3[],applied:spec.correction.map(()=>0),lastSlip:0,lastReach:0,
      world:[] as THREE.Vector3[],takeoff:new THREE.Vector3(),landing:new THREE.Vector3(),takeoffYaw:0,landingYaw:0,flight:0,duration:0,stanceTime:0};
  });
  let previous=-1,previousX=0,previousZ=0,previousYaw=0,phase=0,gaze=0;
  const blend={walk:0,left:0,right:0};
  const localPoint=(index:number)=>body.getVertexPosition(index,new THREE.Vector3()).applyMatrix4(meshToRoot);
  const footPoints=(foot:typeof feet[number])=>foot.indices.map(localPoint);
  const center=(points:THREE.Vector3[])=>points.reduce((v,p)=>v.add(p),new THREE.Vector3()).divideScalar(points.length);
  function weight(name:string,value:number) {
    for(const mesh of meshes){const index=mesh.morphTargetDictionary![name];if(index!==undefined)mesh.morphTargetInfluences![index]=value;}
  }
  function sample(bank:string,value:number) {
    if(value===0)return;
    let next=specs.phases.findIndex(p=>p>phase);if(next<0)next=0;
    const first=(next+specs.phases.length-1)%specs.phases.length;
    const start=specs.phases[first],end=next===0?1:specs.phases[next];
    const t=(phase-start)/(end-start);
    weight(bank+String(first).padStart(2,'0'),value*(1-t));weight(bank+String(next).padStart(2,'0'),value*t);
  }
  return {
    update(pose:Pose,seconds:number,index:number) {
      const reset=previous<0||seconds<previous||seconds-previous>.25;
      const dt=reset?0:Math.min(.1,seconds-previous);
      const dx=reset?0:pose.x-previousX,dz=reset?0:pose.z-previousZ,dyaw=reset?0:wrap(pose.yaw-previousYaw);
      const distance=Math.hypot(dx,dz),angle=Math.abs(dyaw);
      // Navigation only travels forward; both accepted movement terms advance the gait.
      const walkPhase=distance/specs.stride,turnPhase=angle/specs.turn_angle;
      const moving=dt>0&&(distance/dt>.006||angle/dt>.035);
      if(reset){phase=0;feet.forEach(f=>{f.planted=false;f.applied.fill(0);});blend.walk=blend.left=blend.right=0;}
      if(moving)phase=THREE.MathUtils.euclideanModulo(phase+walkPhase+turnPhase,1);
      const rate=dt?(walkPhase+turnPhase)/dt:0;
      const activity=moving?THREE.MathUtils.smoothstep(rate,.025,.22):0;
      const turnRatio=turnPhase/(walkPhase+turnPhase||1),smooth=reset?1:1-Math.exp(-dt/.09);
      blend.walk=THREE.MathUtils.lerp(blend.walk,activity*(1-turnRatio),smooth);
      blend.left=THREE.MathUtils.lerp(blend.left,dyaw>=0?activity*turnRatio:0,smooth);
      blend.right=THREE.MathUtils.lerp(blend.right,dyaw<0?activity*turnRatio:0,smooth);
      root.position.set(pose.x,0,pose.z);root.rotation.y=pose.yaw;
      meshes.forEach(m=>m.morphTargetInfluences!.fill(0));
      sample('Walk',blend.walk);sample('TurnLeft',blend.left);sample('TurnRight',blend.right);
      gaze=THREE.MathUtils.lerp(gaze,THREE.MathUtils.clamp(pose.look,-specs.head_angle,specs.head_angle),reset?1:1-Math.exp(-dt/.12));
      weight(gaze<0?'HeadRight':'HeadLeft',Math.abs(gaze)/specs.head_angle);
      const wag=Math.sin(seconds*(index?1.7:1.45)+index*.9)*.25;
      weight(wag<0?'WagLeft':'WagRight',Math.abs(wag));
      root.updateWorldMatrix(true,true);
      const inverseRoot=root.matrixWorld.clone().invert();
      let supports=feet.filter(f=>f.planted).length;
      for(const foot of feet){
        const q=THREE.MathUtils.euclideanModulo(phase+foot.spec.offset,1);
        const raw=footPoints(foot),worldRaw=raw.map(p=>p.clone().applyMatrix4(root.matrixWorld));
        if(reset){foot.world=worldRaw.map(p=>p.clone());foot.anchors=worldRaw.map(p=>p.clone());foot.anchor.copy(center(worldRaw));foot.planted=true;foot.stanceTime=0;}
        foot.stanceTime+=dt;
        if(foot.planted&&moving&&supports>1&&((supports>2&&q>specs.stance)||foot.anchor.distanceTo(center(worldRaw))>.18)&&foot.stanceTime>.12){
          supports--;
          foot.planted=false;foot.flight=0;
          foot.takeoff.copy(center(foot.world));foot.takeoffYaw=yawOf(foot.world[0].clone().sub(foot.world[1]));
          foot.duration=THREE.MathUtils.clamp((1-specs.stance)/Math.max(rate,.25),.42,.5);
          const futureYaw=pose.yaw+(dt?dyaw/dt:0)*foot.duration*.5;
          // Anticipate a native touchdown, including the root's accepted arc.
          const localLanding=foot.baseCenter.clone();localLanding.x+=specs.stride*.12;
          const futureRoot=new THREE.Matrix4().compose(new THREE.Vector3(pose.x+(dt?dx/dt:0)*foot.duration*.5,0,pose.z+(dt?dz/dt:0)*foot.duration*.5),new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),futureYaw),root.scale);
          foot.landing.copy(localLanding.applyMatrix4(futureRoot));foot.landing.y=foot.baseCenter.y*root.scale.y;
          const step=foot.landing.clone().sub(foot.takeoff);step.y=0;
          if(step.length()>.30){step.setLength(.30);foot.landing.x=foot.takeoff.x+step.x;foot.landing.z=foot.takeoff.z+step.z;}
          foot.landingYaw=futureYaw+yawOf(foot.basePoints[0].clone().sub(foot.basePoints[1]));
        }
        let desired:THREE.Vector3[];
        if(foot.planted)desired=foot.anchors;
        else{
          foot.flight+=dt;
          const t=Math.min(1,foot.flight/foot.duration),u=ease(t);
          const position=foot.takeoff.clone().lerp(foot.landing,u);
          position.y+=.035*Math.sin(Math.PI*t)**2;
          const yaw=foot.takeoffYaw+wrap(foot.landingYaw-foot.takeoffYaw)*u;
          const baseYaw=yawOf(foot.basePoints[0].clone().sub(foot.basePoints[1]));
          desired=foot.basePoints.map(p=>p.clone().sub(foot.baseCenter).applyAxisAngle(new THREE.Vector3(0,1,0),yaw-baseYaw).multiply(root.scale).add(position));
          if(t===1){supports++;foot.planted=true;foot.stanceTime=0;foot.anchors=desired.map(p=>p.clone());foot.anchor.copy(position);}
        }
        // Fit all decoded sole markers with finite native yaw poses, not an
        // infinitesimal heading correction that lengthens the paw on reversals.
        const target=desired.flatMap((p,i)=>p.clone().applyMatrix4(inverseRoot).sub(raw[i]).toArray());
        const rhs=foot.columns.map(c=>c.reduce((sum,v,i)=>sum+v*target[i],0));
        foot.applied=foot.inverse.map(row=>row.reduce((sum,v,i)=>sum+v*rhs[i],0));
        foot.spec.correction.forEach((name,i)=>weight(name,foot.applied[i]));
        foot.world=footPoints(foot).map(p=>p.applyMatrix4(root.matrixWorld));
        foot.lastReach=center(worldRaw).distanceTo(center(foot.world));
        foot.lastSlip=foot.planted?Math.max(...foot.world.map((p,i)=>p.distanceTo(foot.anchors[i]))):0;
      }
      previous=seconds;previousX=pose.x;previousZ=pose.z;previousYaw=pose.yaw;
    },
    diagnostics(){return {phase,feet:feet.map(f=>({planted:f.planted,slip:f.lastSlip,reach:f.lastReach,soleLengths:[f.world[0].distanceTo(f.world[1]),f.world[0].distanceTo(f.world[2]),f.world[1].distanceTo(f.world[2])],restLengths:[f.basePoints[0].distanceTo(f.basePoints[1]),f.basePoints[0].distanceTo(f.basePoints[2]),f.basePoints[1].distanceTo(f.basePoints[2])].map(v=>v*root.scale.x),points:footPoints(f).map(p=>p.applyMatrix4(root.matrixWorld).toArray()),anchors:f.anchors.map(p=>p.toArray()),corrections:[...f.applied]}))};},
  };
}
