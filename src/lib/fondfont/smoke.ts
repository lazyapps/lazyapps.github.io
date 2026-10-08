import * as THREE from 'three';
import { WIND_X } from './nature.mjs';

// A three-dimensional density field, ray-marched through a small chimney volume.
export function createChimneySmoke(origin:THREE.Vector3){
  const geometry=new THREE.BoxGeometry(2.4,3.4,1.4);
  geometry.translate(.7,1.7,0);
  const uniforms={uTime:{value:0},uWind:{value:WIND_X}};
  const material=new THREE.ShaderMaterial({
    uniforms,transparent:true,depthWrite:false,toneMapped:false,
    vertexShader:`varying vec3 vLocal;varying vec3 vWorld;void main(){vLocal=position;vWorld=(modelMatrix*vec4(position,1.0)).xyz;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
    fragmentShader:`
      precision highp float;
      varying vec3 vLocal;
      varying vec3 vWorld;
      uniform float uTime,uWind;
      float hash(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
      float noise(vec3 p){
        vec3 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
        return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),
                   mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);
      }
      float density(vec3 p){
        if(p.y<0.0||p.y>3.35)return 0.0;
        float bend=uWind*(.13*p.y+.105*p.y*p.y);
        float curl=.07*p.y*sin(p.y*2.7-uTime*.55);
        float radius=.08+.15*p.y;
        float d=length(vec2(p.x-bend-curl,p.z-.055*p.y*sin(p.y*2.1-uTime*.37)))/radius;
        vec3 flow=p*4.0-vec3(uTime*.13,uTime*.6,0);
        float grain=.65*noise(flow)+.25*noise(flow*2.07)+.10*noise(flow*4.13);
        float edge=1.0-smoothstep(.3,1.1,d+(grain-.5)*.9);
        return edge*(.1+.9*smoothstep(.25,.7,grain))*smoothstep(0.0,.16,p.y)*(1.0-smoothstep(.7,3.1,p.y));
      }
      void main(){
        // Per-pixel line of sight (the volume is translated, never rotated).
        vec3 ray=normalize(vWorld-cameraPosition),p=vLocal+ray*.001;
        float alpha=0.0,light=0.0;
        for(int i=0;i<48;i++){
          if(p.x<-.5||p.x>1.9||p.y<0.0||p.y>3.4||abs(p.z)>.7)break;
        float a=density(p)*.15;
          light+=(1.0-alpha)*a*(.83+.1*noise(p*2.0));
          alpha+=(1.0-alpha)*a;
          p+=ray*.065;
        }
        if(alpha<.001)discard;
        gl_FragColor=vec4(vec3(.18+.04*light/max(alpha,.001)),alpha*.85);
      }`,
  });
  const mesh=new THREE.Mesh(geometry,material);mesh.position.copy(origin);
  mesh.name='Volumetric chimney smoke';mesh.frustumCulled=false;
  return{mesh,geometry,material,update(seconds:number){uniforms.uTime.value=seconds;}};
}
