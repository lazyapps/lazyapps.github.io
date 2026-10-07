import * as THREE from 'three';

type StackerPose={x:number;z:number;fork:number;angle:number;steer:number;reach:number};
export function createStackerAnimator(model:THREE.Object3D){
  const stackers=new Map(['Source','Receiver'].map(name=>{
    const body=model.getObjectByName(name+'Stacker')!;
    return[name,{body,forks:model.getObjectByName(name+'Forks')!,reach:model.getObjectByName(name+'ForkReach')!,mast:model.getObjectByName(name+'InnerMast')!,piston:model.getObjectByName(name+'Piston')!,wheels:body.children.filter(o=>o.name.startsWith(name+'StackerWheel')).map(wheel=>({wheel,distance:0,previous:null as null|{x:number;z:number;heading:number}}))}] as const;
  }));
  return(name:string,state:StackerPose)=>{
    const {body,forks,reach,mast,piston,wheels}=stackers.get(name)!;
    body.position.x=state.x-1.6*Math.sin(state.angle);
    body.position.z=state.z-1.6*Math.cos(state.angle);body.rotation.y=state.angle;
    forks.position.y=state.fork;
    reach.position.z=.35*state.reach;
    const extension=Math.max(0,state.fork-1.05);
    mast.position.y=extension;piston.position.y=extension*.5;
    body.position.y=0;
    for(const tracker of wheels){
      const {wheel}=tracker;
      const steer=wheel.name.endsWith('_-0.75')?state.steer:0;
      const x=body.position.x+wheel.position.x*Math.cos(state.angle)+wheel.position.z*Math.sin(state.angle);
      const z=body.position.z-wheel.position.x*Math.sin(state.angle)+wheel.position.z*Math.cos(state.angle);
      const heading=state.angle+steer;
      if(tracker.previous){
        const p=tracker.previous;
        const turn=Math.atan2(Math.sin(heading-p.heading),Math.cos(heading-p.heading));
        const mid=p.heading+turn*.5;
        tracker.distance+=(x-p.x)*Math.sin(mid)+(z-p.z)*Math.cos(mid);
      }
      tracker.previous={x,z,heading};
      // Travel is measured at each axle, including its arc through rear steering.
      wheel.rotation.set(tracker.distance/Number(wheel.userData.radius),steer,0,'YXZ');
    }
  };
}
