import * as THREE from 'three';
import { loadModel } from './model-loader.ts';
import { createStudioLocomotion } from './studio-pet-locomotion.ts';
import type { sampleGardenLife } from './garden-life.mjs';

type Life = ReturnType<typeof sampleGardenLife>;
export function createCatPair(source:THREE.Object3D) {
  const cat = source.getObjectByName('PetCat')!;
  const charcoal = cat.clone(true); charcoal.name = 'PetCatCharcoal';
  const coatMaterials = new Map<THREE.Material,THREE.Material>();
  charcoal.traverse(object => {
    if (!(object instanceof THREE.Mesh)) return;
    const recolor = (original:THREE.Material) => {
      if (original.name !== 'CalicoCat-original-coat') return original;
      if (coatMaterials.has(original)) return coatMaterials.get(original)!;
      const material = original.clone();
      material.onBeforeCompile = shader => {
        shader.fragmentShader = shader.fragmentShader.replace('#include <map_fragment>', `
          #include <map_fragment>
          float coatLuma = dot(diffuseColor.rgb, vec3(.2126, .7152, .0722));
          diffuseColor.rgb = vec3(.006, .009, .014) + vec3(.065, .075, .09) * pow(coatLuma, .65);
        `);
      };
      material.customProgramCacheKey = () => 'fondfont-calico-charcoal-coat-v1';
      coatMaterials.set(original,material); return material;
    };
    object.material = Array.isArray(object.material) ? object.material.map(recolor) : recolor(object.material);
  });
  const scene = new THREE.Group();
  scene.add(charcoal,cat);
  return { scene, animations: [] as THREE.AnimationClip[] };
}

export async function loadStudioPets(signal?:AbortSignal) {
  const source = await loadModel('/v/fondfont/pets/cat-v2.glb',signal);
  return createCatPair(source.scene);
}

/** Original native rigs retain their evaluated walk, turn and planted-sole poses. */
export function createStudioPetAnimator(model: THREE.Object3D) {
  const pets=['PetCatCharcoal','PetCat'].map(name=>createStudioLocomotion(model.getObjectByName(name)!));
  return {
    update(life:Life,seconds:number){pets.forEach((pet,index)=>pet.update(index?life.cat:life.dog,seconds,index));},
    diagnostics(){return pets.map(pet=>pet.diagnostics());},
    dispose(){},
  };
}
