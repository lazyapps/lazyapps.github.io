import {WIND_X,leafArrival,sampleLeaf,leafGround} from './nature.mjs';
import {sampleMotion,DECK} from './motion.mjs';

const STEP=1/40;
const random=seed=>{const value=Math.sin(seed*127.1+311.7)*43758.5453;return value-Math.floor(value);};
export const LEAF_DECK=DECK+.015;
const localPoint=(p,truck)=>{
  const a=truck.angle+truck.drift,c=Math.cos(a),s=Math.sin(a),dx=p.x-truck.x,dz=p.z-truck.z;
  return {x:dx*c-dz*s,z:dx*s+dz*c};
};
const restsOnDeck=(p,motion)=>{
  const q=localPoint(p,motion.truck);
  // Keep the whole leaf clear of the stakes, rails and cab. Loaded type trays
  // occupy the middle of the deck; leaves can settle along its exposed edges.
  if(q.x< -2.21||q.x>.58||Math.abs(q.z)>.73)return null;
  const load=motion.cargo;
  if(load&&load.y>=DECK-.03){
    const a=load.angle??0,c=Math.cos(a),s=Math.sin(a),dx=p.x-load.x,dz=p.z-load.z;
    if(Math.abs(dx*c-dz*s)<1.18&&Math.abs(dx*s+dz*c)<.68)return null;
  }
  return q;
};
const placeOnDeck=(leaf,truck,t)=>{
  const a=truck.angle+truck.drift,c=Math.cos(a),s=Math.sin(a),q=leaf.deck;
  const f=Math.min(1,Math.max(0,(t-q.time)/.22)),settle=f*f*(3-2*f);
  leaf.x=truck.x+q.x*c+q.z*s;leaf.z=truck.z-q.x*s+q.z*c;leaf.y=LEAF_DECK;
  leaf.yaw=q.yaw+a;leaf.pitch=q.pitch+(-Math.PI/2-q.pitch)*settle;leaf.roll=q.roll*(1-settle);
};
const wheels=truck=>{
  const a=truck.angle+truck.drift,c=Math.cos(a),s=Math.sin(a);
  return [-1.82,-.75,1.62].flatMap(x=>[-.88,.88].map(z=>({x:truck.x+x*c+z*s,z:truck.z-x*s+z*c})));
};
const segmentDistance=(x,z,a,b)=>{
  const dx=b.x-a.x,dz=b.z-a.z,l=dx*dx+dz*dz;
  const p=l?Math.max(0,Math.min(1,((x-a.x)*dx+(z-a.z)*dz)/l)):0;
  const px=a.x+p*dx,pz=a.z+p*dz;
  return {distance:Math.hypot(x-px,z-pz),x:px,z:pz};
};

// Fixed steps preserve the same accumulated leaves on fast, slow and frozen previews.
export function createLeafLitter({truckAt=sampleMotion,leafAt=sampleLeaf}={}){
  let time=0,leaves=[],next=[],kickCount=0,skyLine=10,captured=new Set();
  const persistent=(p,arrival)=>({...p,id:arrival.id,index:arrival.index,cycle:arrival.cycle,vx:0,vy:0,vz:0,spin:0,lastKick:-Infinity,airborne:false,kicks:0});
  function reset(){
    time=0;leaves=[];kickCount=0;captured=new Set();
    next=Array.from({length:6},(_,i)=>{
      let cycle=0;while(leafArrival(i,cycle).time<0)cycle++;
      return leafArrival(i,cycle);
    });
  }
  reset();
  function step(t,dt){
    for(let i=0;i<6;i++){
      const p=leafAt(t,i,skyLine),before=leafAt(t-dt,i,skyLine);
      if(p.id!==before.id||captured.has(p.id)||before.y<=LEAF_DECK||p.y>LEAF_DECK)continue;
      const f=(before.y-LEAF_DECK)/(before.y-p.y),hitTime=t-dt+dt*f;
      const hit={...p,x:before.x+(p.x-before.x)*f,z:before.z+(p.z-before.z)*f,y:LEAF_DECK};
      const pose=truckAt(hitTime),local=restsOnDeck(hit,pose);
      if(!local)continue;
      const leaf=persistent(hit,p);
      leaf.deck={...local,yaw:hit.yaw-pose.truck.angle-pose.truck.drift,pitch:hit.pitch,roll:hit.roll,time:hitTime};
      captured.add(p.id);leaves.push(leaf);
    }
    for(let i=0;i<6;i++)while(next[i].time<=t){
      const arrival=next[i],p=leafAt(arrival.time+1e-8,i,skyLine);
      if(!captured.has(arrival.id))leaves.push({...persistent(p,arrival),pitch:-Math.PI/2,roll:0});
      next[i]=leafArrival(i,arrival.cycle+1);
    }
    const current=truckAt(t).truck,previous=truckAt(Math.max(0,t-dt)).truck;
    const speed=Math.hypot(current.x-previous.x,current.z-previous.z)/dt;
    const now=wheels(current),before=wheels(previous);
    for(const leaf of leaves){
      if(leaf.deck){
        placeOnDeck(leaf,current,t);
        continue;
      }
      if(leaf.airborne){
        leaf.vy-=3.8*dt;leaf.vx*=Math.exp(-1.3*dt);leaf.vz*=Math.exp(-1.3*dt);
        leaf.x+=leaf.vx*dt;leaf.z+=leaf.vz*dt;leaf.y+=leaf.vy*dt;
        leaf.yaw+=leaf.spin*.65*dt;leaf.pitch+=leaf.spin*dt;leaf.roll=.22*Math.sin((t-leaf.lastKick)*7);
        const floor=leafGround(leaf.x,leaf.z);
        if(leaf.y<=floor){
          leaf.y=floor;leaf.airborne=false;leaf.pitch=-Math.PI/2;leaf.roll=0;
          leaf.lastDisplacement=Math.hypot(leaf.x-leaf.kickX,leaf.z-leaf.kickZ);
        }
      }
      if(leaf.airborne||t-leaf.lastKick<1.4||speed<.3)continue;
      let nearest={distance:Infinity,x:0,z:0};
      for(let i=0;i<now.length;i++){
        const hit=segmentDistance(leaf.x,leaf.z,before[i],now[i]);
        if(hit.distance<nearest.distance)nearest=hit;
      }
      if(nearest.distance>.85)continue;
      const dx=leaf.x-nearest.x,dz=leaf.z-nearest.z,d=Math.max(.1,Math.hypot(dx,dz));
      const strength=Math.min(1,speed/3.5)*(1-nearest.distance/1.15);
      const seed=leaf.index*131+leaf.cycle*17+leaf.kicks*97;
      const direction=Math.atan2(dz/d,dx/d)+(random(seed+1)-.5)*2;
      const gust=(1.6+random(seed+2)*1.8)*(.7+strength*.3);
      leaf.vx=Math.cos(direction)*gust+WIND_X*.35;
      leaf.vz=Math.sin(direction)*gust;
      leaf.vy=.95+strength*.6+random(seed+3)*.2;
      leaf.spin=(random(seed+4)<.5?-1:1)*(3+random(seed+5)*3);
      leaf.kickX=leaf.x;leaf.kickZ=leaf.z;
      leaf.airborne=true;leaf.lastKick=t;leaf.kicks++;kickCount++;
    }
  }
  return {sample(seconds,spawnLine=10){
    skyLine=spawnLine;
    const target=Math.max(0,seconds),tick=Math.floor((target+1e-8)/STEP);
    if(target<time-1e-7)reset();
    while(Math.round(time/STEP)<tick){time=(Math.round(time/STEP)+1)*STEP;step(time,STEP);}
    const truck=truckAt(target).truck;
    for(const leaf of leaves)if(leaf.deck)placeOnDeck(leaf,truck,target);
    return {leaves,kickCount,captured,deckCount:leaves.filter(p=>p.deck).length};
  }};
}
