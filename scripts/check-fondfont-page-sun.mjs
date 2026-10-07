import assert from 'node:assert/strict';
import * as THREE from 'three';
import {pageSunPosition} from '../src/lib/fondfont/page-sun.ts';

const scenarios=[[1280,420,112,119,42],[768,330,52,43.4,35.5],[390,180,72,25,32],[1440,420,177,207,42]];
let last;
for(const [width,height,sky,sunX,sunY] of scenarios){
  const span=34,camera=new THREE.OrthographicCamera(-span/2,span/2,span*height/width/2+sky*span/width,-span*height/width/2,.1,100);
  camera.position.set(0,19.25,28.7);camera.lookAt(0,.25,-.8);camera.updateMatrixWorld(true);
  const canvas={left:0,top:2,width,height:height+sky};
  const pixel=p=>{const n=p.clone().project(camera);return new THREE.Vector2((n.x+1)*width/2,canvas.top+(1-n.y)*canvas.height/2);};
  const sun={left:sunX-5,top:sunY-5,width:10,height:10},sunPixel=new THREE.Vector2(sunX,sunY);
  const light=pageSunPosition(camera,canvas,sun),target=new THREE.Vector3();
  const expected=pixel(target).sub(sunPixel).normalize(),away=target.clone().sub(light).normalize();
  assert.ok(!last||light.distanceTo(last)>1e-3,'responsive layouts recompute the world sunlight');last=light;
  for(const top of [new THREE.Vector3(-5.6,3,0),new THREE.Vector3(5.6,3,0),new THREE.Vector3(0,1.5,4),new THREE.Vector3(2,.5,1)]){
    const base=new THREE.Vector3(top.x,0,top.z),shadow=top.clone().addScaledVector(away,-top.y/away.y);
    const extension=pixel(shadow).sub(pixel(base));
    assert.ok(Math.abs(shadow.y)<1e-8,'all rays land on the shared ground');
    assert.ok(extension.x>0&&extension.y>0,`${width}px: a sun above-left must cast ground shadows down-right, got ${extension.toArray()}`);
    assert.ok(extension.clone().normalize().dot(expected)>.999999,'base-to-shadow bearing follows the screen sun, not the top-to-shadow ray');
  }
  const bearing=light.clone();bearing.y=0;
  assert.ok(pixel(bearing).distanceTo(sunPixel)<1e-7,'sun screen position supplies ground-plane bearing');
}
console.log('Page sun: base-to-shadow extensions point down-right, follow the responsive DOM sun bearing, and agree for buildings/vehicles/pets in four layouts.');
