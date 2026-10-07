const TAU=Math.PI*2,STEP=1/60;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const angleDifference=(a,b)=>Math.atan2(Math.sin(b-a),Math.cos(b-a));
const lerp=(a,b,t)=>a+(b-a)*t;
const obstacles=[[-8.9,-4.4,-2.3,.71],[2.3,-4.4,8.9,.71],[-1.35,-1.5,1.35,.45],[-6.8,.6,-4.4,2.2],[4.4,.6,6.8,2.2]];
const nodes=[[-3.5,1.4],[-2.9,1.4],[-1.8,1.4],[0,1.4],[1.8,1.4],[2.9,1.4],[3.5,1.4],[1.85,.55],[1.85,-.6],[1.85,-1.8],[1.85,-2.25],[1.55,-2.65],[0,-2.65],[-1.55,-2.65],[-1.85,-2.25],[-1.85,-1.8],[-1.85,-.6],[-1.85,.55]];
const links=nodes.map(()=>[]);
for(let i=0;i<6;i++){links[i].push(i+1);links[i+1].push(i);}
// The narrow passages have one-way circulation; pets can pass in two front lanes.
for(const [a,b] of [[4,7],[7,8],[8,9],[9,10],[10,11],[11,12],[12,13],[13,14],[14,15],[15,16],[16,17],[17,2]])links[a].push(b);
function pointSegment(p,a,b){const x=b[0]-a[0],z=b[1]-a[1],t=clamp(((p[0]-a[0])*x+(p[1]-a[1])*z)/(x*x+z*z||1),0,1);return Math.hypot(p[0]-a[0]-t*x,p[1]-a[1]-t*z);}
function segmentDistance(a,b,c,d){
  const cross=(p,q,r)=>(q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]);
  const x=cross(a,b,c),y=cross(a,b,d),z=cross(c,d,a),w=cross(c,d,b);
  if(x*y<0&&z*w<0)return 0;
  return Math.min(pointSegment(a,c,d),pointSegment(b,c,d),pointSegment(c,a,b),pointSegment(d,a,b));
}
function capsule(p){const c=Math.cos(p.yaw),s=Math.sin(p.yaw);return [[p.x-.41*c,p.z+.41*s],[p.x+.35*c,p.z-.35*s]];}
export function petsClear(a,b){const [a0,a1]=capsule(a),[b0,b1]=capsule(b);return segmentDistance(a0,a1,b0,b1)>.36;}
export function petCanStand(p){
  const [a,b]=capsule(p);
  if([a,b].some(v=>Math.hypot(Math.max(0,Math.abs(v[0])-7.4),v[1]+.8)>2.82))return false;
  for(const [x0,z0,x1,z1] of obstacles){
    if([a,b].some(v=>v[0]>=x0&&v[0]<=x1&&v[1]>=z0&&v[1]<=z1))return false;
    const corners=[[x0,z0],[x1,z0],[x1,z1],[x0,z1]];
    for(let i=0;i<4;i++)if(segmentDistance(a,b,corners[i],corners[(i+1)%4])<.18)return false;
  }
  return true;
}
function nodePoint(i,cat){return [nodes[i][0],i<7?(cat?1.6:1.4):nodes[i][1]];}
function nearest(p,cat){let best=0,distance=Infinity;nodes.forEach((_,i)=>{const n=nodePoint(i,cat),d=Math.hypot(n[0]-p.x,n[1]-p.z);if(d<distance){distance=d;best=i;}});return best;}
function route(from,to){
  const queue=[from],previous=new Map([[from,-1]]);
  for(let i=0;i<queue.length;i++){const n=queue[i];if(n===to)break;for(const next of links[n])if(!previous.has(next)){previous.set(next,n);queue.push(next);}}
  const path=[to];while(path[0]!==from)path.unshift(previous.get(path[0]));return path;
}
export function createGardenLife(seed=47){
  let randomState=seed>>>0,time=0,previousTime=0,nextPlay=6,corridorOwner=-1,turnOwner=-1;
  const random=()=>{randomState=(Math.imul(randomState,1664525)+1013904223)>>>0;return randomState/4294967296;};
  const make=(cat)=>({cat,x:cat?.65:-.65,z:cat?1.6:1.4,yaw:cat?Math.PI:0,speed:0,vx:0,vz:0,travel:0,turnTravel:0,turn:0,head:0,mood:cat?'watch':'sniff',until:cat?3:1.5,path:[],goal:3,blocked:0,lastWaypoint:0,cruise:.5,actionStart:0,nextPotty:cat?42:22,pottySide:-1,task:null,points:{},yieldUntil:0,yieldX:0,yieldZ:0});
  let actors=[make(false),make(true)],previous=actors.map(p=>({...p}));
  function stop(p,mood){p.path=[];if(mood!=='potty-align')p.task=null;p.mood=mood;p.until=mood==='potty-align'?Infinity:time+1.8+random()*(p.cat?5:3);p.actionStart=time;}
  function choose(p,other){
    if(random()<.22){stop(p,p.cat?'watch':'sniff');return;}
    const start=nearest(p,p.cat);
    let goal=Math.floor(random()*7);
    const potty=time>=p.nextPotty;
    const explore=!potty&&start<7&&random()<.35;
    if(potty){goal=random()<.5?1:5;p.task='potty';p.pottySide=goal===1?-1:1;}else p.task=null;
    if(!potty&&!p.cat&&other.path.length&&random()<.4){goal=other.goal;p.mood='follow';}else p.mood='walk';
    if(goal===start&&!potty)goal=(goal+3)%7;
    p.goal=goal;p.points={};p.lastWaypoint=time;
    p.points[goal]=[nodes[goal][0]+(potty?0:(random()-.5)*.6),potty?1.4:1.36+random()*.24];
    if(explore){
      p.points[18]=[.65+random()*.6,-2.15-random()*.85];p.points[19]=[(random()-.5)*1.1,-2.15-random()*.9];p.points[20]=[-.65-random()*.6,-2.15-random()*.85];
      const reverse=random()<.5,entry=reverse?2:4,exit=reverse?4:2;
      const circuit=reverse?[17,16,15,14,13,20,19,18,11,10,9,8,7]:[7,8,9,10,11,18,19,20,13,14,15,16,17];
      p.path=[...route(start,entry),...circuit,...route(exit,goal)];
    }else p.path=route(start,goal);p.cruise=p.cat?.24+random()*.08:.25+random()*.08;p.blocked=0;
    if(p.path.length>1&&p.path[0]<7&&p.path[1]<7)p.path.shift();
    if(p.mood==='follow')p.cruise=.35;
  }
  function point(p,i){return p.points[i]??nodePoint(i,p.cat);}
  function assignYield(p,other){
    if(p.mood==='potty')return false;
    if(p.yieldUntil>time)return true;
    const away=p.x>other.x?1:-1;
    const candidates=[.8,.56,.36,.2].flatMap(distance=>[[away*distance,1.4-p.z],[Math.cos(p.yaw)*distance,1.4-p.z]]);
    for(const [dx,dz] of candidates){
      if(Math.hypot(dx,dz)<.04||(other.z>.3&&Math.hypot(p.x+dx-other.x,p.z+dz-other.z)<Math.hypot(p.x-other.x,p.z-other.z)+.12))continue;
      const heading=Math.atan2(-dz,dx),delta=angleDifference(p.yaw,heading);
      const clear=[.2,.4,.6,1].every(t=>{
        const turning={...p,yaw:p.yaw+delta*t};
        const moving={...p,x:p.x+dx*t,z:p.z+dz*t,yaw:heading};
        return petCanStand(turning)&&petsClear(turning,other)&&petCanStand(moving)&&petsClear(moving,other);
      });
      if(clear&&Math.abs(p.x+dx)<3.78){p.yieldUntil=time+4;p.yieldX=p.x+dx;p.yieldZ=p.z+dz;return true;}
    }
    return false;
  }
  function step(){
    previous=actors.map(p=>({...p}));previousTime=time;time+=STEP;
    if(time>nextPlay&&Math.hypot(actors[0].x-actors[1].x,actors[0].z-actors[1].z)<1.15&&!actors.some(p=>p.path.length||p.mood.startsWith('potty')||nearest(p,p.cat)>=7)){
      actors.forEach(p=>{stop(p,'play');p.until=time+3.4;});nextPlay=time+18+random()*25;
    }
    actors.forEach((p,index)=>{
      const other=actors[1-index];
      if(corridorOwner===index&&nearest(p,p.cat)<7&&p.z>.9)corridorOwner=-1;
      if(p.mood==='potty-align'&&Math.hypot(p.x-point(p,p.goal)[0],p.z-point(p,p.goal)[1])>.18){p.path=[p.goal];p.task='potty';p.mood='walk';}
      if((p.path.length||p.mood==='potty-align')&&nearest(p,p.cat)<7&&time-p.lastWaypoint>10){if(p.task==='potty')p.nextPotty=time+15+random()*15;stop(p,p.cat?'watch':'sniff');if(turnOwner===index)turnOwner=-1;p.yieldUntil=0;}
      if(!p.path.length&&time>=p.until)choose(p,other);
      let desiredYaw=p.yaw,desiredSpeed=0;
      if(p.path.length){
        let target=point(p,p.path[0]),distance=Math.hypot(target[0]-p.x,target[1]-p.z);
        if(distance<.15){p.lastWaypoint=time;p.path.shift();if(!p.path.length)stop(p,p.task==='potty'?'potty-align':random()<.55?'sniff':'watch');else{target=point(p,p.path[0]);distance=Math.hypot(target[0]-p.x,target[1]-p.z);}}
        if(p.path.length){
          desiredYaw=Math.atan2(p.z-target[1],target[0]-p.x);
          const turn=Math.abs(angleDifference(p.yaw,desiredYaw));
          desiredSpeed=p.cruise*Math.max(0,Math.cos(turn))**2*Math.min(1,distance/(p.path.length===1?.55:.25));
          if((p.path[0]===7||p.path[0]===17)&&p.z>.9){if(corridorOwner>=0&&corridorOwner!==index){desiredSpeed=0;if(Math.hypot(p.x-other.x,p.z-other.z)<1.8)assignYield(p,other);}else corridorOwner=index;}
        }
      }else if(p.mood==='potty-align'||p.mood==='potty'){
        desiredYaw=p.pottySide<0?0:Math.PI;
        if(p.mood==='potty-align'&&Math.abs(angleDifference(p.yaw,desiredYaw))<.06&&p.speed<.01){p.mood='potty';p.actionStart=time;p.until=time+5.4;p.nextPotty=time+55+random()*75;p.task=null;p.yieldUntil=0;}
      }else if(p.mood==='play')desiredYaw=Math.atan2(p.z-other.z,other.x-p.x);
      else if(p.mood==='watch')desiredYaw=p.yaw+Math.sin(time*.65+index)*.006;
      // A pet waits inside the passage while its exit is cleared forward.
      if(p.z<1&&p.z>-.8&&-Math.sin(desiredYaw)>.5&&other.z>1.2&&Math.abs(p.x-other.x)<1.2){
        desiredSpeed=0;desiredYaw=p.yaw;assignYield(other,p);
      }
      if(p.z>1.2&&other.z<1.12&&other.z>-.8&&nearest(other,other.cat)>=7&&other.vz>=0){
        if(Math.cos(desiredYaw)*(other.x-p.x)>0&&Math.abs(p.x-other.x)<1.65){desiredSpeed=0;desiredYaw=p.yaw;}
      }
      const rawTurn=angleDifference(p.yaw,desiredYaw),gap=Math.hypot(p.x-other.x,p.z-other.z);
      if(turnOwner===index&&Math.abs(rawTurn)<.15&&p.yieldUntil<=time)turnOwner=-1;
      if(gap<1.9&&nearest(p,p.cat)<7&&nearest(other,other.cat)<7&&p.yieldUntil<=time&&other.yieldUntil<=time){
        const approaching=(p.vx-other.vx)*(other.x-p.x)+(p.vz-other.vz)*(other.z-p.z)>.02;
        if(approaching&&assignYield(p,other))turnOwner=index;
      }
      if(time>=p.yieldUntil&&Math.abs(rawTurn)>.5&&nearest(p,p.cat)<7){
        if(turnOwner<0)turnOwner=index;
        if(turnOwner===index&&gap<1.25){
          const otherHasPriority=nearest(other,other.cat)>=7||other.mood.startsWith('potty');
          if(otherHasPriority||!assignYield(other,p))assignYield(p,other);
          desiredYaw=p.yaw;desiredSpeed=0;
        }
      }
      if(((turnOwner>=0&&turnOwner!==index&&gap<2)||other.yieldUntil>time&&gap<2)&&time>=p.yieldUntil){desiredYaw=p.yaw;desiredSpeed=0;}
      if(time<p.yieldUntil&&Math.hypot(p.yieldX-p.x,p.yieldZ-p.z)<.04)p.yieldUntil=0;
      const yielding=time<p.yieldUntil;
      if(yielding){
        desiredYaw=Math.atan2(p.z-p.yieldZ,p.yieldX-p.x);
        const error=Math.abs(angleDifference(p.yaw,desiredYaw));
        desiredSpeed=error>.55?0:.3*Math.min(1,Math.hypot(p.yieldX-p.x,p.yieldZ-p.z)/.18);
      }
      const headingError=angleDifference(p.yaw,desiredYaw);
      const targetTurn=clamp(headingError*2.8,-.9,.9);
      const turn=p.turn+clamp(targetTurn-p.turn,-4*STEP,4*STEP);
      const yaw=p.yaw+turn*STEP;
      p.head+=clamp(clamp(headingError*.45,-.42,.42)-p.head,-1.6*STEP,1.6*STEP);
      const speed=p.speed+clamp(desiredSpeed-p.speed,-1.0*STEP,.7*STEP);
      // Travel follows the facing direction, including yielding: never backpedal.
      const candidate={...p,x:p.x+Math.cos(yaw)*speed*STEP,z:p.z-Math.sin(yaw)*speed*STEP,yaw};
      const wantsMotion=desiredSpeed>.01||yielding||Math.abs(headingError)>.08;
      const sweptClear=end=>[.25,.5,.75,1].every(a=>{const pose={x:lerp(p.x,end.x,a),z:lerp(p.z,end.z,a),yaw:p.yaw+angleDifference(p.yaw,end.yaw)*a};return petCanStand(pose)&&petsClear(pose,other);});
      const frontLane=nearest(p,p.cat)<7&&p.path[0]!==7&&p.path[0]!==17&&p.z>=1.34&&p.z<=1.60;
      if(frontLane)candidate.z=clamp(candidate.z,1.34,1.60);
      if(sweptClear(candidate)){
        const distance=Math.hypot(candidate.x-p.x,candidate.z-p.z);p.travel+=distance;p.turnTravel+=Math.abs(angleDifference(p.yaw,yaw))*.35;p.turn=angleDifference(p.yaw,yaw)/STEP;p.vx=(candidate.x-p.x)/STEP;p.vz=(candidate.z-p.z)/STEP;p.x=candidate.x;p.z=candidate.z;p.yaw=yaw;p.speed=speed;p.blocked=distance>.001||Math.abs(p.turn)>.02||!wantsMotion?0:p.blocked+STEP;
      }else{
        p.speed=0;p.vx=0;p.vz=0;p.turn=0;p.blocked=wantsMotion?p.blocked+STEP:0;
        const turning={...p,yaw};if(sweptClear(turning)){p.turnTravel+=Math.abs(angleDifference(p.yaw,yaw))*.35;p.turn=angleDifference(p.yaw,yaw)/STEP;p.yaw=yaw;}
        if(p.blocked>.8&&nearest(p,p.cat)<7&&!yielding){if(!assignYield(p,other))assignYield(other,p);turnOwner=-1;}
        if(p.blocked>1.7&&nearest(p,p.cat)<7){stop(p,p.cat?'watch':'sniff');p.blocked=0;}
      }
    });
  }
  function pose(p,old,alpha,seconds){
    const vx=lerp(old.vx,p.vx,alpha),vz=lerp(old.vz,p.vz,alpha),speed=Math.hypot(vx,vz),turn=lerp(old.turn,p.turn,alpha),gait=clamp(speed/.12+Math.abs(turn)*.35,0,1),stride=(lerp(old.travel,p.travel,alpha)+lerp(old.turnTravel,p.turnTravel,alpha))/.2;
    const elapsed=seconds-p.actionStart,play=p.mood==='play',sniff=p.mood==='sniff';
    return {x:lerp(old.x,p.x,alpha),z:lerp(old.z,p.z,alpha),yaw:old.yaw+angleDifference(old.yaw,p.yaw)*alpha,stride,gait,backward:false,distance:lerp(old.travel,p.travel,alpha),speed,vx,vz,turn,bob:gait*.005*(1-Math.cos(stride*TAU*2)),bow:!p.cat&&(play||sniff)?Math.sin(Math.min(Math.PI,Math.max(0,elapsed)*.9))*(play?1:.45):0,paw:p.cat&&play?Math.max(0,Math.sin(elapsed*4))*.055:0,tail:Math.sin(seconds*(p.cat?1.1:5.2))*(p.cat?.12:.3),look:lerp(old.head,p.head,alpha)+(p.mood==='watch'?Math.sin(seconds*.7)*.16:0),mood:p.mood,pottySide:p.pottySide,actionTime:Math.max(0,seconds-p.actionStart)};
  }
  return {sample(seconds){
    if(seconds<previousTime){randomState=seed>>>0;time=0;previousTime=0;nextPlay=6;corridorOwner=-1;turnOwner=-1;actors=[make(false),make(true)];previous=actors.map(p=>({...p}));}
    while(time<seconds)step();
    const alpha=clamp((seconds-previousTime)/STEP,0,1);
    return{dog:pose(actors[0],previous[0],alpha,seconds),cat:pose(actors[1],previous[1],alpha,seconds)};
  }};
}
const defaultLife=createGardenLife();
export const sampleGardenLife=seconds=>defaultLife.sample(seconds);
export function sampleButterfly(seconds,index){
  const p=index*2.2,t=seconds,dx=.85*.53*Math.cos(t*.53+p),dz=.35*.74*Math.cos(t*.74+p);
  return{x:.1+.85*Math.sin(t*.53+p),z:-.6+.35*Math.sin(t*.74+p),y:.95+.24*Math.sin(t*.9+p)+.06*Math.sin(t*2.2+p),yaw:Math.atan2(-dx,-dz),roll:.12*Math.sin(t*.9+p),flap:.35+Math.sin(t*22+p)*.85,size:.28-index*.025};
}
