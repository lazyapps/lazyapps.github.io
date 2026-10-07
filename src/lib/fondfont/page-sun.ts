import * as THREE from 'three';

type Rect={left:number;top:number;width:number;height:number};

// The page sun defines a bearing on the projected ground. Elevate that bearing
// after unprojection so shadows extend from object bases away from the icon.
export function pageSunPosition(camera:THREE.OrthographicCamera,canvas:Rect,sun:Rect,height=18){
  const x=sun.left+sun.width/2,y=sun.top+sun.height/2;
  const origin=new THREE.Vector3((x-canvas.left)/canvas.width*2-1,1-(y-canvas.top)/canvas.height*2,-1).unproject(camera);
  const direction=camera.getWorldDirection(new THREE.Vector3());
  origin.addScaledVector(direction,-origin.y/direction.y);
  origin.y=height;
  return origin;
}
