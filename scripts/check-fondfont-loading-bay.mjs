import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import * as THREE from 'three';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {sampleMotion,DURATION} from '../src/lib/fondfont/motion.mjs';
import {createStackerAnimator} from '../src/lib/fondfont/stacker-animation.ts';
import {installLoadingBayVisibility} from '../src/lib/fondfont/loading-bay.ts';
import {createCampusCamera,aimCamera,roadOutline} from '../src/lib/fondfont/campus-camera.ts';
const bytes=readFileSync(new URL('../public/v/fondfont/blender-v3/campus-v3.glb',import.meta.url));
const gltf=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12))),bin=bytes.subarray(28+bytes.readUInt32LE(12));
await MeshoptDecoder.ready;
const nodes=gltf.nodes.map(n=>{
 const o=n.mesh===undefined?new THREE.Object3D():new THREE.Mesh(new THREE.BufferGeometry(),new THREE.MeshBasicMaterial());
 o.name=n.name;o.userData=n.extras??{};
 if(n.translation)o.position.fromArray(n.translation);if(n.rotation)o.quaternion.fromArray(n.rotation);if(n.scale)o.scale.fromArray(n.scale);
 return o;
});
gltf.nodes.forEach((n,i)=>n.children?.forEach(j=>nodes[i].add(nodes[j])));
const model=new THREE.Group();gltf.scenes[gltf.scene??0].nodes.forEach(i=>model.add(nodes[i]));model.updateMatrixWorld(true);
function vertices(i){
 const a=gltf.accessors[gltf.meshes[gltf.nodes[i].mesh].primitives[0].attributes.POSITION],view=gltf.bufferViews[a.bufferView],ext=view.extensions?.EXT_meshopt_compression;
 const data=new Uint8Array(ext.count*ext.byteStride);MeshoptDecoder.decodeGltfBuffer(data,ext.count,ext.byteStride,bin.subarray(ext.byteOffset??0,(ext.byteOffset??0)+ext.byteLength),ext.mode,ext.filter);
 const dv=new DataView(data.buffer),size={5122:2,5123:2,5126:4}[a.componentType],getter={5122:'getInt16',5123:'getUint16',5126:'getFloat32'}[a.componentType],div=a.normalized?({5122:32767,5123:65535}[a.componentType]??1):1;
 return Array.from({length:a.count},(_,j)=>new THREE.Vector3(...[0,1,2].map(k=>dv[getter]((a.byteOffset??0)+j*ext.byteStride+k*size,true)/div)).applyMatrix4(nodes[i].matrixWorld));
}
for(const name of ['Foundry','Warehouse']){
 const building=model.getObjectByName(name),[left,right,h,z]=building.userData.loading_bay_portal;
 assert.equal(building.userData.physical_loading_bay,true);
 const floorIndex=gltf.nodes.findIndex(n=>n.name===name+' bay floor'),floor=vertices(floorIndex);
 assert.ok(floor.every(v=>Math.abs(v.y)<.0001),'actual exported floor is flat at ground level');
 assert.ok(Math.min(...floor.map(v=>v.z))<=-4.399&&Math.max(...floor.map(v=>v.z))>=z-.001,'floor spans complete interior to sill');
 // A point under the old floating roof is outside the door's line of sight from the lens.
 const lens=createCampusCamera();aimCamera(lens,new THREE.Vector3(0,.25,-.8),()=>roadOutline());
 const insideRoof=new THREE.Vector3(building.position.x,1.52,-2.45),t=(z-lens.position.z)/(insideRoof.z-lens.position.z);
 assert.ok(lens.position.y+t*(insideRoof.y-lens.position.y)>h,'old floating roof position is beyond the actual doorway sight line');
 assert.ok(left<0&&right>0);
}
// Modeled sawtooth: each of the four bays rises to its peak at 74% of the bay width, on the right as in the artwork.
const slateIndex=gltf.nodes.findIndex(n=>n.name==='Foundry slate');
assert.ok(slateIndex>=0,'modeled slate roof is exported');
const slate=vertices(slateIndex),foundry=model.getObjectByName('Foundry'),peakY=Math.max(...slate.map(v=>v.y));
const peaks=[...new Set(slate.filter(v=>v.y>peakY-.002).map(v=>Math.round((v.x-foundry.position.x)*1000)/1000))].sort((a,b)=>a-b);
const expected=[0,1,2,3].map(i=>-3.3+1.65*i+1.65*.74);
for(const x of expected)assert.ok(peaks.some(p=>Math.abs(p-x)<.03),`sawtooth bay peak near ${x.toFixed(3)} (found ${peaks.join(', ')})`);
const camera=createCampusCamera();aimCamera(camera,new THREE.Vector3(0,.25,-.8),()=>roadOutline());
const shared=model.getObjectByName('Cargo').children.find(o=>o.isMesh)?.material;
const materials=installLoadingBayVisibility(model);
for(const material of materials){const shader={vertexShader:'#include <project_vertex>',fragmentShader:'#include <clipping_planes_fragment>'};material.onBeforeCompile(shader,{});assert.match(shader.fragmentShader,/vBayWorld\.z</);assert.match(shader.fragmentShader,/cameraPosition\+bayT\*/,'per-fragment line of sight through the door');assert.match(shader.vertexShader,/modelMatrix/);}
if(shared)assert.notEqual(model.getObjectByName('Cargo').children.find(o=>o.isMesh).material,shared,'clip materials are private to the moving load');
const animate=createStackerAnimator(model);
for(let t=0;t<DURATION;t+=.05){const state=sampleMotion(t);for(const [name,pose] of [['Source',state.source],['Receiver',state.receiver]]){animate(name,pose);assert.equal(model.getObjectByName(name+'Stacker').position.y,0);}}
console.log('Published native bay: continuous Y=0 floors, registered sill planes, four modeled sawtooth bays rising on the right; production portal clipping and stationary chassis elevation passed.');
