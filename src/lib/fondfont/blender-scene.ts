import * as THREE from 'three';
import { loadModel } from './model-loader.ts';
import { sampleMotion,wheelTravel,truckSteering,WHEEL_RADIUS,DRIFT_MAX,ROAD,TURN_RADIUS,TURN_X } from './motion.mjs';
import { sampleLeaf } from './nature.mjs';
import { createLeafLitter } from './leaf-litter.mjs';
import { createStackerAnimator } from './stacker-animation';
import { pageSunPosition } from './page-sun';
import { createRoofGlyphs,roofFontFiles } from './roof-glyphs.ts';
import { createCampusCamera,aimCamera,fitLens,rayToPlane,metresPerPixel,roadOutline } from './campus-camera.ts';
import { installLoadingBayVisibility } from './loading-bay';
import { createChimneySmoke } from './smoke';
import { createStudioPetAnimator,loadStudioPets } from './studio-pet-animation';
import { createGardenLife,sampleButterfly } from './garden-life.mjs';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

type SceneCopy={foundry:string;library:string;name:string};
const ROOT='/v/fondfont/blender-v2/';
const CAMPUS='/v/fondfont/blender-v3/';
// Light from the full 1280px poster export; share it through the initial handoff.
const POSTER_SUN=new THREE.Vector3(-17.675282317950803,18,-15.42424746850476);
class CampusAOPass extends GTAOPass{
  constructor(scene:THREE.Scene,camera:THREE.Camera,private alphaSurfaces:THREE.Object3D[]){super(scene,camera);}
  override render(...args:Parameters<GTAOPass['render']>){
    const visibility=this.alphaSurfaces.map(o=>o.visible);this.alphaSurfaces.forEach(o=>o.visible=false);
    try{super.render(...args);}finally{this.alphaSurfaces.forEach((o,i)=>o.visible=visibility[i]);}
  }
}
export async function createBlenderFactory(host:HTMLElement,copy:SceneCopy,signal:AbortSignal){
  const renderer=new THREE.WebGLRenderer({canvas:host.querySelector('canvas')!,alpha:true,antialias:true,powerPreference:'low-power',preserveDrawingBuffer:host.classList.contains('is-export')});
  renderer.setPixelRatio(Math.min(devicePixelRatio,host.clientWidth<600?1.5:2));
  renderer.setClearColor(0xf8f8f6,0);
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.NeutralToneMapping;renderer.toneMappingExposure=1;
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFShadowMap;
  const scene=new THREE.Scene();
  const pmrem=new THREE.PMREMGenerator(renderer),room=new RoomEnvironment();
  const env=pmrem.fromScene(room,.06);scene.environment=env.texture;scene.environmentIntensity=.7;room.dispose();pmrem.dispose();
  scene.add(new THREE.HemisphereLight(0xffffff,0x787280,.72));
  const key=new THREE.DirectionalLight(0xffffff,1.8);key.name='Page sun';key.position.copy(POSTER_SUN);key.target.position.set(0,0,0);key.castShadow=true;scene.add(key.target);
  const shadowSize=host.clientWidth<600?1024:2048;key.shadow.mapSize.set(shadowSize,shadowSize);Object.assign(key.shadow.camera,{left:-17,right:17,top:14,bottom:-14,near:1,far:50});
  key.shadow.radius=3;key.shadow.normalBias=.001;key.shadow.bias=-.00003;scene.add(key);
  const camera=createCampusCamera();
  const cameraTarget=new THREE.Vector3(0,.25,ROAD-TURN_RADIUS);
  aimCamera(camera,cameraTarget,()=>roadOutline());
  const code=host.dataset.locale??'zh-hans';
  const font=new FontFace(`FondFontModel-${code}`,`url(${ROOT}sign-${code}.woff)`,{weight:'100 900'});
  // Every locale has a pool of licensed typefaces for the drifting roof glyphs.
  const roofFonts=roofFontFiles(code).map((file,i)=>new FontFace(`FondFontRoof-${code}-${i}`,`url(${CAMPUS}roof/${file})`));
  let loadFailed=false;
  const [{scene:model},,brandTexture,,dustTexture,leafTexture,petRig]=await Promise.all([
    loadModel(`${CAMPUS}campus-v3.glb`,signal),
    font.load().then(f=>{if(!loadFailed&&!signal.aborted)document.fonts.add(f);}),
    new THREE.TextureLoader().loadAsync(`${ROOT}cab-symbol-paint-v3.svg`),
    Promise.all(roofFonts.map(face=>face.load())).then(faces=>{if(!loadFailed&&!signal.aborted)faces.forEach(f=>document.fonts.add(f));}),
    new THREE.TextureLoader().loadAsync(`${ROOT}drift-dust-v2.webp`),
    new THREE.TextureLoader().loadAsync(`${ROOT}wind-leaf-v2.webp`),
    loadStudioPets(signal),
  ]).catch(error=>{loadFailed=true;env.dispose();renderer.dispose();document.fonts.delete(font);roofFonts.forEach(f=>document.fonts.delete(f));throw error;});
  const geometrySet=new Set<THREE.BufferGeometry>(),materialSet=new Set<THREE.Material>(),textureSet=new Set<THREE.Texture>();
  for(const species of ['Dog','Cat']){
    const old=model.getObjectByName('Pet'+species);if(!old)continue;
    old.traverse(o=>{if(o instanceof THREE.Mesh){geometrySet.add(o.geometry);for(const m of Array.isArray(o.material)?o.material:[o.material])materialSet.add(m);}});
    old.removeFromParent();
  }
  model.add(...petRig.scene.children);
  const petAnimator=createStudioPetAnimator(model);
  const skeletonSet=new Set<THREE.Skeleton>();
  const windTime={value:0};
  model.traverse(o=>{
    if(o.userData.name)o.name=String(o.userData.name);
    if(o instanceof THREE.SkinnedMesh)skeletonSet.add(o.skeleton);
    if(!(o instanceof THREE.Mesh))return;
    let isBotanical=false;
    for(let parent:THREE.Object3D|null=o;parent;parent=parent.parent)if(parent.userData.native_botanical===true)isBotanical=true;
    if(isBotanical)for(const material of Array.isArray(o.material)?o.material:[o.material]){
      material.onBeforeCompile=shader=>{
        shader.uniforms.uWindTime=windTime;
        shader.vertexShader='uniform float uWindTime;\n'+shader.vertexShader;
        shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>',`
          vec3 transformed=vec3(position);
          float rooted=pow(clamp(position.y/.95,0.0,1.0),2.0);
          float phase=position.x*.83+position.z*.47;
          float breeze=.004*sin(uWindTime*.45+phase)+.001*sin(uWindTime*.19+phase*.7);
          float flutter=.0005*sin(uWindTime*.8+position.x*3.7);
          transformed.x+=rooted*(breeze+flutter);
        `);
      };
      material.customProgramCacheKey=()=> 'fondfont-native-botanical-gentle-wind-v2';
    }
    if(!Array.isArray(o.material)&&o.material.name.startsWith('imagegen industrial ')){
      const source=o.material as THREE.MeshStandardMaterial;
      o.material=new THREE.MeshBasicMaterial({name:source.name,map:source.map,alphaTest:.42,side:THREE.DoubleSide,toneMapped:false});
      source.dispose();
    }
    o.castShadow=true;o.receiveShadow=true;geometrySet.add(o.geometry);
    const architectureRole=o.userData.architecture_role;
    if(architectureRole==='artwork'||architectureRole==='interior-art')o.castShadow=false;
    if(architectureRole==='caster'||architectureRole==='occluder'){
      for(const material of Array.isArray(o.material)?o.material:[o.material])materialSet.add(material);
      o.material=new THREE.MeshBasicMaterial({colorWrite:false,depthWrite:false,side:THREE.DoubleSide});
      o.renderOrder=-1;
    }
    if(architectureRole==='interior'||architectureRole==='interior-art'){
      for(const m of Array.isArray(o.material)?o.material:[o.material])m.side=THREE.DoubleSide;
    }
    for(const m of Array.isArray(o.material)?o.material:[o.material]){
      if(m.name.startsWith('imagegen ')&&m.name.endsWith(' alpha')){m.transparent=false;m.alphaTest=.42;m.depthWrite=true;}
      materialSet.add(m);
      for(const value of Object.values(m))if(value instanceof THREE.Texture){textureSet.add(value);value.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());}
    }
  });
  const portalMaterials=installLoadingBayVisibility(model);
  for(const material of portalMaterials)materialSet.add(material);
  scene.add(model);
  // The lens is centred on the projected curb outline (see campus-camera.ts), as the page layout expects.
  model.updateMatrixWorld(true);
  if(import.meta.env.DEV&&new URLSearchParams(location.search).has('petStudy')){
    cameraTarget.set(0,.3,1.4);
    camera.position.set(0,8,13);camera.lookAt(cameraTarget);camera.zoom=5;camera.updateMatrixWorld(true);
  }
  const groundGeometry=new THREE.PlaneGeometry(200,200),groundMaterial=new THREE.ShadowMaterial({opacity:.34});
  const ground=new THREE.Mesh(groundGeometry,groundMaterial);ground.rotation.x=-Math.PI/2;ground.position.y=.001;ground.receiveShadow=true;scene.add(ground);geometrySet.add(groundGeometry);materialSet.add(groundMaterial);
  brandTexture.colorSpace=THREE.SRGBColorSpace;brandTexture.anisotropy=8;textureSet.add(brandTexture);
  function graphic(anchor:string,texture:THREE.Texture,width:number,height:number,rotation:[number,number,number]=[0,0,0]){
    const parent=model.getObjectByName(anchor);if(!parent)return;
    const material=new THREE.MeshStandardMaterial({map:texture,transparent:true,depthWrite:false,roughness:.48});materialSet.add(material);
    const geometry=new THREE.PlaneGeometry(width,height);geometrySet.add(geometry);
    const mesh=new THREE.Mesh(geometry,material);mesh.rotation.set(...rotation);parent.add(mesh);return mesh;
  }
  function label(anchor:string,text:string,width:number,height:number,color:string,rotation:[number,number,number]=[0,0,0],family=`"FondFontModel-${code}"`,weight=650){
    const c=document.createElement('canvas');c.width=1024;c.height=Math.round(1024*height/width);
    const ctx=c.getContext('2d')!;ctx.fillStyle=color;ctx.textAlign='center';ctx.textBaseline='middle';
    const lines=text.split('\n');let size=c.height*.84/lines.length;
    do{ctx.font=`${weight} ${size}px ${family}`;if(lines.every(line=>ctx.measureText(line).width<c.width*.94))break;size-=1;}while(size>8);
    lines.forEach((line,i)=>ctx.fillText(line,c.width/2,c.height/2+(i-(lines.length-1)/2)*size*1.07));
    const texture=new THREE.CanvasTexture(c);texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=8;textureSet.add(texture);
    return graphic(anchor,texture,width,height,rotation);
  }
  const top:[number,number,number]=[-Math.PI/2,0,0],back:[number,number,number]=[0,Math.PI,0];
  const foundrySign=model.getObjectByName('FoundrySign')!,librarySign=model.getObjectByName('WarehouseSign')!;
  label('FoundrySign',copy.foundry,foundrySign.userData.width,foundrySign.userData.height,'#fff0e4');
  const cabLogo=graphic('CabRoofName',brandTexture,1.1,1.1,top);
  if(cabLogo)(cabLogo.material as THREE.MeshStandardMaterial).roughness=1;
  label('FlatbedName',copy.name,1.7,.36,'#352a3e',top);
  label('WarehouseSign',`iOS ${copy.library}`,librarySign.userData.width,librarySign.userData.height,'#fff0e4');
  // Match the localized poster's first frame, including glyph order and typefaces.
  const roofSeed=47;
  const roofGlyphs=createRoofGlyphs(model.getObjectByName('PhoneScreenGlyph')!,code,roofFonts.map(f=>f.family),roofSeed);
  textureSet.add(roofGlyphs.texture);roofGlyphs.materials.forEach(m=>materialSet.add(m));roofGlyphs.geometries.forEach(g=>geometrySet.add(g));
  dustTexture.colorSpace=THREE.SRGBColorSpace;textureSet.add(dustTexture);
  const dustAspect=dustTexture.image.width/dustTexture.image.height;
  const dust=Array.from({length:18},()=>{
    const material=new THREE.SpriteMaterial({map:dustTexture,transparent:true,opacity:0,depthWrite:false,toneMapped:false});
    materialSet.add(material);const sprite=new THREE.Sprite(material);sprite.center.set(.5,.05);scene.add(sprite);return sprite;
  });
  leafTexture.colorSpace=THREE.SRGBColorSpace;textureSet.add(leafTexture);
  const leafGeometry=new THREE.PlaneGeometry(1,1,4,8);
  const leafPositions=leafGeometry.getAttribute('position');
  for(let i=0;i<leafPositions.count;i++)leafPositions.setZ(i,.07*Math.sin((leafPositions.getY(i)+.5)*Math.PI));
  geometrySet.add(leafGeometry);
  const leaves=Array.from({length:6},()=>{
    const material=new THREE.MeshBasicMaterial({map:leafTexture,transparent:true,alphaTest:.02,depthWrite:false,side:THREE.DoubleSide,toneMapped:false});
    materialSet.add(material);const leaf=new THREE.Mesh(leafGeometry,material);scene.add(leaf);return leaf;
  });
  const litter=createLeafLitter(),leafTransform=new THREE.Object3D();
  const litterMaterial=new THREE.MeshBasicMaterial({map:leafTexture,alphaTest:.2,side:THREE.DoubleSide,toneMapped:false});
  materialSet.add(litterMaterial);
  let litterCapacity=64,litterMesh=new THREE.InstancedMesh(leafGeometry,litterMaterial,litterCapacity);
  litterMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);litterMesh.frustumCulled=false;litterMesh.count=0;scene.add(litterMesh);
  const smoke=createChimneySmoke(model.getObjectByName('ChimneySmoke')!.getWorldPosition(new THREE.Vector3()));
  scene.add(smoke.mesh);geometrySet.add(smoke.geometry);materialSet.add(smoke.material);
  const butterflies=[model.getObjectByName('Butterfly')!];
  for(let i=1;i<3;i++){const butterfly=butterflies[0].clone(true);scene.add(butterfly);butterflies.push(butterfly);}
  const smokeBlur=host.querySelector<HTMLElement>('.font-factory__smoke-blur');
  const gardenLife=createGardenLife(host.classList.contains('is-shot')?47:Math.floor(Math.random()*4294967296));
  const target=new THREE.WebGLRenderTarget(1,1,{type:THREE.HalfFloatType,samples:host.clientWidth<600?2:4});
  const alphaSurfaces=[...['PhoneRoof','FoundryArt'].flatMap(name=>model.getObjectByName(name)??[]),roofGlyphs.group,smoke.mesh,...dust,...leaves,litterMesh];
  model.traverse(o=>{if(o.userData.architecture_role==='caster'||o.userData.architecture_role==='occluder')alphaSurfaces.push(o);});
  const composer=new EffectComposer(renderer,target),beauty=new RenderPass(scene,camera),ao=new CampusAOPass(scene,camera,alphaSurfaces),output=new OutputPass();
  // Convert straight color, then restore premultiplied alpha for the page backdrop.
  output.material.fragmentShader=output.material.fragmentShader
    .replace('gl_FragColor = texture2D( tDiffuse, vUv );','gl_FragColor = texture2D( tDiffuse, vUv ); gl_FragColor.rgb /= max(gl_FragColor.a, .00001);')
    .replace('gl_FragColor = sRGBTransferOETF( gl_FragColor );','gl_FragColor = sRGBTransferOETF( gl_FragColor ); gl_FragColor.rgb *= gl_FragColor.a;');
  ao.updateGtaoMaterial({radius:.5,distanceExponent:1.5,thickness:.8,samples:12});ao.blendIntensity=.32;
  composer.addPass(beauty);composer.addPass(ao);composer.addPass(output);
  let disposed=false,renderTime=0;
  let leafSkyLine=10,skyPixels=0,canvasWidth=1,canvasHeight=1;
  function dispose(){if(disposed)return;disposed=true;resize.disconnect();petAnimator.dispose();litterMesh.dispose();host.classList.remove('is-ready');if(smokeBlur)smokeBlur.style.opacity='0';skeletonSet.forEach(s=>s.dispose());geometrySet.forEach(g=>g.dispose());materialSet.forEach(m=>m.dispose());textureSet.forEach(t=>t.dispose());env.dispose();key.shadow.dispose();ao.dispose();beauty.dispose();output.dispose();composer.dispose();renderer.dispose();document.fonts.delete(font);roofFonts.forEach(f=>document.fonts.delete(f));}
  const pageSun=document.querySelector<HTMLElement>('[data-nav-sun]');
  const header=document.querySelector<HTMLElement>('.site-header');
  const sunTarget=POSTER_SUN.clone();
  let previousSun='';
  function syncSun(){
    if(!pageSun)return;
    const sun=pageSun.getBoundingClientRect(),canvas=renderer.domElement.getBoundingClientRect();
    const signature=[sun.left,sun.top,sun.width,sun.height,canvas.left,canvas.top,canvas.width,canvas.height,camera.fov,camera.view?.offsetY].join(',');
    if(signature===previousSun)return;
    previousSun=signature;
    sunTarget.copy(pageSunPosition(camera,canvas,sun));
    key.shadow.camera.far=Math.max(sunTarget.length(),POSTER_SUN.length())+30;
    key.shadow.camera.updateProjectionMatrix();
    if(import.meta.env.DEV){
      const pixel=(point:THREE.Vector3)=>{
        const p=point.project(camera);
        return [canvas.left+(p.x+1)*canvas.width/2,canvas.top+(1-p.y)*canvas.height/2];
      };
      const bearing=sunTarget.clone();bearing.y=0;
      const base=pixel(new THREE.Vector3());
      const tip=pixel(new THREE.Vector3(-sunTarget.x/sunTarget.y,0,-sunTarget.z/sunTarget.y));
      host.dataset.sceneSun=JSON.stringify({world:sunTarget.toArray(),icon:[sun.left+sun.width/2,sun.top+sun.height/2],groundBearing:pixel(bearing),base,shadowPerMeter:[tip[0]-base[0],tip[1]-base[1]],canvas:[canvas.left,canvas.top,canvas.width,canvas.height]});
    }
  }
  function size(){
    const stage=host.querySelector<HTMLElement>('.font-factory__stage')??host;
    const w=stage.clientWidth,h=stage.clientHeight;
    const logo=header?.querySelector('.site-header__product')?.getBoundingClientRect();
    // Keep the sky in document coordinates when the header sticks during scrolling.
    const stageTop=stage.getBoundingClientRect().top+window.scrollY;
    const logoTop=logo?logo.top-header!.getBoundingClientRect().top:stageTop;
    const skyInset=host.classList.contains('is-export')?0:Math.max(0,stageTop-logoTop+24);
    host.style.setProperty('--sky-inset',`${skyInset}px`);
    const totalHeight=h+skyInset;
    skyPixels=skyInset;canvasWidth=w;canvasHeight=totalHeight;
    const shadowSize=host.clientWidth<600?1024:2048;
    if(key.shadow.mapSize.x!==shadowSize){key.shadow.mapSize.set(shadowSize,shadowSize);key.shadow.map?.setSize(shadowSize,shadowSize);}
    renderer.setSize(w,totalHeight,false);composer.setSize(w,totalHeight);ao.setSize(Math.round(w*renderer.getPixelRatio()*.75),Math.round(totalHeight*renderer.getPixelRatio()*.75));
    const contentWidth=host.getBoundingClientRect().width;
    const poster=host.querySelector<HTMLElement>('.font-factory__poster')!;
    const roadWidth=poster.getBoundingClientRect().width*.821875;
    previousSun='';
    fitLens(camera,roadWidth,w,h,skyInset);
    // Leaves spawn on the ray through the pixel just above the logo, at the depth of the campus centre.
    const spawnPixel=logoTop-8-(stageTop-skyInset);
    const spawn=rayToPlane(camera,0,1-2*spawnPixel/totalHeight,new THREE.Plane(new THREE.Vector3(0,0,1),-cameraTarget.z));
    leafSkyLine=Math.cos(Math.atan2(19,29.5))*spawn.y-Math.sin(Math.atan2(19,29.5))*spawn.z;
    syncSun();
    if(import.meta.env.DEV){
      const xs=roadOutline().map(p=>p.clone().project(camera).x);
      host.dataset.sceneFrame=JSON.stringify({width:w,height:h,roadWidth:(Math.max(...xs)-Math.min(...xs))*w/2,contentWidth,centerX:w/2,fov:camera.fov,position:camera.position.toArray()});
    }
  }
  const resize=new ResizeObserver(()=>{size();render(renderTime);});resize.observe(host);resize.observe(host.querySelector('.font-factory__stage')??host);
  if(pageSun)resize.observe(pageSun);
  if(header)resize.observe(header);
  if(signal.aborted){dispose();return null;}
  const truckStudy=import.meta.env.DEV&&new URLSearchParams(location.search).has('truckStudy');
  const truck=model.getObjectByName('Truck')!,cargo=model.getObjectByName('Cargo')!;
  const stacker=createStackerAnimator(model);
  function door(name:string,open:number){
    const o=model.getObjectByName(name);if(!o)return;
    const height=Number(o.userData.height);
    o.scale.y=Math.max(.0001,1-open);o.position.y=height-height*(1-open)/2;
  }
  function render(seconds:number){
    if(disposed)return false;
    renderTime=seconds;
    syncSun();
    const sunlight=Math.max(0,Math.min(1,(seconds-.2)/.6));
    const reveal=sunlight*sunlight*(3-2*sunlight);
    key.position.lerpVectors(POSTER_SUN,sunTarget,reveal);
    const s=sampleMotion(seconds);
    {
      truck.position.set(s.truck.x,0,s.truck.z);truck.rotation.y=s.truck.angle+s.truck.drift;
      cargo.position.set(s.cargo.x,s.cargo.y,s.cargo.z);cargo.rotation.y=s.cargo.angle;
      model.getObjectByName('LoadingSideGate')!.rotation.x=-Math.PI*s.sideGate;
      stacker('Source',s.source);stacker('Receiver',s.receiver);
      door('SourceDoor',s.sourceOpen);door('ReceiverDoor',s.receiverOpen);
      for(const x of [-1.82,-.75,1.62])for(const side of [-1,1]){
        model.getObjectByName(`Wheel_${x}_${side}`)!.rotation.z=-wheelTravel(seconds,x,side*.88)/WHEEL_RADIUS;
        const steer=model.getObjectByName(`Steer_${x}_${side}`)!;
        steer.rotation.y=truckSteering(s.truck,x,side);
      }
    }
    if(truckStudy){
      const offset=new THREE.Vector3(6,4.5,9).applyAxisAngle(new THREE.Vector3(0,1,0),truck.rotation.y);
      cameraTarget.set(s.truck.x,1,s.truck.z);camera.position.copy(cameraTarget).add(offset);camera.lookAt(cameraTarget);camera.zoom=1.4;camera.updateProjectionMatrix();camera.updateMatrixWorld(true);syncSun();
    }
    if(import.meta.env.DEV)host.dataset.sceneTime=seconds.toFixed(3);
    dust.forEach((sprite,i)=>{
      const age=((seconds+i*.064)%1.15+1.15)%1.15,pose=sampleMotion(seconds-age).truck;
      const angle=pose.angle+pose.drift,side=i%2?1:-1;
      sprite.position.set(pose.x-1.82*Math.cos(angle)+side*(.91+age*.28)*Math.sin(angle),.10+age*.12,pose.z+1.82*Math.sin(angle)+side*(.91+age*.28)*Math.cos(angle));
      const width=1.8+age*1.8;sprite.scale.set(width,width/dustAspect,1);
      const opacity=pose.drift/DRIFT_MAX*(1-age/1.15)**2*.6;sprite.visible=opacity>.001;
      (sprite.material as THREE.SpriteMaterial).opacity=opacity;
    });
    windTime.value=seconds;
    const fallen=litter.sample(seconds,leafSkyLine);
    leaves.forEach((leaf,i)=>{
      const p=sampleLeaf(seconds,i,leafSkyLine);leaf.visible=p.opacity*reveal>.005&&!fallen.captured.has(p.id);
      leaf.position.set(p.x,p.y,p.z);leaf.rotation.set(p.pitch,p.yaw,p.roll,'YXZ');
      leaf.scale.set(p.size*leafTexture.image.width/leafTexture.image.height,p.size,1);
      (leaf.material as THREE.MeshBasicMaterial).opacity=p.opacity*.85*reveal;
    });
    if(fallen.leaves.length>litterCapacity){
      const previous=litterMesh;while(litterCapacity<fallen.leaves.length)litterCapacity*=2;
      litterMesh=new THREE.InstancedMesh(leafGeometry,litterMaterial,litterCapacity);
      litterMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);litterMesh.frustumCulled=false;
      scene.add(litterMesh);alphaSurfaces[alphaSurfaces.indexOf(previous)]=litterMesh;previous.removeFromParent();previous.dispose();
    }
    fallen.leaves.forEach((p,i)=>{
      leafTransform.position.set(p.x,p.y,p.z);leafTransform.rotation.set(p.pitch,p.yaw,p.roll,'YXZ');
      leafTransform.scale.set(p.size*leafTexture.image.width/leafTexture.image.height,p.size,1);leafTransform.updateMatrix();
      litterMesh.setMatrixAt(i,leafTransform.matrix);
    });
    litterMesh.count=fallen.leaves.length;litterMesh.instanceMatrix.needsUpdate=true;
    if(import.meta.env.DEV)host.dataset.leafLitter=JSON.stringify({count:fallen.leaves.length,deck:fallen.deckCount,kicks:fallen.kickCount,airborne:fallen.leaves.filter(p=>p.airborne).length});
    // Sky extent varies by viewport; introduce its effects only after the poster handoff.
    smoke.update(seconds,reveal);roofGlyphs.update(seconds);
    const life=gardenLife.sample(seconds);petAnimator.update(life,seconds);
    butterflies.forEach((butterfly,i)=>{
      const p=sampleButterfly(seconds,i);butterfly.position.set(p.x,p.y,p.z);butterfly.rotation.set(0,p.yaw,p.roll);butterfly.scale.setScalar(p.size);
      butterfly.getObjectByName('ButterflyWingL')!.rotation.z=-p.flap;butterfly.getObjectByName('ButterflyWingR')!.rotation.z=p.flap;
    });
    if(smokeBlur){
      const h=2.7,p=smoke.mesh.position.clone().add(new THREE.Vector3(.13*h+.105*h*h+.07*h*Math.sin(h*2.7-seconds*.55),h,0)).project(camera);
      const world=smoke.mesh.position.clone().add(new THREE.Vector3(0,h,0));
      const width=(.08+.15*h)/metresPerPixel(camera,world,canvasHeight)*3.8,height=width*1.45;
      smokeBlur.style.width=`${width}px`;smokeBlur.style.height=`${height}px`;
      smokeBlur.style.transform=`translate(${(p.x+1)*canvasWidth/2-width/2}px,${(1-p.y)*canvasHeight/2-skyPixels-height/2}px)`;
      smokeBlur.style.opacity=String(host.classList.contains('is-export')?0:(.5+.15*Math.sin(seconds*.55))*reveal);
    }
    composer.render();return true;
  }
  try{size();render(0);host.classList.add('is-ready');}catch(error){dispose();throw error;}
  return{render,dispose};
}
