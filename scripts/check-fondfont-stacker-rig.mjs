import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import * as THREE from 'three';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {createStackerAnimator} from '../src/lib/fondfont/stacker-animation.ts';
import {sampleMotion,DURATION} from '../src/lib/fondfont/motion.mjs';

// Use the exported Blender hierarchy, including every local rest transform.
const bytes=readFileSync(new URL('../public/v/fondfont/blender-v3/campus-v3.glb',import.meta.url));
const gltf=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)));
const nodes=gltf.nodes.map(n=>{
  const o=new THREE.Object3D();o.name=n.name;o.userData=n.extras??{};
  if(n.translation)o.position.fromArray(n.translation);if(n.rotation)o.quaternion.fromArray(n.rotation);if(n.scale)o.scale.fromArray(n.scale);
  if(n.matrix)new THREE.Matrix4().fromArray(n.matrix).decompose(o.position,o.quaternion,o.scale);
  return o;
});
gltf.nodes.forEach((n,i)=>n.children?.forEach(j=>nodes[i].add(nodes[j])));
const model=new THREE.Group();gltf.scenes[gltf.scene??0].nodes.forEach(i=>model.add(nodes[i]));
// Decode the published tire geometry; pivot/radius agreement alone cannot prove contact.
await MeshoptDecoder.ready;
const bin=bytes.subarray(28+bytes.readUInt32LE(12));
const tires=[];
for(const [i,n] of gltf.nodes.entries()){
  if(!/^(Source|Receiver)StackerWheel.*_rubber$/.test(n.name))continue;
  const a=gltf.accessors[gltf.meshes[n.mesh].primitives[0].attributes.POSITION];
  const view=gltf.bufferViews[a.bufferView],ext=view.extensions?.EXT_meshopt_compression;
  const size={5120:1,5121:1,5122:2,5123:2,5126:4}[a.componentType];
  let data,stride;
  if(ext){data=new Uint8Array(ext.count*ext.byteStride);MeshoptDecoder.decodeGltfBuffer(data,ext.count,ext.byteStride,bin.subarray(ext.byteOffset??0,(ext.byteOffset??0)+ext.byteLength),ext.mode,ext.filter);stride=ext.byteStride;}
  else{data=bin.subarray(view.byteOffset??0,(view.byteOffset??0)+view.byteLength);stride=view.byteStride??size*3;}
  const dv=new DataView(data.buffer,data.byteOffset,data.byteLength);
  const get={5120:'getInt8',5121:'getUint8',5122:'getInt16',5123:'getUint16',5126:'getFloat32'}[a.componentType];
  const divisor=a.normalized?({5120:127,5121:255,5122:32767,5123:65535}[a.componentType]??1):1;
  const vertices=Array.from({length:a.count},(_,j)=>new THREE.Vector3(...[0,1,2].map(k=>dv[get]((a.byteOffset??0)+j*stride+k*size,true)/divisor)));
  tires.push({node:nodes[i],vertices});
}
assert.equal(tires.length,8,'published model contains eight actual tire meshes');
let lowestSole=Infinity,highestSole=-Infinity;
const point=new THREE.Vector3();
const animate=createStackerAnimator(model);let maxTilt=0,maxContactError=0;
for(let t=0;t<DURATION*2;t+=.025){
  const state=sampleMotion(t);animate('Source',state.source);animate('Receiver',state.receiver);model.updateMatrixWorld(true);
  for(const tire of tires){
    let sole=Infinity;
    for(const v of tire.vertices)sole=Math.min(sole,point.copy(v).applyMatrix4(tire.node.matrixWorld).y);
    lowestSole=Math.min(lowestSole,sole);highestSole=Math.max(highestSole,sole);
  }
  for(const [name,pose] of [['Source',state.source],['Receiver',state.receiver]]){
    assert.equal(model.getObjectByName(name+'Stacker').userData.native_forklift_revision,'grounded-tread-and-low-chassis-v4');
    assert.ok(Math.abs(model.getObjectByName(name+'ForkReach').position.z-.35*pose.reach)<1e-8,'native fork extension follows reach state');
  }
  for(const name of ['Source','Receiver'])for(const wheel of model.getObjectByName(name+'Stacker').children.filter(o=>o.name.startsWith(name+'StackerWheel'))){
    const axle=new THREE.Vector3(1,0,0).applyQuaternion(wheel.getWorldQuaternion(new THREE.Quaternion()));
    maxTilt=Math.max(maxTilt,Math.abs(axle.y));
    assert.ok(Math.abs(wheel.position.x)>.57,'tire sidewalls remain outside the narrowed chassis');
    const y=wheel.getWorldPosition(new THREE.Vector3()).y;
    maxContactError=Math.max(maxContactError,Math.abs(y-Number(wheel.userData.radius)));
  }
}
assert.ok(maxTilt<1e-6,'steering and spinning never tilt forklift axles out of the ground plane');
assert.ok(maxContactError<1e-6,'all eight wheels remain in contact with the ground');
console.log(`Actual Blender forklift hierarchy: two full trips, eight grounded wheels, max axle tilt ${maxTilt}, contact error ${maxContactError}m.`);

assert.ok(lowestSole>-.001&&highestSole<.003,`actual rolling tire vertices stay within 3 mm of floor: ${lowestSole}..${highestSole}`);
const pose={x:0,z:0,fork:.127,angle:0,steer:0,reach:0};
animate('Source',pose);
const wheel=model.getObjectByName('SourceStacker').children.find(o=>o.name.startsWith('SourceStackerWheel'));
const beforeRoll=wheel.rotation.x;
animate('Source',{...pose,fork:1.2});
assert.equal(wheel.rotation.x,beforeRoll,'lifting a stationary carriage never rotates road wheels');
animate('Source',{...pose,z:.6});
assert.ok(Math.abs(wheel.rotation.x-beforeRoll-.6/Number(wheel.userData.radius))<1e-8,'visible wheel roll matches actual axle travel');
animate('Source',pose);
assert.ok(Math.abs(wheel.rotation.x-beforeRoll)<1e-8,'reverse road travel reverses wheel roll');
console.log(`Decoded tire soles over two trips: ${lowestSole.toFixed(6)}..${highestSole.toFixed(6)}m; independent carriage lift and signed wheel travel passed.`);
