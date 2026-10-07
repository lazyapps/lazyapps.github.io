import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {sampleLeaf,LEAF_FLOOR} from '../src/lib/fondfont/nature.mjs';
import {createGardenLife,petCanStand,petsClear,sampleButterfly} from '../src/lib/fondfont/garden-life.mjs';
import {sampleMotion,wheelTravel,truckSteering,DRIFT_MAX,DURATION,TIMING,SOURCE,DESTINATION,ROAD,DECK,CLEARANCE,REAR_AXLE,TURN_RADIUS,TURN_X,WHEEL_RADIUS,LIBRARY_STOP} from '../src/lib/fondfont/motion.mjs';
const close=(a,b,message,tolerance=1e-7)=>assert.ok(Math.abs(a-b)<tolerance,`${message}: ${a} ≠ ${b}`);
const groundDistance=(x,z)=>Math.abs(Math.hypot(Math.max(0,Math.abs(x)-TURN_X),z-(ROAD-TURN_RADIUS))-TURN_RADIUS);
const portals=JSON.parse(readFileSync(new URL('./assets/fondfont/blender-v2/industrial-projection.json',import.meta.url)));
for(let t=0;t<DURATION;t+=.01){
  const s=sampleMotion(t),{cargo:c,truck:v}=s;
  for(const part of [v,c,s.source,s.receiver])assert.ok(Object.values(part).every(Number.isFinite));
  assert.ok(c.y>=-1e-8&&c.y<=CLEARANCE+1e-8,'cargo stays above ground and within lift clearance');
  if(t<TIMING.loadLower[1]||t>=TIMING.reset){close(s.source.fork,c.y+.127,'source forks support the pallet underside');close(s.source.z,c.z,'source stacker carries the pallet');close(s.source.x,c.x,'source load follows lateral alignment');}
  if(t>=TIMING.unloadRaise[0]&&t<TIMING.unloadSettle[1]){close(s.receiver.fork,c.y+.127,'receiver forks support the pallet underside');close(s.receiver.z,c.z,'receiver stacker carries the pallet');close(s.receiver.x,c.x,'receiver load follows lateral alignment');}
  if(t>=TIMING.loadLower[1]&&t<TIMING.unloadRaise[0]){close(c.x,v.x-.75,'cargo sits on truck');close(c.y,DECK,'cargo deck contact');close(c.z,v.z,'cargo lateral contact');}
  if(t>=TIMING.sourceWithdraw[0]&&t<TIMING.sourceWithdraw[1])assert.ok(s.source.fork-.055>1.069,'withdrawn forks clear truck deck');
  if(t>=TIMING.unloadSettle[1]&&t<TIMING.reset){close(c.y,0,'delivered pallet rests on warehouse floor');assert.ok(s.receiver.fork-.055>=0,'released forks clear warehouse floor');}
  for(const [i,stacker] of [s.source,s.receiver].entries()){
    const mastFront=stacker.z-1.05*Math.cos(stacker.angle)+.44*Math.abs(Math.sin(stacker.angle))+.06, mastTop=Math.max(1.52,stacker.fork+.4775,1.4625+Math.max(0,stacker.fork-1.05));
    assert.ok(mastFront<=ROAD-.925,'mast stays clear of open truck loading side');
    const tip=stacker.z+.50*Math.cos(stacker.angle)+.5775*Math.abs(Math.sin(stacker.angle));
    if([s.sourceOpen,s.receiverOpen][i]===0)assert.ok(tip<portals[i].door_z,'fork tines retract inside closed shutter');
    if(s.sideGate<.001&&stacker.fork<1.48)assert.ok(tip<ROAD-.925,'lowered forks clear closed truck sideboard');
    if(mastFront<=.71)assert.ok(mastTop<portals[i].door_height,'retracted mast clears building eave and portal');
    // Check both sides of the complete body, not just the mast centerline.
    for(const x of [-.71,.71])for(const z of [-1.04,.66]){
      const wx=stacker.x+x*Math.cos(stacker.angle)+(z-1.6)*Math.sin(stacker.angle);
      const wz=stacker.z-x*Math.sin(stacker.angle)+(z-1.6)*Math.cos(stacker.angle);
      if(wz<.71)assert.ok(Math.abs(wx-[SOURCE,DESTINATION][i])<portals[i].door_width/2-.03,'forklift body clears portal jambs throughout its turn');
    }
  }
  const palletFront=c.z+.56*Math.abs(Math.cos(c.angle))+1.025*Math.abs(Math.sin(c.angle));
  const palletSide=1.025*Math.abs(Math.cos(c.angle))+.56*Math.abs(Math.sin(c.angle));
  if(c.y<DECK-.001&&Math.abs(c.x-(v.x-.81))<1.61+palletSide)assert.ok(palletFront<ROAD-.89,'low pallet clears the complete truck deck footprint before lifting/lowering');
  if(c.z<1.2)assert.ok(c.y+1.044<portals[c.x<0?0:1].door_height,'loaded cases clear the building portal');
  if(t>=TIMING.return[0])for(const x of [-1.82,-.75,1.62])for(const z of [-.88,.88]){
    const wx=v.x+x*Math.cos(v.angle+v.drift)+z*Math.sin(v.angle+v.drift),wz=v.z-x*Math.sin(v.angle+v.drift)+z*Math.cos(v.angle+v.drift);
    const heading=v.angle+v.drift+truckSteering(v,x,z/.88);
    for(const longitudinal of [-.12,.12])for(const lateral of [-.1175,.1175]){
      const px=wx+longitudinal*Math.cos(heading)+lateral*Math.sin(heading),pz=wz-longitudinal*Math.sin(heading)+lateral*Math.cos(heading);
      assert.ok(groundDistance(px,pz)<1.8,'complete six-tire contact patches remain inside actual asphalt boundary');
    }
  }
}
assert.ok(1.095-.04>.88+.235/2,'cranked loading-side hinge keeps the down-folded sideboard outside rear tires');
assert.ok(.34+.115/2<.8-.22/2,'fork tines clear outer pallet feet');
for(let t=0;t<DURATION;t+=.01){
  const s=sampleMotion(t);
  for(const forklift of [s.source,s.receiver])assert.ok(forklift.reach>=-1e-8&&forklift.reach<=1+1e-8,'native reach stays inside its physical stroke');
  if(t<TIMING.loadLower[1]||t>=TIMING.restockLift[0])close(s.source.reach,1,'loaded source forks stay fully extended');
  if(t>=TIMING.unloadRaise[0]&&t<=TIMING.unloadRelease[1])close(s.receiver.reach,1,'loaded receiver forks stay fully extended');
}
const before=sampleMotion(TIMING.reset-1e-5),after=sampleMotion(TIMING.reset+1e-5);
close(before.sourceOpen,0,'foundry shutter hides inventory reset');close(before.receiverOpen,0,'warehouse shutter hides inventory reset');
close(before.cargo.z,LIBRARY_STOP,'delivered cargo inside warehouse');close(after.cargo.z,-.7,'new cargo inside foundry');
close(before.cargo.x,DESTINATION,'destination batch');close(after.cargo.x,SOURCE,'source batch');
for(const t of [0,1,DURATION,...Object.values(TIMING).filter(Array.isArray).flat()]){
  const a=sampleMotion(t-1e-5),b=sampleMotion(t+1e-5);
  for(const part of ['truck','cargo','source','receiver'])for(const axis of ['x','y','z','fork','angle'])if(axis in a[part]&&!(axis==='angle'&&part==='truck'))close(a[part][axis],b[part][axis],`${part}.${axis} continuous at ${t}`,.001);
}
const initial=sampleMotion(0),last=sampleMotion(DURATION-1e-7);
for(const part of ['cargo','source','receiver'])for(const key of Object.keys(initial[part]))close(initial[part][key],last[part][key],`${part}.${key} periodic`);
close(Math.cos(initial.truck.angle),Math.cos(last.truck.angle),'heading periodic');close(Math.sin(initial.truck.angle),Math.sin(last.truck.angle),'heading periodic');
for(const x of [-1.82,-.75,1.62])for(const z of [-.88,.88]){
  let previous=0;
  for(let t=0;t<2*DURATION;t+=.02){const d=wheelTravel(t,x,z);assert.ok(d>=previous-1e-7,'wheel travel monotonic through two loops');previous=d;}
  close(wheelTravel(DURATION-1e-6,x,z),wheelTravel(DURATION+1e-6,x,z),'wheel rotation continuous at cycle boundary',.0001);
}
assert.ok(LIBRARY_STOP-.56>-4.4&&LIBRARY_STOP+.56<.201,'delivered pallet fits inside recessed warehouse');
for(const portal of portals){assert.ok(portal.door_height>1.48+.03,'retracted mast has head clearance');assert.ok(portal.door_width>2.05+.1,'pallet clears both jambs');}
assert.ok(WHEEL_RADIUS>.4&&REAR_AXLE<0);
for(let t=0;t<TIMING.receiverOpen[0];t+=.01)close(sampleMotion(t).receiverOpen,0,'warehouse remains closed until truck arrival');
for(let t=TIMING.receiverOpen[0];t<TIMING.receiverClose[1];t+=.01)close(sampleMotion(t).sourceOpen,0,'foundry stays closed during warehouse delivery');
for(const t of [11,14,29,39])close(sampleMotion(t).sideGate,0,'truck loading side restored during transport');
for(let t=0;t<DURATION;t+=.01){
  const s=sampleMotion(t);
  for(const forklift of [s.source,s.receiver])assert.ok(Math.abs(forklift.angle)<.25,'low alignment and empty return turns stay below fifteen degrees');
  if(t>=TIMING.loadRaise[0]&&t<TIMING.sourceWithdraw[1])close(s.source.angle,0,'raised loading and withdrawal stay square to the truck');
  if(t>=TIMING.receiverRaise[0]&&t<TIMING.unloadLower[1])close(s.receiver.angle,0,'raised pickup and withdrawal stay square to the truck');
  if(Math.abs(s.cargo.angle)>1e-6)assert.ok(s.cargo.y<.041,'carried pallets turn only at low height');
}
for(const [start,end] of [[0,TIMING.loadLower[1]],[TIMING.unloadRaise[0],TIMING.unloadSettle[1]]]){
  for(let t=start+.002;t<end-.002;t+=.01){
    const a=sampleMotion(t-.001).cargo,b=sampleMotion(t+.001).cargo,c=sampleMotion(t).cargo;
    const dx=b.x-a.x-1.2*(Math.sin(b.angle)-Math.sin(a.angle));
    const dz=b.z-a.z-1.2*(Math.cos(b.angle)-Math.cos(a.angle));
    assert.ok(Math.abs(dx*Math.cos(c.angle)-dz*Math.sin(c.angle))<1e-7,'forklift front axle rolls along its heading without rotating a stationary load');
  }
}
console.log('FondFont: fork support, mast/door clearance, fork withdrawal, road contact, replenishment and two-cycle continuity passed.');
const bytes=readFileSync(new URL('../public/v/fondfont/blender-v2/factory-truck-v14.glb',import.meta.url));
const gltf=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
for(const name of ['Truck','TruckCargo','Cargo','SourceStacker','ReceiverStacker','SourceForks','ReceiverForks','SourceInnerMast','ReceiverInnerMast','SourcePiston','ReceiverPiston','SourceDoor','ReceiverDoor','FoundrySign','WarehouseSign','FoundryArt','CabRoofName','FlatbedName','RailNameFront','PhoneRoof','Garden','LoadingSideGate','PhoneScreenGlyph',...Array.from({length:3},(_,i)=>`TypeTray${i}`)])assert.ok(gltf.nodes.some(n=>n.name===name),`model preserves ${name}`);
for(const name of ['FoundryBadge','FoundryWordmark','SourceBridge','ReceiverBridge','SourceShuttle','ReceiverShuttle','RailNameBack'])assert.ok(!gltf.nodes.some(n=>n.name===name),`obsolete or conflicting geometry removed: ${name}`);
for(const x of [-1.82,-.75,1.62])for(const side of [-1,1])for(const root of ['Wheel','Steer'])assert.ok(gltf.nodes.some(n=>n.name===`${root}_${x}_${side}`),'independent truck wheel pivots preserved');
assert.ok(bytes.length<8*1024*1024,'compressed model remains under 8 MiB');
assert.ok(!gltf.nodes.some(n=>n.name==='Architecture_imagegen limestone plinth'),'no visible rectangular land plinth');
for(const name of ['imagegen FondFont red enamel','imagegen plum enamel','imagegen industrial foundry alpha','imagegen industrial warehouse alpha'])assert.ok(gltf.materials.some(m=>m.name===name),`original imagegen material survives: ${name}`);
assert.ok(gltf.nodes.some(n=>n.name==='ChimneySmoke'),'native chimney emitter is preserved');
assert.ok(gltf.nodes.some(n=>n.extras?.native_botanical),'real botanical mesh survives export and merging');
for(const m of gltf.materials.filter(m=>m.name.startsWith('Botanical ')))assert.ok(!m.pbrMetallicRoughness?.baseColorTexture,'botanical surfaces are modeled materials, not image cards');
assert.ok(!gltf.materials.some(m=>m.name.startsWith('imagegen whole meadow ')),'no botanical image cards remain');
console.log(`GLB: stackers, three exposed type trays, wheel pivots, original imagegen materials and ${(bytes.length/1024/1024).toFixed(2)} MiB budget passed.`);
const garden=JSON.parse(readFileSync(new URL('./assets/fondfont/blender-v2/garden-layout.json',import.meta.url)));
const c=Math.cos(garden.camera_pitch),s=Math.sin(garden.camera_pitch);
for(const patch of garden.patches)for(const [i,building] of portals.entries()){
  const [left,top,right,bottom]=building.bounds,scale=6.6/(right-left),x=[SOURCE,DESTINATION][i];
  const base=c*patch.y-s*patch.z;
  const planting=[patch.x-patch.width/2-garden.max_sway,base-.008,patch.x+patch.width/2+garden.max_sway,base+patch.height+.008];
  const facade=[x-3.3,(building.ground-bottom)*scale-s*.55,x+3.3,(building.ground-top)*scale-s*.55];
  assert.ok(planting[2]<facade[0]||planting[0]>facade[2]||planting[3]<facade[1]||planting[1]>facade[3],`complete ${patch.kind} planting clears ${building.root}, including chimney and maximum wind sway`);
}
for(let t=0;t<120;t+=.02)for(let i=0;i<6;i++){
  const leaf=sampleLeaf(t,i),next=sampleLeaf(t+.02,i);
  assert.ok([leaf.x,leaf.y,leaf.z,leaf.pitch,leaf.yaw,leaf.roll,leaf.size,leaf.opacity].every(Number.isFinite)&&leaf.y>=LEAF_FLOOR-1e-8&&leaf.opacity>=0&&leaf.opacity<=1,'falling leaves stay finite, above ground, and within alpha range');
  if(Math.hypot(next.x-leaf.x,next.y-leaf.y,next.z-leaf.z)>.3)assert.ok(leaf.opacity===0&&next.opacity<.005,'leaf respawns are below the renderer visibility threshold');
}
console.log('Garden: full projected patches clear both buildings; ambient leaves fall and respawn invisibly over 120 seconds.');
for(const species of ['Dog','Cat'])for(const part of ['','Body','Head','Tail',...['FL','FR','BL','BR'].flatMap(side=>['Hip','Knee','Paw'].map(joint=>joint+side))])assert.ok(gltf.nodes.some(n=>n.name==='Pet'+species+part),`native articulated ${species} ${part} remains editable`);
for(const name of ['Butterfly','ButterflyWingL','ButterflyWingR'])assert.ok(gltf.nodes.some(n=>n.name===name),`native butterfly hinge retained: ${name}`);
for(const m of gltf.materials.filter(m=>m.name.startsWith('Garden life ')))assert.ok(!m.pbrMetallicRoughness?.baseColorTexture,'pets and butterflies use volumetric native geometry, no raster cards');
const corners=new Set();
for(const seed of [47,11,991,2]){
  const life=createGardenLife(seed),moods=new Set();let minX=Infinity,maxX=-Infinity,minZ=Infinity;const progress={dog:0,cat:0};let lastPose,windowEnd=45;const pottyEnd={dog:null,cat:null};
  for(let t=0;t<600;t+=.05){
    const current=life.sample(t),next=life.sample(t+.025);
    if(lastPose)for(const species of ['dog','cat'])progress[species]+=Math.hypot(current[species].x-lastPose[species].x,current[species].z-lastPose[species].z);
    lastPose=current;
    if(t>=windowEnd){for(const species of ['dog','cat']){assert.ok(progress[species]>1,`${species} seed ${seed} time ${t} keeps moving over every 45-second window`);progress[species]=0;}windowEnd+=45;}
    assert.ok(petsClear(current.dog,current.cat),'oriented pet bodies do not intersect');
    for(const species of ['dog','cat']){
      const p=current[species],q=next[species];
      if(p.mood==='potty'){
        assert.ok(Math.hypot(p.x-(p.pottySide<0?-2.9:2.9),p.z-1.3)<.3,'urination stays at its chosen building corner');
        pottyEnd[species]=p.actionTime;corners.add(p.pottySide);
      }else if(pottyEnd[species]!==null){assert.ok(pottyEnd[species]>5.3,'urination finishes its native stand-to-pose-to-stand clip');pottyEnd[species]=null;}
      moods.add(p.mood);minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minZ=Math.min(minZ,p.z);
      assert.ok(Object.values(p).every(v=>typeof v==='boolean'||typeof v==='string'||Number.isFinite(v)),'pet poses stay finite');
      assert.ok(petCanStand(p),'complete pet capsules clear buildings, flower bed, loading bays and asphalt');
      const travel=Math.hypot(p.x-q.x,p.z-q.z);
      const forward=(q.x-p.x)*Math.cos(p.yaw)-(q.z-p.z)*Math.sin(p.yaw);
      assert.ok(forward>=-.00001,'navigation never moves opposite the pet facing');
      assert.ok(travel<.025,'pet motion remains continuous through random behavior changes');
      if(travel>.0001)assert.ok(Math.max(p.gait,q.gait)>.01,'all translating phases include walking');

    }
    for(let i=0;i<3;i++){const b=sampleButterfly(t,i);assert.ok(Object.values(b).every(Number.isFinite)&&b.y>.6&&Math.abs(b.x)<1.1&&b.z<0,'butterflies remain over the central flowers');}
  }
  assert.ok(maxX-minX>6&&minZ<-2,'random navigation reaches both front clearings and rear passage');
  assert.ok(moods.has('walk')&&moods.has('sniff')&&moods.has('watch'),'roaming includes locomotion and varied pauses');
  console.log(`Pets seed ${seed}: ${600} seconds, territory ${(maxX-minX).toFixed(2)}m wide, rear ${minZ.toFixed(2)}m, ${[...moods].join('/')}.`);
}
assert.equal(corners.size,2,'random urination visits both building corners across seeds');
assert.deepEqual(createGardenLife(47).sample(31),createGardenLife(47).sample(31),'fixed seed keeps posters reproducible');
assert.notDeepEqual(createGardenLife(47).sample(31),createGardenLife(48).sample(31),'new seeds create different live behavior');
console.log('Garden life: native geometry, swept collision clearance, broad random roaming, per-pet progress and butterfly flight passed.');
