import * as THREE from 'three';
import type { sampleGardenLife } from './garden-life.mjs';
type Life=ReturnType<typeof sampleGardenLife>;
export function createPetAnimator(model:THREE.Object3D,clips:THREE.AnimationClip[]){
  const mixer=new THREE.AnimationMixer(model);
  const actions=new Map(clips.map(clip=>{
    // Navigation owns root motion; Blender owns the articulated body.
    const local=new THREE.AnimationClip(clip.name,clip.duration,clip.tracks.filter(t=>!/^Pet(Dog|Cat)Root\./.test(t.name)));
    const action=mixer.clipAction(local);action.play();action.setEffectiveWeight(0);return[clip.name,action] as const;
  }));
  const make=()=>({yaw:0,sign:0,progress:{left:0,right:0},active:false,rest:'Idle',restStart:0,weights:new Map<string,number>([['Idle',1]])});
  const states={Dog:make(),Cat:make()},overlayBases=new Map<string,THREE.Quaternion>();
  const tailBones=['PetDogTail','PetDogTailMid','PetDogTailTip'].map(name=>model.getObjectByName(name)!);
  const wag={phase:0,amplitude:.3,rate:1.4};
  const up=new THREE.Vector3(),parentRotation=new THREE.Quaternion(),rotation=new THREE.Quaternion();
  let lastTime=-1;
  function pet(species:'Dog'|'Cat',pose:Life['dog'],seconds:number){
    const root=model.getObjectByName('Pet'+species)!;root.position.set(pose.x,0,pose.z);root.rotation.y=pose.yaw;
    const state=states[species],desired=new Map<string,number>();
    const time=(kind:string,value:number)=>{const action=actions.get('Pet'+species+kind)!;action.time=value%action.getClip().duration;};
    const c=Math.cos(pose.yaw),s=Math.sin(pose.yaw),forward=c*pose.vx-s*pose.vz,side=s*pose.vx+c*pose.vz;
    const walking=THREE.MathUtils.smoothstep(pose.speed,.015,.12);
    const pivot=(1-walking)*THREE.MathUtils.smoothstep(Math.abs(pose.turn),.08,.5),sign=Math.sign(pose.turn),active=pivot>.05;
    if(active){
      const direction=sign>=0?'left':'right';
      if(seconds<lastTime)state.progress={left:0,right:0};
      if(state.active&&sign===state.sign)state.progress[direction]+=Math.abs(Math.atan2(Math.sin(pose.yaw-state.yaw),Math.cos(pose.yaw-state.yaw)));
      const kind=sign>=0?'TurnLeft':'TurnRight',action=actions.get('Pet'+species+kind)!;
      time(kind,((state.progress[direction]/(Math.PI/2))%1)*action.getClip().duration);
    }
    state.yaw=pose.yaw;state.sign=sign;state.active=active;
    desired.set(sign>=0?'TurnLeft':'TurnRight',pivot);
    const total=Math.abs(forward)+Math.abs(side)||1,specs=root.userData.locomotion;
    for(const kind of ['WalkForward','WalkBackward','StepLeft','StepRight']){
      const action=actions.get('Pet'+species+kind)!;time(kind,pose.distance/specs[kind].stride*action.getClip().duration);
    }
    desired.set(forward>=0?'WalkForward':'WalkBackward',walking*Math.abs(forward)/total);
    desired.set(side>=0?'StepRight':'StepLeft',walking*Math.abs(side)/total);
    const rest=pose.mood==='potty'?(pose.pottySide<0?'UrinateLeft':'UrinateRight'):pose.mood==='play'?'Play':pose.mood==='sniff'?'Sniff':'Idle';
    if(state.rest!==rest||seconds<lastTime){state.rest=rest;state.restStart=seconds;}
    time(rest,pose.mood==='potty'?Math.min(pose.actionTime,5.399):seconds-state.restStart);
    desired.set(rest,1-walking-pivot);
    const blend=lastTime<0||seconds<lastTime?1:1-Math.exp(-Math.min(.1,seconds-lastTime)/.18);
    for(const [name,action] of actions)if(name.startsWith('Pet'+species)){
      const kind=name.slice(('Pet'+species).length),old=state.weights.get(kind)??0;
      const weight=THREE.MathUtils.lerp(old,desired.get(kind)??0,blend);state.weights.set(kind,weight);action.setEffectiveWeight(weight);
    }
  }
  return {
    update(life:Life,seconds:number){
      // Restore the animated base before adding the current gaze; cached mixer poses
      // do not overwrite an unchanged value, so incremental overlays would accumulate.
      for(const [name,base] of overlayBases)model.getObjectByName(name)!.quaternion.copy(base);
      const dt=lastTime<0||seconds<lastTime?0:Math.min(.1,seconds-lastTime);
      pet('Dog',life.dog,seconds);pet('Cat',life.cat,seconds);mixer.update(0);
      for(const bone of tailBones)overlayBases.set(bone.name,bone.quaternion.clone());
      for(const [species,pose] of [['Dog',life.dog],['Cat',life.cat]] as const){
        const head=model.getObjectByName('Pet'+species+'Head')!;overlayBases.set(head.name,head.quaternion.clone());head.rotateZ(pose.look);
      }
      const mood=life.dog.mood,amplitude=mood==='play'?.46:mood==='potty'?.08:mood==='sniff'?.22:.34;
      const rate=mood==='play'?2.1:mood==='potty'?.7:1.4,blend=dt?1-Math.exp(-dt/.35):1;
      wag.amplitude=THREE.MathUtils.lerp(wag.amplitude,amplitude,blend);wag.rate=THREE.MathUtils.lerp(wag.rate,rate,blend);
      wag.phase=dt?wag.phase+dt*wag.rate*Math.PI*2:seconds*1.4*Math.PI*2;
      model.updateMatrixWorld(true);
      tailBones.forEach((bone,i)=>{
        up.set(0,1,0).applyQuaternion(bone.parent!.getWorldQuaternion(parentRotation).invert());
        const angle=wag.amplitude*[1,.58,.36][i]*Math.sin(wag.phase-i*.48);
        bone.quaternion.premultiply(rotation.setFromAxisAngle(up,angle));
        bone.updateWorldMatrix(false,true);
      });
      lastTime=seconds;
    },
    dispose(){mixer.stopAllAction();mixer.uncacheRoot(model);},
  };
}
