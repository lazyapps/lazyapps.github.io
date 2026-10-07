import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { sampleMotion, wheelTravel, truckSteering, WHEEL_RADIUS, DURATION } from '../src/lib/fondfont/motion.mjs';

function read(name) {
  const bytes = readFileSync(new URL(`../public/v/fondfont/blender-v2/${name}.glb`, import.meta.url));
  return { bytes, json: JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12))) };
}
const original = read('factory-building-v6').json;
const { bytes, json } = read('factory-truck-v14');
function descendants(gltf, index) {
  return [index, ...(gltf.nodes[index].children ?? []).flatMap(i => descendants(gltf, i))];
}
const truckIndex = original.nodes.findIndex(n => n.name === 'Truck');
let preserved = 0;
for (const i of descendants(original, truckIndex)) {
  const before = original.nodes[i];
  if (before.mesh !== undefined || before.name === 'Truck') continue;
  const afterIndex = json.nodes.findIndex(n => n.name === before.name);
  assert.ok(afterIndex >= 0, `preserved attachment ${before.name}`);
  const after = json.nodes[afterIndex];
  const parentBefore = original.nodes.find(n => n.children?.includes(i));
  const parentAfter = json.nodes.find(n => n.children?.includes(afterIndex));
  assert.equal(parentAfter?.name, parentBefore?.name, `${before.name} parent`);
  if (before.name === 'CabRoofName') {
    assert.ok(Math.abs(after.translation[1] - 2.372) < .00001, 'paint sits above the new 2.365m roof');
    assert.equal(after.translation[0], before.translation[0]);
    assert.equal(after.translation[2], before.translation[2]);
  } else for (const key of ['translation', 'rotation', 'scale', 'matrix']) {
    assert.deepEqual(after[key], before[key], `${before.name} ${key}`);
  }
  preserved++;
}
assert.equal(preserved, 21);
assert.equal(json.nodes.find(n => n.name === 'Truck').extras.wheel_radius, WHEEL_RADIUS);
assert.ok(json.materials.some(m => m.name === 'Precision truck graphite gate'));
assert.ok(json.materials.some(m => m.name === 'Precision truck clean automotive vermilion' && m.pbrMetallicRoughness.baseColorFactor[0] > .6 && m.pbrMetallicRoughness.baseColorFactor[1] < .04 && !m.pbrMetallicRoughness.baseColorTexture), 'plain red roof material survives window booleans');

assert.ok(json.materials.some(m => m.name === 'imagegen truck precision lamp optics' && m.pbrMetallicRoughness.baseColorTexture), 'actual imagegen lamp image is embedded');
assert.ok(!json.nodes.some(n => n.name === 'Cab editable quad cage'), 'editable source cage stays outside the web export');

// Decode actual exported tire geometry; source bitmap decoding belongs to browser checks.
const length = bytes.readUInt32LE(12);
const geometry = structuredClone(json);
geometry.materials = geometry.materials.map(m => ({ name: m.name }));
const text = JSON.stringify(geometry);
const chunk = Buffer.from(text.padEnd(Math.ceil(text.length / 4) * 4, ' '));
const buffer = Buffer.concat([bytes.subarray(0, 20), chunk, bytes.subarray(20 + length)]);
buffer.writeUInt32LE(buffer.length, 8); buffer.writeUInt32LE(chunk.length, 12);
const { scene } = await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength), '');
scene.traverse(o => { if (o.userData.name) o.name = String(o.userData.name); });
const truck = scene.getObjectByName('Truck');
const wheels = [];
for (const x of [-1.82, -.75, 1.62]) for (const side of [-1, 1]) {
  const wheel = scene.getObjectByName(`Wheel_${x}_${side}`);
  const tires = [];
  wheel.traverse(o => {
    if (o.isMesh && o.material.name === 'Precision truck soft tire rubber') tires.push(o);
  });
  assert.ok(tires.length, 'each native wheel retains actual tire surfaces');
  wheels.push({ wheel, steer: scene.getObjectByName(`Steer_${x}_${side}`), x, side, tires });
}
const point = new THREE.Vector3();
let lowest = Infinity, highest = -Infinity;
for (let t = 0; t < DURATION * 2; t += .15) {
  const pose = sampleMotion(t).truck;
  truck.position.set(pose.x, 0, pose.z); truck.rotation.y = pose.angle + pose.drift;
  for (const w of wheels) {
    w.wheel.rotation.z = -wheelTravel(t, w.x, w.side * .88) / WHEEL_RADIUS;
    w.steer.rotation.y = truckSteering(pose, w.x, w.side);
  }
  scene.updateMatrixWorld(true);
  for (const w of wheels) {
    let floor = Infinity;
    for (const tire of w.tires) {
      const positions = tire.geometry.attributes.position;
      for (let i = 0; i < positions.count; i++) {
        point.fromBufferAttribute(positions, i).applyMatrix4(tire.matrixWorld);
        floor = Math.min(floor, point.y);
      }
    }
    lowest = Math.min(lowest, floor); highest = Math.max(highest, floor);
    assert.ok(Math.abs(floor) < .002, `actual rolling/steering tire contact at ${t}: ${floor}`);
  }
}
console.log({ preservedAttachments: preserved, wheels: wheels.length, lowest, highest, bytes: bytes.length });
