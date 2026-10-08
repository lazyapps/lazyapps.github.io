import * as THREE from 'three';

/**
 * Interior bays (and vehicles inside them) are drawn only where the line of sight from the
 * lens passes through the door opening. Each fragment behind the door plane traces its
 * own ray back to the camera, so the clip is exact for a perspective lens.
 */
export function installLoadingBayVisibility(model:THREE.Object3D){
  const portals=['Foundry','Warehouse'].map(name=>{
    const building=model.getObjectByName(name)!;
    const [left,right,height,z]=building.userData.loading_bay_portal as number[];
    return {building,left:left+building.position.x,right:right+building.position.x,height,z};
  });
  const fragment=portals.map(p=>{
    const [l,r,h,z]=[p.left,p.right,p.height,p.z].map(v=>v.toFixed(8));
    return `if(vBayWorld.x>${l} && vBayWorld.x<${r} && vBayWorld.z<${z}){
      float bayT=(${z}-cameraPosition.z)/(vBayWorld.z-cameraPosition.z);
      vec3 bayDoor=cameraPosition+bayT*(vBayWorld-cameraPosition);
      if(bayDoor.y>${h} || bayDoor.x<${l} || bayDoor.x>${r})discard;
    }`;
  }).join('\n');
  const materials:THREE.Material[]=[];
  const apply=(o:THREE.Object3D)=>{
    if(!(o instanceof THREE.Mesh))return;
    const copies=(Array.isArray(o.material)?o.material:[o.material]).map(source=>{
      const material=source.clone();materials.push(material);
      material.onBeforeCompile=shader=>{
        shader.vertexShader='varying vec3 vBayWorld;\n'+shader.vertexShader;
        shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>','#include <project_vertex>\nvBayWorld=(modelMatrix*vec4(transformed,1.0)).xyz;');
        shader.fragmentShader='varying vec3 vBayWorld;\n'+shader.fragmentShader;
        shader.fragmentShader=shader.fragmentShader.replace('#include <clipping_planes_fragment>','#include <clipping_planes_fragment>\n'+fragment);
      };
      material.customProgramCacheKey=()=>`loading-bays-${fragment}`;
      return material;
    });
    o.material=Array.isArray(o.material)?copies:copies[0];
  };
  for(const {building} of portals)building.traverse(o=>{
    if(o.userData.architecture_role==='interior'||o.userData.architecture_role==='interior-art')apply(o);
  });
  for(const name of ['SourceStacker','ReceiverStacker','Cargo'])model.getObjectByName(name)!.traverse(apply);
  return materials;
}
