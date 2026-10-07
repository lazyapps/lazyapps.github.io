// Physical model coordinates in meters. A single clock owns all moving parts.
export const DURATION=47.9;
export const SOURCE=-5.6,DESTINATION=5.6,ROAD=4,DECK=1.07,DOCK=0;
export const LIBRARY_STOP=-.85;
export const CLEARANCE=1.19,WHEEL_RADIUS=.435,DRIFT_MAX=.34;
export const REAR_AXLE=-1.285,TURN_RADIUS=4.8,TURN_X=7.4;
export const TIMING={
  loadLift:[1,1.5],loadExit:[1.6,2.0],loadRaise:[2.6,3.8],loadAdvance:[3.9,6.8],
  loadAlign:[2.1,2.5],loadApproach:[6.9,7.5],loadLower:[7.7,8.7],
  loadRelease:[8.8,9],sourceWithdraw:[9.1,10.1],sourceLower:[10.2,10.7],
  sourceReturn:[12,14.6],sourceClose:[14.7,15.25],drive:[10.9,15.3],
  receiverOpen:[15.3,16],receiverExit:[16.1,18.5],receiverBendIn:[18.55,19.15],receiverAdvance:[20.7,22.9],receiverBendOut:[19.2,19.8],receiverRaise:[19.9,20.6],
  receiverApproach:[23,23.6],unloadRaise:[23.8,24.4],unloadWithdraw:[24.5,25.1],
  unloadAlign:[25.2,26.6],unloadRetreat:[26.7,28.3],unloadLower:[28.4,29.3],unloadBendHome:[29.4,30.1],unloadStraighten:[30.2,30.9],
  unloadEnter:[31,33.6],unloadSettle:[33.7,34.1],unloadRelease:[34.2,34.5],receiverRetract:[34.5,34.8],
  receiverClose:[34.8,35.9],return:[34.8,47.1],reset:40.7,
  sourceOpen:[41.2,42.2],restockReach:[42.05,42.3],restockLift:[42.3,42.9],restockExit:[43,46.7],restockLower:[46.7,47],
  gateClose:[10.7,10.9],gateUnloadClose:[28.6,29],gateReload:[47.1,DURATION],
};
export const smooth=(a,b,t)=>{const p=Math.max(0,Math.min(1,(t-a)/(b-a)));return p*p*(3-2*p);};
const mix=(a,b,t)=>a+(b-a)*t;
const cycle=t=>((t%DURATION)+DURATION)%DURATION;
const ramp=(key,t)=>smooth(...TIMING[key],t);
const loadedLength=DESTINATION-SOURCE;
const firstLength=TURN_X-(DESTINATION+.75+REAR_AXLE),arcLength=Math.PI*TURN_RADIUS,rearLength=2*TURN_X,lastLength=(SOURCE+.75+REAR_AXLE)+TURN_X;
export const RETURN_LENGTH=firstLength+arcLength+rearLength+arcLength+lastLength;
function returnPose(distance){
  let d=distance,x,z=ROAD,angle=0,curvature=0;
  if(d<=firstLength)x=DESTINATION+.75+REAR_AXLE+d;
  else if((d-=firstLength)<=arcLength){
    angle=d/TURN_RADIUS;x=TURN_X+TURN_RADIUS*Math.sin(angle);z=ROAD-TURN_RADIUS+TURN_RADIUS*Math.cos(angle);curvature=1/TURN_RADIUS;
  }else if((d-=arcLength)<=rearLength){x=TURN_X-d;z=ROAD-2*TURN_RADIUS;angle=Math.PI;}
  else if((d-=rearLength)<=arcLength){
    angle=Math.PI+d/TURN_RADIUS;x=-TURN_X-TURN_RADIUS*Math.sin(d/TURN_RADIUS);z=ROAD-TURN_RADIUS-TURN_RADIUS*Math.cos(d/TURN_RADIUS);curvature=1/TURN_RADIUS;
  }else{x=-TURN_X+(d-arcLength);angle=2*Math.PI;}
  return{x:x-REAR_AXLE*Math.cos(angle),z:z+REAR_AXLE*Math.sin(angle),angle,curvature};
}
// Rear-steered forklifts follow the front axle path. The load sits 1.2 m ahead
// of that axle, so its cornering motion follows the rigid vehicle as well.
const LOAD_OVERHANG=1.2;
// Finish small alignment turns with the load low. Raised transfers remain
// square to the truck and door instead of yawing the mast and pallet beside it.
function bend(key,t,dx,dz){
  const p=ramp(key,t),lateral=p*p*(3-2*p);
  return {x:dx*lateral,z:dz*p,angle:Math.atan(dx*6*p*(1-p)/dz)};
}
function sourcePath(t){
  const a=bend('loadExit',t,.04,.4),b=bend('loadAlign',t,-.04,.4);
  return{x:SOURCE+a.x+b.x,z:1.4+a.z+1.5*ramp('loadAdvance',t)+b.z+.3*ramp('loadApproach',t),angle:a.angle+b.angle};
}
function receiverApproachPath(t){
  const a=bend('receiverBendIn',t,.04,.4),b=bend('receiverBendOut',t,-.04,.4);
  return{x:DESTINATION+a.x+b.x,z:LIBRARY_STOP+(1.4-LIBRARY_STOP)*ramp('receiverExit',t)+a.z+1.5*ramp('receiverAdvance',t)+b.z+.3*ramp('receiverApproach',t),angle:a.angle+b.angle};
}
function receiverPath(t){
  const a=bend('unloadBendHome',t,.04,-.4),b=bend('unloadStraighten',t,-.04,-.4);
  return{x:DESTINATION+a.x+b.x,z:ROAD-.3*ramp('unloadWithdraw',t)-.7*ramp('unloadAlign',t)-.8*ramp('unloadRetreat',t)+a.z+b.z-(1.4-LIBRARY_STOP)*ramp('unloadEnter',t),angle:a.angle+b.angle};
}
function carry(path,t){
  const pose=path(t),before=path(t-.001),after=path(t+.001);
  const speed=(after.x-before.x)*Math.sin(pose.angle)+(after.z-before.z)*Math.cos(pose.angle);
  const steer=Math.abs(speed)>1e-8?-Math.atan(1.15*(after.angle-before.angle)/speed):0;
  return{...pose,x:pose.x+LOAD_OVERHANG*Math.sin(pose.angle),z:pose.z+LOAD_OVERHANG*(Math.cos(pose.angle)-1),steer};
}
function sourceHomePath(t){
  const p=ramp('sourceReturn',t);
  return{x:SOURCE+.25*Math.sin(Math.PI*p)**2,z:2.5-3.2*p,angle:Math.atan(-.25*Math.PI*Math.sin(2*Math.PI*p)/3.2)};
}
function sourceLoad(t){
  return{...carry(sourcePath,t),y:.04*ramp('loadLift',t)+(CLEARANCE-.04)*ramp('loadRaise',t)-(CLEARANCE-DECK)*ramp('loadLower',t)};
}
function receiverUnload(t){
  return{...carry(receiverPath,t),y:DECK+(CLEARANCE-DECK)*ramp('unloadRaise',t)-(CLEARANCE-.04)*ramp('unloadLower',t)-.04*ramp('unloadSettle',t)};
}
export function sampleMotion(seconds){
  const t=cycle(seconds),drive=ramp('drive',t);
  let truck={x:mix(SOURCE+.75,DESTINATION+.75,drive),z:ROAD,angle:0,curvature:0,distance:loadedLength*drive};
  if(t>=TIMING.return[0]){const distance=RETURN_LENGTH*ramp('return',t);truck={...returnPose(distance),distance:loadedLength+distance};}
  let cargo,source={x:SOURCE,z:1.4,fork:.127,angle:0,steer:0},receiver={x:DESTINATION,z:LIBRARY_STOP,fork:.127,angle:0,steer:0},phase=0;
  if(t<TIMING.loadLower[1]){
    cargo=sourceLoad(t);source={x:cargo.x,z:cargo.z,fork:cargo.y+.127,angle:cargo.angle,steer:cargo.steer};phase=t<1?0:1;
  }else if(t<TIMING.reset){
    cargo={x:truck.x-.75,y:DECK,z:ROAD,angle:0};
    source.z=ROAD-(ROAD-2.5)*ramp('sourceWithdraw',t);
    if(t>=TIMING.sourceReturn[0])source={...source,...carry(sourceHomePath,t)};
    source.fork=DECK+.127-.07*ramp('loadRelease',t)-(DECK-.07)*ramp('sourceLower',t);
    if(t>=TIMING.unloadRaise[0]){
      cargo=receiverUnload(t);receiver={x:cargo.x,z:cargo.z,fork:cargo.y+.127-.07*ramp('unloadRelease',t),angle:cargo.angle,steer:cargo.steer};
    }
    phase=t<TIMING.receiverOpen[0]?2:t<TIMING.unloadSettle[1]?3:4;
  }else{
    cargo={x:SOURCE,y:.04*(ramp('restockLift',t)-ramp('restockLower',t)),z:mix(-.7,1.4,ramp('restockExit',t)),angle:0};
    source={x:cargo.x,z:cargo.z,fork:cargo.y+.127,angle:0,steer:0};
  }
  if(t<TIMING.unloadRaise[0]){
    const approach=carry(receiverApproachPath,t);
    receiver={...receiver,x:approach.x,z:approach.z,angle:approach.angle,steer:approach.steer};
    receiver.fork=.127+DECK*ramp('receiverRaise',t);
  }else if(t>=TIMING.reset){
    receiver={x:DESTINATION,z:LIBRARY_STOP,fork:.057+.07*smooth(TIMING.reset,TIMING.reset+.2,t),angle:0,steer:0};
  }
  const sourceOpen=1-ramp('sourceClose',t)+ramp('sourceOpen',t),receiverOpen=ramp('receiverOpen',t)-ramp('receiverClose',t);
  const sourceReach=1-ramp('sourceLower',t)+ramp('restockReach',t);
  const receiverReach=ramp('receiverRaise',t)-ramp('receiverRetract',t);
  const sideGate=1-ramp('gateClose',t)+ramp('receiverOpen',t)-ramp('gateUnloadClose',t)+ramp('gateReload',t);
  truck.drift=truck.curvature?DRIFT_MAX*Math.sin(truck.angle%Math.PI)**2:0;
  // Yaw about the rear axle, preserving its road path through the powerslide.
  truck.x+=REAR_AXLE*(Math.cos(truck.angle)-Math.cos(truck.angle+truck.drift));
  truck.z+=REAR_AXLE*(Math.sin(truck.angle+truck.drift)-Math.sin(truck.angle));
  truck.distance+=Math.floor(seconds/DURATION)*(loadedLength+RETURN_LENGTH);
  const {x,y,z,angle}=cargo;
  return{t,truck,cargo:{x,y,z,angle},source:{...source,reach:sourceReach},receiver:{...receiver,reach:receiverReach},sourceOpen,receiverOpen,sideGate,phase};
}
export function truckSteering(truck,x,side){
  if(x<0)return 0;
  const normal=Math.atan2(truck.curvature*(x-REAR_AXLE),1+truck.curvature*side*.88);
  return normal*(1-.95*truck.drift/DRIFT_MAX)-truck.drift*.9;
}
export function wheelTravel(seconds,x=0,z=0){
  const t=cycle(seconds),d=RETURN_LENGTH*ramp('return',t);
  const scale=Math.hypot(1+z/TURN_RADIUS,(x-REAR_AXLE)/TURN_RADIUS);
  let remainder=d,partial=0;
  for(const [length,factor] of [[firstLength,1],[arcLength,scale],[rearLength,1],[arcLength,scale],[lastLength,1]]){
    const travel=Math.min(length,Math.max(0,remainder));partial+=travel*factor;remainder-=length;
  }
  const total=loadedLength+firstLength+rearLength+lastLength+2*arcLength*scale;
  return Math.floor(seconds/DURATION)*total+loadedLength*ramp('drive',t)+(t>=TIMING.return[0]?partial:0);
}
