import * as THREE from 'three';
import { rayToPlane } from './campus-camera.ts';

type Rect={left:number;top:number;width:number;height:number};
const ground=new THREE.Plane(new THREE.Vector3(0,1,0),0);

// The page sun defines a bearing on the projected ground. The ray through the icon's
// pixel (perspective or orthographic) meets the ground; elevating that ground point keeps
// shadows extending from object bases away from the icon.
export function pageSunPosition(camera:THREE.Camera,canvas:Rect,sun:Rect,height=18){
  const x=sun.left+sun.width/2,y=sun.top+sun.height/2;
  const origin=rayToPlane(camera,(x-canvas.left)/canvas.width*2-1,1-(y-canvas.top)/canvas.height*2,ground);
  origin.y=height;
  return origin;
}
