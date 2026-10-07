import assert from 'node:assert/strict';
import {createLeafLitter,LEAF_DECK} from '../src/lib/fondfont/leaf-litter.mjs';
import {LEAF_FLOOR,leafGround} from '../src/lib/fondfont/nature.mjs';
import {sampleMotion} from '../src/lib/fondfont/motion.mjs';

const still=()=>({truck:{x:100,z:100,angle:0,drift:0}});
const litter=createLeafLitter(),quiet=createLeafLitter({truckAt:still});
let previous=new Set(),maxHeight=0,maxAirborne=0,airborne=new Map(),landings=[];
for(let t=0;t<=600;t+=.1){
  const state=litter.sample(t),ids=new Set(state.leaves.map(p=>p.id));
  for(const id of previous)assert.ok(ids.has(id),'landed leaves never disappear when the truck loops');
  assert.equal(ids.size,state.leaves.length,'one persistent leaf per arrival');
  for(const p of state.leaves){
    assert.ok([p.x,p.y,p.z,p.pitch,p.yaw,p.roll].every(Number.isFinite));
    assert.ok(p.y>=LEAF_FLOOR,'leaf collision keeps all leaves above ground');
    if(!p.airborne&&(!p.deck||t-p.deck.time>.25))assert.equal(p.pitch,-Math.PI/2,'settled leaves lie flat');
    if(p.deck){
      const truck=sampleMotion(t).truck,a=truck.angle+truck.drift,c=Math.cos(a),s=Math.sin(a);
      const dx=p.x-truck.x,dz=p.z-truck.z;
      assert.ok(Math.abs(dx*c-dz*s-p.deck.x)<1e-7&&Math.abs(dx*s+dz*c-p.deck.z)<1e-7,'deck leaves follow the exact moving/turning/drifting truck transform');
      assert.equal(p.y,LEAF_DECK,'leaves stay on the actual deck surface');
      assert.equal(p.kicks,0,'road wheels do not kick leaves through the truck floor');
    }
    if(!p.airborne&&airborne.get(p.id)){
      assert.ok(p.lastDisplacement>.3&&p.lastDisplacement<2,'every wheel wake settles at a visibly different nearby position');
      landings.push({dx:p.x-p.kickX,dz:p.z-p.kickZ});
    }
    airborne.set(p.id,p.airborne);
    if(!p.deck)maxHeight=Math.max(maxHeight,p.y);
  }
  maxAirborne=Math.max(maxAirborne,state.leaves.filter(p=>p.airborne).length);previous=ids;
}
const result=structuredClone(litter.sample(600)),baseline=structuredClone(quiet.sample(600));
assert.ok(result.leaves.length>100,'leaves accumulate beyond the six falling meshes');
assert.ok(result.kickCount>0&&maxAirborne>0,'actual truck wheels lift nearby leaves');
assert.ok(result.deckCount>0,'natural sky trajectories cross and land inside the actual truck bed');
assert.ok(landings.some(p=>p.dx>.3)&&landings.some(p=>p.dx<-.3)&&landings.some(p=>p.dz>.3)&&landings.some(p=>p.dz<-.3),'successive wakes vary their landing direction');
assert.ok(maxHeight>.1&&maxHeight<.5,'wheel wake lifts leaves gently, below half a metre');
const rest=structuredClone(quiet.sample(620));
for(const original of baseline.leaves){
  const leaf=rest.leaves.find(p=>p.id===original.id);
  assert.equal(leaf.x,original.x);assert.equal(leaf.z,original.z);assert.ok(Math.abs(leaf.y-leafGround(leaf.x,leaf.z))<1e-6,'resting leaves clear the actual asphalt and curb heights');
}
assert.ok(result.leaves.some((p,i)=>Math.hypot(p.x-baseline.leaves[i].x,p.z-baseline.leaves[i].z)>.1),'truck wake moves fallen leaves before they settle again');
const replay=createLeafLitter();assert.deepEqual(replay.sample(600),result,'frozen preview and live stepping produce the same leaf history');
litter.sample(10);assert.deepEqual(litter.sample(600),result,'seeking backward rebuilds the same persistent leaves');
// A downward plane crossing must occur inside the bed at that instant. Merely
// passing beneath an already grounded leaf cannot capture it.
const fall=(t,index)=>({id:`${index}:0`,index,cycle:0,x:0,z:index?10:0,y:2-t,pitch:0,yaw:.4,roll:0,size:.4,opacity:1});
const turn=t=>({truck:{x:0,z:0,angle:t*.4,drift:.1}});
const carried=createLeafLitter({truckAt:turn,leafAt:fall});
assert.equal(carried.sample(.8).deckCount,0,'no premature capture above the deck');
assert.equal(carried.sample(1.2).deckCount,1,'only the leaf inside the bed lands');
assert.equal(carried.sample(4).deckCount,1,'a captured falling leaf is not duplicated');
assert.ok(Math.abs(carried.sample(4).leaves.find(p=>p.deck).yaw-(.4+1.6-(2-LEAF_DECK)*.4))<1e-8,'leaf heading rotates with the bed');
const grounded=createLeafLitter({truckAt:turn,leafAt:(t,i)=>({...fall(t,i),y:.04})});
assert.equal(grounded.sample(4).deckCount,0,'the bed never attracts grounded leaves upward');
console.log(`Leaf litter: ${result.leaves.length} persistent leaves in 600s, ${result.deckCount} carried in the bed, ${result.kickCount} wheel wakes, max ground wake ${maxHeight.toFixed(3)}m; ${landings.length} checked landings displace >0.3m in varied directions; cadence/replay deterministic.`);
