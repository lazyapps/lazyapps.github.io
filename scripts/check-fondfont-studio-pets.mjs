import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {createStudioPetAnimator,createCatPair} from '../src/lib/fondfont/studio-pet-animation.ts';
import {createGardenLife} from '../src/lib/fondfont/garden-life.mjs';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';

const assets={cat:'cat-v1'};
for(const kind of ['cat']){
  const path=new URL(`../public/v/fondfont/pets/${assets[kind]}.glb`,import.meta.url);
  const bytes=readFileSync(path),length=bytes.readUInt32LE(12);
  const gltf=JSON.parse(bytes.subarray(20,20+length));
  assert.ok(gltf.meshes.every(m=>m.primitives.every(p=>p.attributes.COLOR_0===undefined)),'source paint masks are not multiplied twice');
  assert.ok(gltf.materials.some(m=>m.pbrMetallicRoughness.baseColorTexture),'original evaluated markings are retained');
  // Headless geometry verification leaves texture decoding to the real browser.
  gltf.materials=gltf.materials.map(m=>({name:m.name}));
  const json=Buffer.from(JSON.stringify(gltf).padEnd(Math.ceil(JSON.stringify(gltf).length/4)*4,' '));
  const result=Buffer.concat([bytes.subarray(0,20),json,bytes.subarray(20+length)]);
  result.writeUInt32LE(result.length,8);result.writeUInt32LE(json.length,12);
  const loaded=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(result.buffer.slice(result.byteOffset,result.byteOffset+result.byteLength),'');
  const root=loaded.scene.getObjectByName('PetCat');
  assert.ok(root.userData.studio_pet.native_paw_contact_error_max<.0002,'native planted paw solves to its target');
  const meshes=[];root.traverse(o=>{if(o.isMesh)meshes.push(o);});
  assert.ok(meshes.length>2&&meshes.every(m=>m.morphTargetInfluences.length===84),'actual source surfaces and groom all retain the evaluated poses');
  const body=meshes.find(m=>root.userData.studio_pet.body_mesh?m.name===root.userData.studio_pet.body_mesh:/GEO_autumn_body$/.test(m.name));
  assert.ok(body,'professional source body is present');
  let minGround=Infinity,maxGround=-Infinity,maxDisplacement=0;
  const v=new THREE.Vector3(),rest=new THREE.Vector3();
  for(let frame=0;frame<root.userData.studio_pet.walk_poses;frame++){
    body.morphTargetInfluences.fill(0);
    body.morphTargetInfluences[body.morphTargetDictionary[`Walk${String(frame).padStart(2,'0')}`]]=1;
    loaded.scene.updateMatrixWorld(true);
    let floor=Infinity;
    for(let i=0;i<body.geometry.attributes.position.count;i++){
      body.getVertexPosition(i,v);rest.fromBufferAttribute(body.geometry.attributes.position,i);
      maxDisplacement=Math.max(maxDisplacement,v.distanceTo(rest));
      v.applyMatrix4(body.matrixWorld);assert.ok(v.toArray().every(Number.isFinite));floor=Math.min(floor,v.y);
    }
    minGround=Math.min(minGround,floor);maxGround=Math.max(maxGround,floor);
  }
  assert.ok(minGround>-.002&&maxGround<.002,`actual evaluated toe surfaces stay on the ground: ${minGround}..${maxGround}`);
  assert.ok(maxDisplacement>.02,'walk deforms the source mesh');
  console.log(kind,{bytes:bytes.length,meshes:meshes.length,minGround,maxGround,maxDisplacement,sourceContactError:root.userData.studio_pet.native_paw_contact_error_max});
}

let model;
for(const kind of ['cat']){
 const bytes=readFileSync(new URL(`../public/v/fondfont/pets/${assets[kind]}.glb`,import.meta.url));
 const len=bytes.readUInt32LE(12),json=JSON.parse(bytes.subarray(20,20+len));json.materials=json.materials.map(m=>({name:m.name}));
 const text=JSON.stringify(json),chunk=Buffer.from(text.padEnd(Math.ceil(text.length/4)*4,' '));
 const geometry=Buffer.concat([bytes.subarray(0,20),chunk,bytes.subarray(20+len)]);geometry.writeUInt32LE(geometry.length,8);geometry.writeUInt32LE(chunk.length,12);
 const loaded=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(geometry.buffer.slice(geometry.byteOffset,geometry.byteOffset+geometry.byteLength),'');model=createCatPair(loaded.scene).scene;
}
const charcoal=model.getObjectByName('PetCatCharcoal'),calico=model.getObjectByName('PetCat');
assert.ok(charcoal&&calico&&!model.getObjectByName('PetDog'),'two cats, no dog');
assert.notEqual(charcoal.userData.studio_pet,calico.userData.studio_pet,'per-cat rig metadata is independent');
const charcoalBody=charcoal.getObjectByName('CalicoCatBody'),calicoBody=calico.getObjectByName('CalicoCatBody');
assert.equal(charcoalBody.geometry,calicoBody.geometry,'two cats share decoded geometry');
assert.notEqual(charcoalBody.morphTargetInfluences,calicoBody.morphTargetInfluences,'independent animation weights');
assert.notEqual(charcoalBody.material,calicoBody.material,'charcoal coat does not recolor the original cat');
assert.equal(charcoalBody.material.customProgramCacheKey(),'fondfont-calico-charcoal-coat-v1');
let maxSlip=0,maxToeFrameJump=0,maxReach=0,maxSoleStretch=0;
function run(name,poseAt,duration,fps=60){
 let scenarioSlip=0,scenarioJump=0;
 const animator=createStudioPetAnimator(model);let previous;
 for(let i=0;i<=duration*fps;i++){
  const t=i/fps,life=poseAt(t);animator.update(life,t);model.updateMatrixWorld(true);
  const states=animator.diagnostics();
  for(let pet=0;pet<2;pet++)for(let foot=0;foot<4;foot++){
   const f=states[pet].feet[foot];
   maxReach=Math.max(maxReach,f.reach);
   maxSoleStretch=Math.max(maxSoleStretch,...f.soleLengths.map((v,i)=>Math.abs(v-f.restLengths[i])));
   if(f.planted){scenarioSlip=Math.max(scenarioSlip,f.slip);maxSlip=Math.max(maxSlip,f.slip);}
   assert.ok(states[pet].feet.filter(f=>f.planted).length>=1,'motion always retains a planted support paw');
   for(let m=0;m<3;m++){
    const p=f.points[m];assert.ok(p.every(Number.isFinite),'finite decoded sole marker');
    if(previous){const jump=Math.hypot(...p.map((v,j)=>v-previous[pet].feet[foot].points[m][j]));scenarioJump=Math.max(scenarioJump,jump);maxToeFrameJump=Math.max(maxToeFrameJump,jump*fps/60);}
    assert.ok(p[1]>-.004,'native sole stays above the ground tolerance');
   }
  }
  previous=states;
 }
 console.log(name,{fps,slip:scenarioSlip,frameJump:scenarioJump});
}
const base=createGardenLife(47).sample(0).dog;
const both=p=>({dog:{...base,...p},cat:{...base,...p,x:p.x+2}});
run('pivot left / right and stop',t=>{const yaw=t<3?t*.8:t<4?2.4:t<7?2.4-(t-4)*.8:0;const turn=t<3?.8:t<4?0:t<7?-.8:0;return both({x:0,z:0,yaw,turn,vx:0,vz:0,speed:0,look:turn*.25,distance:0});},9);
run('forward curved start / stop',t=>{const u=Math.min(t,6),yaw=u*.45,x=.35/.45*Math.sin(yaw),z=.35/.45*(Math.cos(yaw)-1);return both({x,z,yaw,turn:t<6?.45:0,vx:t<6?.35*Math.cos(yaw):0,vz:t<6?-.35*Math.sin(yaw):0,speed:t<6?.35:0,look:.15,distance:u*.35});},9);
for(const seed of [47,11,991,2]){const garden=createGardenLife(seed);run('navigation '+seed,t=>garden.sample(t),120);}
for(const fps of [30,120]){const garden=createGardenLife(47);run('frame-rate continuity '+fps,t=>garden.sample(t),60,fps);}
assert.ok(maxSlip<.005,`decoded planted toe/heel slip under 5 mm: ${maxSlip}`);
assert.ok(maxToeFrameJump<.025,`no abrupt decoded paw jumps: ${maxToeFrameJump}`);
assert.ok(maxReach<.35,'paw correction stays within the native leg reach regression bound');
assert.ok(maxSoleStretch<.003,'finite native yaw preserves sole edge lengths within 3 mm');
console.log({maxReach,maxSoleStretch});
console.log('Two native cats: shared geometry, independent motion/materials, turning and planted-paw transitions passed.');
