// Retired native rig (not shipped since 2026-10-08); the GLB is kept locally under scripts/assets.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {createGardenLife} from '../src/lib/fondfont/garden-life.mjs';
import {createPetAnimator} from '../src/lib/fondfont/pet-animation.ts';
const bytes=readFileSync(new URL('./assets/fondfont/blender-v2/retired-public/garden-life-rig-v6.glb',import.meta.url));
const gltf=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)));
assert.equal(gltf.skins.length,3,'both pets plus the separate imagegen head retain real skins');
assert.equal(new Set(gltf.skins.flatMap(s=>s.joints)).size,42,'both pets retain wrist/hock joints');
assert.equal(gltf.animations.length,22,'eleven native Blender clips per pet');
assert.ok(bytes.length<3.2*1024*1024,'rigged pets and embedded imagegen face stay below 3.2 MiB');
assert.ok(gltf.meshes.some(m=>m.primitives.some(p=>p.attributes.COLOR_0!==undefined)),'native coat paint survives as vertex colors');
assert.ok(gltf.materials.some(m=>m.name==='Imagegen puppy face original v6'&&m.pbrMetallicRoughness?.baseColorTexture),'actual imagegen face is embedded on the rigged head');
// Verify skinned geometry headlessly; actual image decoding is checked in browser.
const jsonLength=bytes.readUInt32LE(12);
const geometryJson=structuredClone(gltf);geometryJson.materials=geometryJson.materials.map(m=>({name:m.name}));
const geometryText=JSON.stringify(geometryJson);const json=Buffer.from(geometryText.padEnd(Math.ceil(geometryText.length/4)*4,' '));
const geometryBytes=Buffer.concat([bytes.subarray(0,20),json,bytes.subarray(20+jsonLength)]);geometryBytes.writeUInt32LE(geometryBytes.length,8);geometryBytes.writeUInt32LE(json.length,12);
const rig=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(geometryBytes.buffer.slice(geometryBytes.byteOffset,geometryBytes.byteOffset+geometryBytes.byteLength),'');
const tailVertices=[];
rig.scene.getObjectByName('PetDog').traverse(mesh=>{
 if(!mesh.isSkinnedMesh)return;
 const tipIndex=mesh.skeleton.bones.findIndex(b=>b.name==='PetDogTailTip');
 assert.ok(tipIndex>=0,'dog has a deforming tail tip bone');
 const indices=mesh.geometry.getAttribute('skinIndex'),weights=mesh.geometry.getAttribute('skinWeight');
 for(let i=0;i<indices.count;i++)for(let j=0;j<4;j++)if(indices.getComponent(i,j)===tipIndex&&weights.getComponent(i,j)>.8){tailVertices.push({mesh,index:i});break;}
});
assert.ok(tailVertices.length>20,'real tail geometry is weighted to its tip');
const idleLife=createGardenLife(47).sample(0);
for(const species of ['dog','cat'])Object.assign(idleLife[species],{x:0,z:0,yaw:0,speed:0,vx:0,vz:0,turn:0,look:0,mood:'watch',distance:0});
const tailAnimator=createPetAnimator(rig.scene,rig.animations),tailSamples=[];
for(let i=0;i<120;i++){
 tailAnimator.update(idleLife,i/60);rig.scene.updateMatrixWorld(true);
 for(const name of ['PetDogTail','PetDogTailMid','PetDogTailTip']){
  const scale=rig.scene.getObjectByName(name).getWorldScale(new THREE.Vector3());
  assert.ok(Math.max(scale.x,scale.y,scale.z)-Math.min(scale.x,scale.y,scale.z)<1e-5,'tail ancestry has uniform scale for world-up rotations');
 }
 const tip=new THREE.Vector3();for(const {mesh,index} of tailVertices)tip.add(mesh.getVertexPosition(index,new THREE.Vector3()).applyMatrix4(mesh.matrixWorld));tip.divideScalar(tailVertices.length);tailSamples.push(tip);
}
const wagRange=Math.max(...tailSamples.map(v=>v.z))-Math.min(...tailSamples.map(v=>v.z));
const verticalWag=Math.max(...tailSamples.map(v=>v.y))-Math.min(...tailSamples.map(v=>v.y));
assert.ok(wagRange>.12,'actual skinned dog tail has an unmistakable left/right sweep');
assert.ok(verticalWag<.015,'wag does not rotate the tail or body up/down');
tailAnimator.dispose();console.log({wagRange,verticalWag});
const pawPatches=new Map();
rig.scene.traverse(mesh=>{
  if(!mesh.isSkinnedMesh)return;
  const indices=mesh.geometry.getAttribute('skinIndex'),weights=mesh.geometry.getAttribute('skinWeight');
  for(const [boneIndex,bone] of mesh.skeleton.bones.entries())if(/Paw[FB][LR]$/.test(bone.name)){
    const vertices=[];
    for(let i=0;i<indices.count;i++)for(let j=0;j<4;j++)if(indices.getComponent(i,j)===boneIndex&&weights.getComponent(i,j)>.8){vertices.push(i);break;}
    if(vertices.length)pawPatches.set(bone.name,{mesh,vertices});
  }
});
let maxSlip=0,maxGroundError=0,minSole=Infinity,maxSoleGap=0;
for(const species of ['Dog','Cat']){
  const root=rig.scene.getObjectByName('Pet'+species),specs=root.userData.locomotion;
  for(const kind of ['WalkForward','WalkBackward','StepLeft','StepRight','TurnLeft','TurnRight']){
    const source=rig.animations.find(c=>c.name==='Pet'+species+kind);
    const clip=new THREE.AnimationClip(source.name,source.duration,source.tracks.filter(t=>!t.name.startsWith('Pet'+species+'Root.')));
    const mixer=new THREE.AnimationMixer(rig.scene),action=mixer.clipAction(clip);action.play();
    let previous;
    for(let n=0;n<=240;n++){
      const p=n/240;action.time=p*clip.duration;
      root.position.set(0,0,0);root.rotation.y=0;
      if(kind.startsWith('Turn'))root.rotation.y=(kind==='TurnLeft'?1:-1)*Math.PI/2*p;
      else root.position[kind.startsWith('Step')?'z':'x']=(kind==='WalkBackward'||kind==='StepLeft'?-1:1)*specs[kind].stride*p;
      mixer.update(0);rig.scene.updateMatrixWorld(true);
      const paws=['FL','FR','BL','BR'].map(s=>rig.scene.getObjectByName('Pet'+species+'Paw'+s).getWorldPosition(new THREE.Vector3()));
      for(const [i,paw] of paws.entries()){
        assert.ok(paw.toArray().every(Number.isFinite)&&paw.y>.025,`native paws remain above ground: ${species} ${kind} ${n} ${i} ${paw.y}`);
        maxGroundError=Math.max(maxGroundError,Math.max(0,.027-paw.y));
        if(previous&&paw.y<.0272&&previous[i].y<.0272)maxSlip=Math.max(maxSlip,paw.distanceTo(previous[i]));
        if(n%12===0&&paw.y<.0275){
          const patch=pawPatches.get('Pet'+species+'Paw'+['FL','FR','BL','BR'][i]);
          assert.ok(patch,'native skin includes weighted paw surface vertices');
          let sole=Infinity;
          for(const index of patch.vertices){const v=patch.mesh.getVertexPosition(index,new THREE.Vector3()).applyMatrix4(patch.mesh.matrixWorld);sole=Math.min(sole,v.y);}
          minSole=Math.min(minSole,sole);maxSoleGap=Math.max(maxSoleGap,sole);
        }
      }
      previous=paws;
    }
    mixer.stopAllAction();mixer.uncacheRoot(rig.scene);
  }
}
assert.ok(maxSlip<.002,'supporting paws remain planted during exported walking and turning');
console.log({minSole,maxSoleGap});
assert.ok(minSole>-.004&&maxSoleGap<.012,'actual skinned supporting paw surfaces contact the ground without visible penetration or floating');
let maxTransition=0,minUp=1,worst;
for(const seed of [47,11,991,2]){
  const animator=createPetAnimator(rig.scene,rig.animations),life=createGardenLife(seed);let last={},oldState;
  for(let t=0;t<(seed===2?600:300);t+=1/60){
    const state=life.sample(t);animator.update(state,t);rig.scene.updateMatrixWorld(true);
    for(const species of ['Dog','Cat']){
      const body=rig.scene.getObjectByName('Pet'+species+'Body');
      const up=new THREE.Vector3(0,0,1).applyQuaternion(body.getWorldQuaternion(new THREE.Quaternion())).y;
      minUp=Math.min(minUp,up);assert.ok(up>.94,'native bodies stay upright through repeated idle/walk/turn overlays');
      for(const side of ['FL','FR','BL','BR']){
        const name='Pet'+species+'Paw'+side,paw=rig.scene.getObjectByName(name).getWorldPosition(new THREE.Vector3());
        const pose=state[species.toLowerCase()],allowance=.024+.06*pose.speed+.02*Math.abs(pose.turn);
        if(last[name])assert.ok(paw.distanceTo(last[name])<allowance,`native paw motion stays within its speed/turn bound: ${seed} ${t} ${name}`);
        if(last[name]&&paw.distanceTo(last[name])>maxTransition){maxTransition=paw.distanceTo(last[name]);worst={seed,t,name,current:state[species.toLowerCase()],previous:oldState?.[species.toLowerCase()]};}last[name]=paw;
        assert.ok(paw.toArray().every(Number.isFinite),'runtime native paw transforms stay finite');
      }
    }
    oldState=state;
  }
  animator.dispose();
}
console.log({maxTransition,minUp,worst});
assert.ok(maxTransition<.07,'integrated native paws have no large discontinuities');
console.log(`Blender rig: 3 skins, 42 unique bones, 22 clips, ${(bytes.length/1024).toFixed(0)} KiB; contact slip ${(maxSlip*1000).toFixed(2)} mm, ground error ${(maxGroundError*1000).toFixed(2)} mm; 1500s integrated motion, bodies upright, no abrupt paw jumps.`);
