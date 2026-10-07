import * as THREE from 'three';

/** Keep the illustrated door and its native interior in the same orthographic sight plane. */
export function installLoadingBayVisibility(model:THREE.Object3D,camera:THREE.Camera){
  const sight=camera.getWorldDirection(new THREE.Vector3());
  const upY=-sight.z,upZ=sight.y;
  const portals=['Foundry','Warehouse'].map(name=>{
    const building=model.getObjectByName(name)!;
    const [left,right,height,z]=building.userData.loading_bay_portal as number[];
    return {building,left:left+building.position.x,right:right+building.position.x,height,z};
  });
  const fragment=portals.map(p=>`if(vBayWorld.x>${p.left.toFixed(8)} && vBayWorld.x<${p.right.toFixed(8)} && vBayWorld.z<${p.z.toFixed(8)} && ${upY.toFixed(8)}*vBayWorld.y+${upZ.toFixed(8)}*vBayWorld.z>${(upY*p.height+upZ*p.z).toFixed(8)})discard;`).join('\n');
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
