import {ROAD,TURN_RADIUS,TURN_X} from './motion.mjs';
const random=seed=>{const x=Math.sin(seed*127.1+311.7)*43758.5453;return x-Math.floor(x);};
export const WIND_X=1;
const bands=[[-10,4.7],[-7.7,3.1],[-1.5,4.1],[3,5.8],[3.5,3.1],[10,-2.7]];
const pitch=Math.atan2(19,29.5),upY=Math.cos(pitch),upZ=-Math.sin(pitch);
const fade=(a,b,t)=>{const p=Math.max(0,Math.min(1,(t-a)/(b-a)));return p*p*(3-2*p);};
export const LEAF_FLOOR=.008;
export function leafGround(x,z){
  const radius=Math.hypot(Math.max(0,Math.abs(x)-TURN_X),z-(ROAD-TURN_RADIUS));
  const distance=Math.abs(radius-TURN_RADIUS);
  return LEAF_FLOOR+(distance<=1.8?.032:distance<=2.1?.048:0);
}
export function leafArrival(index,cycle){
  const period=25+random(index+1)*8,offset=random(index+9)*period;
  const seed=index*31+cycle*17,life=15+random(seed+3)*4;
  return {index,cycle,id:`${index}:${cycle}`,time:cycle*period-offset+life,life};
}

// Ambient wind uses elapsed time, independently of the truck's repeating trip.
export function sampleLeaf(seconds,index,skyLine=10){
  const period=25+random(index+1)*8,offset=random(index+9)*period;
  const cycle=Math.floor((seconds+offset)/period),age=seconds+offset-cycle*period;
  const seed=index*31+cycle*17,life=15+random(seed+3)*4,p=Math.min(1,age/life);
  const fallingAge=Math.min(age,life),settle=fade(.86,1,p);
  const [x,z]=bands[index],phase=random(seed+4)*Math.PI*2;
  const depth=z+(random(seed+8)-.5)*.6+.8*p+Math.sin(fallingAge*.6+phase)*.13;
  const across=x+(random(seed+5)-.5)*1.2+WIND_X*(2.5+random(seed+6)*1.5)*p+Math.sin(fallingAge*.7+phase)*.16;
  const floor=leafGround(across,depth);
  return{
    id:`${index}:${cycle}`,index,cycle,
    x:across,
    y:floor+(Math.max(floor,(skyLine-upZ*depth)/upY)-floor)*(1-p),
    z:depth,
    pitch:(.9+Math.sin(fallingAge*.9+phase)*.45)*(1-settle)-Math.PI/2*settle,
    yaw:phase+fallingAge*(.25+random(seed+10)*.15),
    roll:(phase*.5+Math.sin(fallingAge*.7+phase)*.45)*(1-settle),
    size:.38+random(seed+11)*.16,
    opacity:age<life?fade(.004,.028,p):0,
  };
}
